"""Implement the model service logic."""
import json
from flask import Flask, request
from flasgger import Swagger
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Counter, make_wsgi_app
from model_interface import ModelInterface

app = Flask(__name__)
swagger = Swagger(app)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

# Load the model interface
model_interface = ModelInterface()


predictions = Counter('predictions', 'The number of predictions served by the model.')
validations = Counter('validations',
                      'The number of validations that are correct/incorrect',
                      ['is_correct'])


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
        description: A wrongly formatted request (no form-data or does not contain the "data" key)
    """

    review = request.form.get("data")
    if review is None:
        return "The request should be form data with a key called \"data\".", 400
    predictions.inc()
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
          description: Either True or False to indicate if the prediction was correct or not
          required: True
    produces:
      - application/json
    responses:
      200:
        description: Successful response
      400:
        description: A wrongly formatted request (not form-data or doesn't contain "validation" key)
    """
    validation_request = request.form.get('validation')
    if validation_request is None:
        return "The request should be form data with a key called \"validation\".", 400
    prediction_is_correct: bool = json.loads(validation_request)
    validations.labels(is_correct=prediction_is_correct).inc()
    return "Thank you", 200
