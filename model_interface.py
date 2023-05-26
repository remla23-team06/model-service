"""Define the model interface."""
import re
import pickle as pkl
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


class ModelInterface:
    """Load Bag-of-Words (BoW) dictionary and classifier model."""
    def __init__(self,
                 model_path="models/c1_BoW_Sentiment_Model.pkl",
                 classifier_path="models/c2_Classifier_Sentiment_Model"):
        self.model = pkl.load(open(model_path, "rb"))
        self.classifier = joblib.load(classifier_path)
        nltk.download('stopwords')

    @staticmethod
    def process_input(review: str) -> str:
        """
        Preprocess the review data
        """
        porter = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        equalized_review = re.sub('[^a-zA-Z]', ' ', review).lower().split()
        stemmed_review = " ".join(
            [porter.stem(word) for word in equalized_review if word not in set(all_stopwords)])
        return stemmed_review

    def predict(self, review: str, pre_process=True) -> int:
        """
        Predict the sentiment of a review
        """
        processed_review = self.process_input(review) if pre_process else review
        [transformed_review] = self.model.transform([processed_review]).toarray()
        predictions = self.classifier.predict([transformed_review])
        print(predictions)
        [prediction] = predictions
        return int(prediction)
