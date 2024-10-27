# -*- coding: utf-8 -*-
"""Model2_run_models.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Pi5qCneCgfwG60TWnoPOujVR-NRnO_7N
"""

import re
import joblib
import lime.lime_text
import numpy as np

# Load the saved model and vectorizer
model = joblib.load('naive_bayes_model2.joblib')
vectorizer = joblib.load('count_vectorizer2.joblib')

# Clean review text function
def clean_review(text):
    return re.sub(r'[^A-Za-z\s]', '', text)

# Function to predict and explain reviews
def predict_review(review):
    # Clean and transform the review
    cleaned_review = clean_review(review)
    review_vectorized = vectorizer.transform([cleaned_review])

    # Make the prediction
    prediction = model.predict(review_vectorized)

    return prediction[0]  # Return only the prediction label

def sum_weights(explainer):
    sum = 0
    for _, weight in explainer.as_list():
        if weight > 0.0:
            sum += weight
    return sum

def normalize_weight(weight, sum):
    return (weight / sum) * 100


def format_influential_words(influential_words):
    contributions = ', '.join([f"{word} ({percentage:.2f}%)" for word, percentage in influential_words])
    result_string = f"The review was labeled based on these words, with each percentage indicating its contribution to the decision: {contributions}."
    return result_string

# Function to explain predictions using LIME
def explain_review(review):
    # Predict label
    prediction = predict_review(review)

    # Initialize LIME explainer with correct class names
    explainer = lime.lime_text.LimeTextExplainer(class_names=['OR', 'CG'])  # 0: OR, 1: CG

    # Explain the prediction
    exp = explainer.explain_instance(
        review,  # Original text input for LIME
        lambda x: model.predict_proba(vectorizer.transform(x)),  # Prediction probabilities
        num_features=10  # Number of features to show in the explanation
    )

    influential_words = []
    sum = sum_weights(exp)
    for word, weight in exp.as_list():
        if weight > 0.0:
            normalized_weight = normalize_weight(weight, sum)
            influential_words.append((str(word), normalized_weight))
    influental_words_string = format_influential_words(influential_words)
    return prediction, influental_words_string

# if __name__ == "__main__":
#     new_review = "I loved the service and the staff was very friendly!"
#     prediction, influental_words_string = explain_review(new_review)
#     print(influental_words_string)

