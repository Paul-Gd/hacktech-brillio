import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_model(model_dir, device=None):
    if device is None:
        device = torch.device('cpu')
    
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()
    
    return model, tokenizer


def predict(texts, model, tokenizer, device=None, max_length=512):
    if device is None:
        device = torch.device('cpu')
    
    if isinstance(texts, str):
        texts = [texts]
    
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
        predictions = torch.argmax(logits, dim=1)
    
    label_mapping = {0: 'OR', 1: 'CG'} 
    predicted_labels = [label_mapping[pred.item()] for pred in predictions]
    
    return predicted_labels

### EXAMPLE:

# Specify the directory where your model and tokenizer are saved
model_directory = './saved_model_distilbert/'

# Specify the device (CPU or GPU)
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

# Load the model and tokenizer
model, tokenizer = load_model(model_directory, device=device)

# Example texts to classify
texts_to_classify = [
    "This product is amazing! I love it.",
    "Worst experience ever. Do not buy this.",
    "The service was okay, nothing special.",
    "I would definitely recommend this to my friends.",
    "It's a scam. Totally fake and waste of money."
]

# Generate predictions
predicted_labels = predict(texts_to_classify, model, tokenizer, device=device)

# Print the results
for text, label in zip(texts_to_classify, predicted_labels):
    print(f"Text: {text}\nPredicted Label: {label}\n")