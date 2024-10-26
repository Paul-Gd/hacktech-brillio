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
    
    # Tokenize input text
    inputs = tokenizer(text_instance, return_tensors="pt", truncation=True, max_length=max_length)
    if device:
        model.to(device)
        inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get embeddings with requires_grad=True
    model.eval()
    embeddings = model.get_input_embeddings()(inputs["input_ids"])
    embeddings.retain_grad()  # Keep track of gradients on the embeddings
    
    # Forward pass with embeddings
    outputs = model(inputs_embeds=embeddings)
    logits = outputs.logits

    # Get predicted label and certainty
    proba = torch.nn.functional.softmax(logits, dim=-1)
    predicted_label = proba.argmax().item()
    certainty = float(proba.max().item())

    # Backward pass to compute gradients w.r.t. embeddings
    proba[0, predicted_label].backward()  # Compute gradients for the predicted class
    
    # Interpret gradients to determine influence
    gradients = embeddings.grad[0].cpu().numpy()
    explanation = {}

    for token_id, grad in zip(inputs["input_ids"][0], gradients):
        word = tokenizer.decode([token_id])
        grad_score = np.mean(grad)  # Aggregate gradient scores for each token
        explanation[word] = float(grad_score)  # Positive for supporting, negative for counteracting

    explanation_data = {
        "text": text_instance,
        "predicted_label": bool(predicted_label),
        "certainty": certainty,
        "explanation": explanation  # Combined positive and negative influences
    }

    return explanation_data

