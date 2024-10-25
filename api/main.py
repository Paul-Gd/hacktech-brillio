# main.py
from fastapi import FastAPI
from review_predictor import review_prediction_router
app = FastAPI()

@app.get("/")
def hello():
    return {"message":"Hello!"}

app.include_router(review_prediction_router)