import joblib
import sklearn

# Load the model
model = joblib.load('naive_bayes_model.joblib')

# Load the vectorizer
vectorizer = joblib.load('count_vectorizer.joblib')

print("Model and vectorizer loaded successfully!")

# Function to clean and predict new reviews
def clean_review(text):
    import re
    return re.sub(r'[^A-Za-z\s]', '', text)

def predict_review(review):
    cleaned_review = clean_review(review)
    review_vectorized = vectorizer.transform([cleaned_review])
    prediction = model.predict(review_vectorized)
    return prediction[0]

# Example of predicting a new review
new_review = "Food was quick and hot, area was nicely clean aswell"
predicted_label = predict_review(new_review)
print(f"Review: '{new_review}' is classified as: {predicted_label} (1 for CG, 0 for OR)")