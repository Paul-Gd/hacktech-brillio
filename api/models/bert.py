import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from lime.lime_text import LimeTextExplainer
import numpy as np

def load_model(model_dir, device=None):
    if device is None:
        device = torch.device('mps')
    
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()
    
    return model, tokenizer


def predict_proba(texts, model, tokenizer, device=None, max_length=512):
    if device is None:
        device = torch.device('mps')
    
    if isinstance(texts, str):
        texts = [texts]
    
    # Tokenize the input texts
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors='pt'
    )
    inputs = {key: val.to(device) for key, val in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        certainties = torch.softmax(logits, dim=1)

    return certainties.cpu().numpy()  # Convert to NumPy format required by LIME

def prediction(text_instance, model, tokenizer, device=None, max_length=512, num_features=10):
    if device is None:
        device = torch.device('mps')
    
    # Initialize the LIME text explainer
    explainer = LimeTextExplainer(class_names=["False", "True"])

    # def lime_predict(texts):
    #     return predict_proba(texts, model, tokenizer, device, max_length)

    # Generate explanation for the provided text instance
    # exp = explainer.explain_instance(
    #     text_instance,
    #     lime_predict,
    #     num_features=num_features,  # Number of features to explain
    #     labels=[1]  # Labels to explain (e.g., label 1 corresponds to True)
    # )
    
    proba = predict_proba([text_instance], model, tokenizer, device, max_length)
    predicted_label = bool(np.argmax(proba))  # Convert prediction to a boolean
    certainty = float(np.max(proba))  # Extract the highest probability value as certainty

    # explanation_key_value = {word: score for word, score in exp.as_list(label=1)}

    explanation_data = {
        "text": text_instance,
        "predicted_label": predicted_label,
        "certainty": certainty,
        # "explanation": explanation_key_value  # Explanation as a dictionary
    }

    explanation_json = explanation_data

    return explanation_json
