"""Define the model interface."""
import pickle as pkl
import joblib
from sklearn.pipeline import Pipeline
from remlaverlib import Preprocessor


class ModelInterface:
    """Load Bag-of-Words (BoW) dictionary and classifier model."""

    def __init__(self,
                 model_path="C:\Courses\REMLA T06\model-service\models\c1_BoW_Sentiment_Model.pkl",
                 classifier_path="C:\Courses\REMLA T06\model-service\models\c2_Classifier_Sentiment_Model"):
        with open(model_path, "rb") as model:
            self.model: Pipeline = pkl.load(model)
        self.classifier = joblib.load(classifier_path)
        self.preprocessor = Preprocessor()

    def predict(self, review: str, pre_process=True) -> int:
        """
        Predict the sentiment of a review
        """
        processed_review = self.preprocessor.process_input(review) if pre_process else review
        [transformed_review] = self.model.transform([processed_review]).toarray()
        predictions = self.classifier.predict([transformed_review])
        [prediction] = predictions
        return int(prediction)
