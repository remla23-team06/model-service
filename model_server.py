import json
from flask import Flask, request
from model_interface import ModelInterface
from flasgger import Swagger
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Counter, Gauge, make_wsgi_app

app = Flask(__name__)
swagger = Swagger(app)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

# Load the model interface
model_interface = ModelInterface()


predictions = Counter('predictions', 'The number of predictions served by the model.')
validations = Counter('validations', 'The number of validations that are correct/incorrect', ['is_correct'])
validation_prediction_ratio = Gauge('validation_to_prediction_ratio', "The ratio of validations to predictions")

def update_validation_prediction_ratio():
  validation_prediction_ratio.set(0 if predictions._value.get() == 0 or not hasattr(predictions, '_value') or not hasattr(validations, '_value') else validations._value.get() / predictions._value.get() * 100)






@app.route('/predict', methods=['POST'])
def predict():
    """
    Obtain predictions from the sentiment analysis model.
    On submitting a user review on this route, the sentiment of this review is predicted.
    Predictions can either be 0 (negative sentiment) or 1 (positive sentiment).
    ---
    consumes:
      - multipart/form-data
    parameters:
        - name: data
          in: form-data
          description: review to be classified
          required: True
    produces:
      - application/json
    responses:
      200:
        description: Successful response
      400:
        description: A wrongly formatted request that is not form-data or does not contain the "data" key
    """

    review = request.form.get("data")
    if review is None:
        return "The request should be form data with a key called \"data\".", 400
    predictions.inc()
    update_validation_prediction_ratio()

    print("I received input data for the model: ", review)

    # 1. Preprocess the input data
    preprocessed_data = model_interface.process_input(review)

    # 2. Pass the preprocessed data through the model
    prediction = model_interface.predict(preprocessed_data, pre_process=False)

    return {'sentiment': prediction}, 200


@app.route("/validate", methods=['POST'])
def validate():
    """
    Save the validations provided by users to evaluate the performance of the model.
    ---
    consumes:
      - multipart/form-data
    parameters:
        - name: validation
          in: form-data
          description: a validation that is either True or False to indicate if the prediction was correct or incorrect respectively.
          required: True
    produces:
      - application/json
    responses:
      200:
        description: Successful response
      400:
        description: A wrongly formatted request that is not form-data or does not contain the "validation" key
    """ 
    validation_request = request.form.get('validation')
    if validation_request is None:
         return "The request should be form data with a key called \"validation\".", 400
    prediction_is_correct: bool = json.loads(validation_request)
    validations.labels(is_correct=prediction_is_correct).inc()
    update_validation_prediction_ratio()
    return "Thank you", 200
