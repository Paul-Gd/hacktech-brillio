import joblib

# Load the model
model = joblib.load('naive_bayes_model.joblib')

# Load the vectorizer
vectorizer = joblib.load('count_vectorizer.joblib')

print("Model and vectorizer loaded successfully!")


# Function to clean and predict new reviews
def clean_review(text):
    import re
    return re.sub(r'[^A-Za-z\s]', '', text)


# gpt 04 mini cheaper but still good
# use gpt to extract data from page
# then we can use gpt4 if it's not good enough

def predict_review_is_cg(review: str) -> bool:
    cleaned_review = clean_review(review)
    review_vectorized = vectorizer.transform([cleaned_review])
    prediction = model.predict(review_vectorized)
    return prediction[0] == 1
