import json
from flask import Flask, request
from model_interface import ModelInterface
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
prom_metrics = PrometheusMetrics(app)
swagger = Swagger(app)

# Load the model interface
model_interface = ModelInterface()

validations_counter = prom_metrics.counter(
    'validations', 'The number of validations.',
    labels={
        'correct': lambda: json.loads(request.form['validation'])
    }
)

predictions_counter = prom_metrics.counter(
    'predictions', 'The number of predictions.', labels={'count': 1}
)





@app.route('/predict', methods=['POST'])
@prom_metrics.do_not_track()
@predictions_counter
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

    print("I received input data for the model: ", review)

    # 1. Preprocess the input data
    preprocessed_data = model_interface.process_input(review)

    # 2. Pass the preprocessed data through the model
    prediction = model_interface.predict(preprocessed_data, pre_process=False)

    return {'sentiment': prediction}, 200


@app.route("/validate", methods=['POST'])
@prom_metrics.do_not_track()
@validations_counter
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
        description: A wrongly formatted request that is not form-data or does not contain the "data" key
    """ 
        
    return "Thank you", 200
