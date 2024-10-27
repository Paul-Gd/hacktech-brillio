import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from collections import defaultdict

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
    positive_influence = defaultdict(float)  # Using defaultdict to accumulate scores for each word

    current_word = ""
    current_score = 0.0
    for token_id, grad in zip(inputs["input_ids"][0], gradients):
        word_part = tokenizer.decode([token_id]).strip()
        grad_score = np.mean(grad)

        if grad_score > 0:  # Only consider positive influences
            if word_part.startswith("##"):
                current_word += word_part[2:]  # Append to current word, removing "##"
                current_score += grad_score    # Accumulate the score for the combined word
            else:
                # Store the previous word if it's complete
                if current_word:
                    positive_influence[current_word] += current_score
                # Start a new word
                current_word = word_part
                current_score = grad_score

    # Add the last word if there's one remaining after the loop
    if current_word:
        positive_influence[current_word] += current_score

    # Calculate total positive influence and contribution percentages
    total_positive = sum(positive_influence.values())
    contribution_percentages = {
        word: (score / total_positive) * 100 for word, score in positive_influence.items()
    }
    
    summary = "The review was labeled based on these words, with each percentage indicating its contribution to the decision: <br />" + "<br />".join(f"{word} ({percentage:.0f}%)" for word, percentage in contribution_percentages.items())

    explanation_data = {
        "text": text_instance,
        "predicted_label": bool(predicted_label),
        "certainty": certainty,
        "explanation": summary  # Summarized positive influences with contribution percentages
    }

    return explanation_data
