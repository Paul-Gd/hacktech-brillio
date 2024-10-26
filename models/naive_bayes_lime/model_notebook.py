# -*- coding: utf-8 -*-
"""Model2-notebook.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1P5YqnD-N6PhuISFF-LqW2OlMG-gm5Vyh
"""

import pandas as pd
import re
import joblib  # Use joblib for saving
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Load dataset
train_df = pd.read_csv('./train-dataset_clean.csv')

# Drop id column
train_df = train_df.drop(['id'], axis=1)

# Map labels to integers
train_df['label'] = train_df['label'].map({'CG': 1, 'OR': 0}).astype(int)

# Clean review text
def clean_review(text):
    return re.sub(r'[^A-Za-z\s]', '', text)

train_df['review'] = train_df['review'].apply(clean_review)

# Split data into features and labels
X = train_df["review"]
Y = train_df["label"]

# Vectorize the text data
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(X)

# Split into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, Y, test_size=0.3, random_state=42)

# Train Naive Bayes model
model = MultinomialNB()
model.fit(X_train, y_train)

# Validate the model
y_pred = model.predict(X_val)
print("Accuracy:", accuracy_score(y_val, y_pred))

import joblib  # You can also use import pickle

# Save the model
joblib.dump(model, 'naive_bayes_model2.joblib')

# Save the vectorizer
joblib.dump(vectorizer, 'count_vectorizer2.joblib')