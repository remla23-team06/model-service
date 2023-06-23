import json
from flask import Flask, request
from flasgger import Swagger
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Counter, make_wsgi_app, Histogram, Gauge
from model_interface import ModelInterface
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
swagger = Swagger(app)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

# Load the model interface
model_interface = ModelInterface()

predictions = Counter("predictions",
                      "The number of predictions served by the model.",
                      ["sender"])

validations = Counter("validations",
                      "The number of validations that are correct/incorrect",
                      ["is_correct", "sender"])

# Accuracy for predictions
# Define a Prometheus histogram for the review ratings
review_rating_histogram = Histogram(
    'review_rating',
    'Distribution of review ratings',
    buckets=[1, 2, 3, 4, 5],
    labelnames=['rating']
)

# Define a gauge to track the accuracy rate of rating predictions
accuracy_gauge = Gauge(
    'review_prediction_accuracy',
    'Accuracy rate of rating predictions'
)

# Define a histogram that stores the total number of requests, correct reviews, and incorrect reviews
# bucket 1 - correct reviews
# bucket 2 - incorrect reviews
# bucket 3 - total number of reviews
review_accuracy_histogram = Histogram(
    'review_correctness_distribution',
    'Distribution of review ratings by correctness',
    labelnames=['result']
)


def process_review(review):
    """
    Process the review and update the appropriate metrics.

    Args:
        review (dict): The review data containing 'user_predict' and 'predicted' keys.
    """
    assessed_rating = asses_rating(review['user_predict']).upper()
    actual_rating = review['predicted'].upper()

    review_rating_histogram.observe(review['user_predict'])

    if assessed_rating == actual_rating:
        review_accuracy_histogram.labels(result='Correct_Reviews').observe(1)
    elif assessed_rating != 'NEUTRAL':
        review_accuracy_histogram.labels(result='Incorrect_Reviews').observe(1)
    else:
        review_accuracy_histogram.labels(result='Inconclusive_Reviews').observe(1)

    review_accuracy_histogram.labels(result='Total_Reviews').observe(1)


def asses_rating(review):
    """
    Assess the rating based on the review value.

    Args:
        review (int): The review rating value.

    Returns:
        str: The assessed rating ('NEUTRAL', 'POSITIVE', or 'NEGATIVE').
    """
    return 'NEUTRAL' if review == 3 else 'POSITIVE' if review > 3 else 'NEGATIVE'


@app.route('/predict', methods=['POST'])
def predict():
    """
    Obtain predictions from the sentiment analysis model.

    On submitting a user review on this route, the sentiment of this review is predicted.
    Predictions can either be 0 (negative sentiment) or 1 (positive sentiment).

    Returns:
        dict: The prediction result containing the 'sentiment' key.
    """
    review = request.form.get("data")
    sender = request.form.get("sender")
    if review is None:
        return "The request should be form data with a key called \"data\".", 400
    predictions.labels(sender=sender).inc()
    print("I received input data for the model: ", review)

    # 1. Preprocess the input data
    preprocessed_data = model_interface.preprocessor.process_input(review)

    # 2. Pass the preprocessed data through the model
    prediction = model_interface.predict(preprocessed_data, pre_process=False)

    return {'sentiment': prediction}, 200


@app.route("/validate", methods=["POST"])
def validate():
    """
    Save the validations provided by users to evaluate the performance of the model.

    Returns:
        str: A response indicating the successful validation save.
    """

    # Compute the required values
    bucket_values = review_accuracy_histogram.collect()
    correct_reviews = next((value for value in bucket_values if value.labels.get('result') == 'Correct_Reviews'), None)
    total_reviews = next((value for value in bucket_values if value.labels.get('result') == 'Total_Reviews'), None)
    print("REACHED")

    try:
        accuracy_gauge.set(correct_reviews.sum / total_reviews.sum)
    except (AttributeError, ZeroDivisionError):
        # In case there is no correct review or no reviews at all
        accuracy_gauge.set(0)

    validation_request = request.form.get("validation")
    sender = request.form.get("sender")
    if validation_request is None:
        return "The request should be form data with a key called \"validation\".", 400
    prediction_is_correct: bool = json.loads(validation_request)
    validations.labels(is_correct=prediction_is_correct, sender=sender).inc()
    return "Thank you", 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
