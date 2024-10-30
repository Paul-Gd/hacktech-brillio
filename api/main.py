from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app_startup import lifespan
from review_predictor import review_prediction_router

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(review_prediction_router)

@app.get("/")
def hello():
    return RedirectResponse(url="https://github.com/Paul-Gd/hacktech-brillio")
