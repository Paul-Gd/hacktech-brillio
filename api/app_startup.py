from contextlib import asynccontextmanager
from typing import Optional

import torch
from fastapi import FastAPI

from models.bert import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = "ArpadAuner/hacktech"
    print("Loading BERT model and tokenizer...")
    bert_model, bert_tokenizer = load_model(model_dir, device=torch.device('cpu'))
    print("BERT model and tokenizer loaded successfully.")

    # Store the model and tokenizer in the app's state
    app.state.bert_model = bert_model
    app.state.bert_tokenizer = bert_tokenizer

    yield  # Start the application

    # Cleanup after the application stops
    print("Cleaning up resources...")
    app.state.bert_model = None
    app.state.bert_tokenizer = None
