import re
import numpy as np
import pandas as pd
import nltk
import pickle
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer

def clean_review(review,ps,all_stopwords):
    review = re.sub('[^a-zA-Z]', ' ', review)
    review = review.lower()
    review = review.split()
    review = [ps.stem(word) for word in review if not word in set(all_stopwords)]
    review = ' '.join(review)
    return review

def preprocess_input(input_data):

    nltk.download('stopwords')

    ps = PorterStemmer()
    all_stopwords = stopwords.words('english')
    all_stopwords.remove('not')

    cvFile = 'models/c1_BoW_Sentiment_Model.pkl'
    cv = pickle.load(open(cvFile, "rb"))

    cleaned_review = clean_review(input_data,ps,all_stopwords)
    transformed_input = cv.transform([cleaned_review]).toarray()
    return transformed_input
