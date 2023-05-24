import json
from flask import Flask, request
from model_interface import ModelInterface
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Load the model interface
model_interface = ModelInterface()

ALL_PREDICTIONS = 0
CORRECT_PREDICTIONS = 0
INCORRECT_PREDICTIONS = 0
VALIDATIONS = 0



@app.route('/predict', methods=['POST'])
def predict():
    global ALL_PREDICTIONS
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
    
    ALL_PREDICTIONS += 1

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
        description: A wrongly formatted request that is not form-data or does not contain the "data" key
    """
    global CORRECT_PREDICTIONS, INCORRECT_PREDICTIONS, VALIDATIONS
    prediction_was_correct: bool = json.loads(request.form['validation'])

    # Do something with the result of the validation of the prediction
    VALIDATIONS += 1
    if prediction_was_correct:
        CORRECT_PREDICTIONS += 1
    else:
        INCORRECT_PREDICTIONS += 1
        
    return "Thank you", 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Send metrics for monitoring to Prometheus."""
    global ALL_PREDICTIONS, CORRECT_PREDICTIONS, INCORRECT_PREDICTIONS # pylint: disable=W0602

    m = "# HELP predictions The number of predictions.\n" # pylint: disable=C0103
    m += "# TYPE predictions counter\n" # pylint: disable=C0103
    m += "predictions{{correct=\"None\"}} {}\n".format(ALL_PREDICTIONS) # pylint: disable={C0103, C0209}
    m += "predictions{{correct=\"True\"}} {}\n".format(CORRECT_PREDICTIONS) # pylint: disable={C0103, C0209}
    m += "predictions{{correct=\"False\"}} {}\n".format(INCORRECT_PREDICTIONS) # pylint: disable={C0103, C0209}

    return m, 200
