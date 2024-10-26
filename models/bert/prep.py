import os
import torch
from transformers import AutoTokenizer
import pandas as pd  # Use pandas for CSV loading

# Device configuration
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

# Load the CSV data from the file
dataset_path = './train-dataset1.csv'
data = pd.read_csv(dataset_path)

# Map string labels to integers
label_mapping = {'CG': 1, 'OR': 0}
data['label'] = data['label'].map(label_mapping)

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Define the maximum sequence length (BERT supports up to 512 tokens)
max_seq_length = 512

input_ids = []
attention_masks = []
labels = []

for i, row in data.iterrows():
    text = row['review']  # Assuming the column with text is named 'review'
    label = row['label']  # Now an integer (0 or 1) after mapping

    # Tokenize the text
    tokenized = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_seq_length,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    )
    
    input_ids.append(tokenized['input_ids'])
    attention_masks.append(tokenized['attention_mask'])
    labels.append(label)  # Label is already an integer
    print(f"Processed {i+1}/{len(data)} samples.")

# Convert lists to tensors
input_ids = torch.cat(input_ids, dim=0)
attention_masks = torch.cat(attention_masks, dim=0)
labels = torch.tensor(labels, dtype=torch.long)

# Save the tensors for later use (optional)
save_dir = os.path.join('..', 'datasets')
os.makedirs(save_dir, exist_ok=True)

torch.save(input_ids, os.path.join(save_dir, 'input_ids.pt'))
torch.save(attention_masks, os.path.join(save_dir, 'attention_masks.pt'))
torch.save(labels, os.path.join(save_dir, 'labels.pt'))