import json

from flask import Flask, request
from preprocess import preprocess_input
import joblib

app = Flask(__name__)

# Load the model
model_path = "models/c2_Classifier_Sentiment_Model"
model = joblib.load(model_path)


@app.route('/predict', methods=['POST'])
def predict():
    """Get predictions from the model."""

    input_data = request.form["data"]

    print("I received input data for the model: ", input_data)

    # 1. Preprocess the input data
    preprocessed_data = preprocess_input(input_data)

    # 2. Pass the preprocessed data through the model
    predictions = model.predict(preprocessed_data)

    # 3. Get predictions
    prediction = predictions[0]

    return {'sentiment': int(prediction)}, 200


@app.route("/validate", methods=['POST'])
def validate():
    prediction_was_correct: bool = json.loads(request.form['validation'])

    # Do something with the result of the validation of the prediction

    return 200
