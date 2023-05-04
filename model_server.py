"""Serves the model through a REST API."""

from flask import Flask, request

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    """Get predictions from the model."""

    input_data = request.form["data"]

    print("I received input data for the model: ", input_data)

    # 1. <preprocess the input data>
    # 2. <pass the preprocessed data through the model>
    # 3. <get predictions>

    return "<this response text will be filled with predictions>", 200


if __name__ == '__main__':
    app.run(host="localhost", port=8080)
