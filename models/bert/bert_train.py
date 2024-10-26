import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, TensorDataset, random_split
from sklearn.metrics import classification_report

# Device configuration
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

# Load the saved tensors
input_ids = torch.load(os.path.join('.', 'datasets', 'input_ids.pt'))
attention_masks = torch.load(os.path.join('.', 'datasets', 'attention_masks.pt'))
labels = torch.load(os.path.join('.', 'datasets', 'labels.pt'))

# Create a TensorDataset
dataset = TensorDataset(input_ids, attention_masks, labels)

# Split the dataset into training and validation sets
train_percentage = 0.8
total_size = len(dataset)
train_size = int(train_percentage * total_size)
val_size = total_size - train_size

# Set seed for reproducibility
seed = 42
torch.manual_seed(seed)

train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

# Define batch size
batch_size = 32  # Adjust based on your system's memory

# Create DataLoaders
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Load the pre-trained DistilBERT model for sequence classification
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2  # Binary classification
).to(device)

# Set up the optimizer and learning rate scheduler
optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
epochs = 1  # Training for 1 epoch as per your request
total_steps = len(train_loader) * epochs

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)

# Training loop
train_losses = []
train_accuracies = []
val_losses = []
val_accuracies = []

for epoch in range(epochs):
    # Training phase
    model.train()
    total_loss = 0.0
    correct_predictions = 0
    total_predictions = 0

    batch_counter = 0
    epoch_start_time = time.time()

    for batch_idx, batch in enumerate(train_loader):
        batch_start_time = time.time()

        input_ids_batch, attention_mask_batch, labels_batch = batch
        input_ids_batch = input_ids_batch.to(device)
        attention_mask_batch = attention_mask_batch.to(device)
        labels_batch = labels_batch.to(device)

        optimizer.zero_grad()
        outputs = model(
            input_ids=input_ids_batch,
            attention_mask=attention_mask_batch,
            labels=labels_batch
        )
        loss = outputs.loss
        logits = outputs.logits

        loss.backward()
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()

        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        correct_predictions += (preds == labels_batch).sum().item()
        total_predictions += labels_batch.size(0)

        batch_counter += 1

        # Every 100 batches, print progress
        if (batch_idx + 1) % 100 == 0:
            batch_time = time.time() - batch_start_time
            avg_loss = total_loss / batch_counter
            avg_accuracy = correct_predictions / total_predictions
            print(f"Epoch [{epoch+1}/{epochs}], Step [{batch_idx+1}/{len(train_loader)}], "
                  f"Loss: {loss.item():.4f}, Avg Loss: {avg_loss:.4f}, "
                  f"Avg Accuracy: {avg_accuracy*100:.2f}%, Time per batch: {batch_time:.2f}s")

    avg_train_loss = total_loss / len(train_loader)
    train_accuracy = correct_predictions / total_predictions

    epoch_time = time.time() - epoch_start_time

    # Validation phase
    model.eval()
    val_loss = 0.0
    val_correct_predictions = 0
    val_total_predictions = 0

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in val_loader:
            input_ids_batch, attention_mask_batch, labels_batch = batch
            input_ids_batch = input_ids_batch.to(device)
            attention_mask_batch = attention_mask_batch.to(device)
            labels_batch = labels_batch.to(device)

            outputs = model(
                input_ids=input_ids_batch,
                attention_mask=attention_mask_batch,
                labels=labels_batch
            )
            loss = outputs.loss
            logits = outputs.logits

            val_loss += loss.item()

            preds = torch.argmax(logits, dim=1)
            val_correct_predictions += (preds == labels_batch).sum().item()
            val_total_predictions += labels_batch.size(0)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels_batch.cpu().numpy())

    avg_val_loss = val_loss / len(val_loader)
    val_accuracy = val_correct_predictions / val_total_predictions

    train_losses.append(avg_train_loss)
    train_accuracies.append(train_accuracy)
    val_losses.append(avg_val_loss)
    val_accuracies.append(val_accuracy)

    print(f"Epoch {epoch+1}/{epochs} completed in {epoch_time:.2f}s")
    print(f"Training Loss: {avg_train_loss:.4f}, Training Accuracy: {train_accuracy*100:.2f}%")
    print(f"Validation Loss: {avg_val_loss:.4f}, Validation Accuracy: {val_accuracy*100:.2f}%")
    print("-" * 50)

    # Save checkpoint after each epoch
    checkpoint_dir = f'./checkpoint_epoch_{epoch+1}/'
    os.makedirs(checkpoint_dir, exist_ok=True)
    model.save_pretrained(checkpoint_dir)
    tokenizer.save_pretrained(checkpoint_dir)
    print(f"Checkpoint saved to {checkpoint_dir}")

# Classification report on validation set
print("Validation Set Performance:")
print(classification_report(all_labels, all_preds, digits=4))

# Save the final trained model
output_dir = './saved_model_distilbert/'
os.makedirs(output_dir, exist_ok=True)
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"Model saved to {output_dir}")

def bert_predict_proba(texts):
    # Tokenize the texts
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )
    # Move inputs to the device
    inputs = {key: val.to(device) for key, val in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
    return probs.cpu().numpy()

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

model.eval()
true_labels = []
predicted_labels = []

with torch.no_grad():
    for batch in val_loader:
        input_ids, attention_mask, labels = batch
        input_ids = input_ids.to(device)
        attention_mask = attention_mask.to(device)
        labels = labels.to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1)

        true_labels.extend(labels.cpu().numpy())
        predicted_labels.extend(preds.cpu().numpy())
        
import matplotlib.pyplot as plt

class_names = ['OR', 'CG']  # Map 0 to 'OR', 1 to 'CG'
cm = confusion_matrix(true_labels, predicted_labels)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(cmap='Blues')
plt.title('Confusion Matrix')
plt.show()
