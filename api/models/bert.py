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

def prediction(text_instances, model, tokenizer, device=None, max_length=512, num_features=10):
    if device is None:
        device = torch.device('mps')
    
    # Ensure input is a list of text instances
    if not isinstance(text_instances, list):
        text_instances = [text_instances]
    
    # Tokenize input texts as a batch
    inputs = tokenizer(text_instances, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
    if device:
        model.to(device)
        inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get embeddings with requires_grad=True
    model.eval()
    embeddings = model.get_input_embeddings()(inputs["input_ids"])
    embeddings.retain_grad()  # Keep track of gradients on the embeddings
    
    # Forward pass with embeddings
    outputs = model(inputs_embeds=embeddings, output_attentions=True)
    logits = outputs.logits

    # Initialize results list
    results = []

    for i in range(len(text_instances)):
        # Get prediction probability and label for each review in the batch
        proba = torch.nn.functional.softmax(logits[i], dim=-1)
        predicted_label = proba.argmax().item()
        certainty = float(proba.max().item())
        
        # Backward pass to compute gradients w.r.t. embeddings for each instance
        proba[predicted_label].backward(retain_graph=True)
        
        # Interpret gradients to determine influence
        gradients = embeddings.grad[i].cpu().numpy()
        positive_influence = defaultdict(float)
        current_word = ""
        current_score = 0.0

        for token_id, grad in zip(inputs["input_ids"][i], gradients):
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
        
        # Format the explanation summary
        summary = "The review was labeled based on these words, with each percentage indicating its contribution to the decision: <br />" + "<br />".join(f"{word} ({percentage:.0f}%)" for word, percentage in contribution_percentages.items())

        # Append each review's results to the results list
        results.append({
            "text": text_instances[i],
            "predicted_label": bool(predicted_label),
            "certainty": certainty,
            "explanation": summary
        })
    model.zero_grad()  # Clear gradients for the model
    embeddings.grad = None  # Remove gradient history from embeddings

    return results
