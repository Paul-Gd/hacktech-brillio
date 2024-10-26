
import joblib
import lime.lime_text

# Load the model relative to the api directory
model = joblib.load('../models/naive_bayes_lime/naive_bayes_model2.joblib')

# Load the vectorizer
vectorizer = joblib.load('../models/naive_bayes_lime/count_vectorizer2.joblib')
# Clean review text function
def clean_review(text):
    import re
    return re.sub(r'[^A-Za-z\s]', '', text)

# Function to predict and explain reviews
def predict_review(review):
    # Clean and transform the review
    cleaned_review = clean_review(review)
    review_vectorized = vectorizer.transform([cleaned_review])

    # Make the prediction
    prediction = model.predict(review_vectorized)

    return prediction[0]  # Return only the prediction label

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

    # Print the words that influenced the prediction
    print("\nInfluential Words:")
    influential_words = []
    for word, weight in exp.as_list():
        if weight > 0.0:
            influential_words.append(f'{word}, {weight}')

    #print(f"\nPredicted Label: {'CG' if prediction == 1 else 'OR'}")
    return prediction, "\n".join(influential_words)