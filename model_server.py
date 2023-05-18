import json
from flask import Flask, request
from model_interface import ModelInterface
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Load the model interface
model_interface = ModelInterface()


@app.route('/predict', methods=['POST'])
def predict():
    """
    Obtain predictions from the sentiment analysis model.
    On submitting a user review on this route, the sentiment of this review is predicted.
    Predictions can either be 0 (negative sentiment) or 1 (positive sentiment).
    ---
    consumes:
      - application/json
    parameters:
        - name: data
          in: form-data
          description: review to be classified
          required: True
          schema:
            type: object
            required: review
            properties:
                review:
                    type: string
                    example: This is a bad/good review.
    produces:
      - application/json
    responses:
      200:
        description: Successful response
    """

    review = request.form["data"]

    print("I received input data for the model: ", review)

    # 1. Preprocess the input data
    preprocessed_data = model_interface.process_input(review)

    # 2. Pass the preprocessed data through the model
    prediction = model_interface.predict(preprocessed_data, pre_process=False)

    return {'sentiment': prediction}, 200


@app.route("/validate", methods=['POST'])
def validate():
    prediction_was_correct: bool = json.loads(request.form['validation'])

    # Do something with the result of the validation of the prediction

    return "Thank you", 200
