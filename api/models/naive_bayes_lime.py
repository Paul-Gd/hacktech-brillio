
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

def sum_weights(explainer):
    sum = 0
    for _, weight in explainer.as_list():
        if weight > 0.0:
            sum += weight
    return sum

def normalize_weight(weight, sum):
    return (weight / sum) * 100

def format_influential_words(influential_words):
    contributions = '<br>'.join([f"<br>{word} ({percentage:.2f}%)<br>" for word, percentage in influential_words])
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

    # Print the words that influenced the prediction
    influential_words = []
    sum = sum_weights(exp)
    for word, weight in exp.as_list():
        if weight > 0.0:
            normalized_weight = normalize_weight(weight, sum)
            influential_words.append((str(word), normalized_weight))
    influental_words_string = format_influential_words(influential_words)

    return prediction, influental_words_string