# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {"message":"Hello!"}

@app.post("/predict_data/")
def predict_data():
    return {"message":"Hello!"}