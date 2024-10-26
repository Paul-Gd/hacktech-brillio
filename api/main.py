from contextlib import asynccontextmanager
from fastapi import FastAPI
from review_predictor import review_prediction_router
from models.bert import load_model
import torch

# Define lifespan event to handle model loading and unloading
@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = "ArpadAuner/hacktech"
    print("Loading BERT model and tokenizer...")
    bert_model, bert_tokenizer = load_model(model_dir, device=torch.device('cpu'))
    print("BERT model and tokenizer loaded successfully.")

    # Store the model and tokenizer in the app's state
    app.state.bert_model = bert_model
    app.state.bert_tokenizer = bert_tokenizer

    yield

    print("Cleaning up resources...")
    app.state.bert_model = None
    app.state.bert_tokenizer = None

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(review_prediction_router)

@app.get("/")
def hello():
    return {"message": "Hello!"}
