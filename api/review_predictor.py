from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.model_types import PredictionModels
from fastapi.responses import JSONResponse
import json

review_prediction_router = APIRouter()


class ProductReview(BaseModel):
    text: str = Field(title="The review text")
    review_value: int | None = Field(default=None, title="The review value")


class ProductReviewRequest(BaseModel):
    description: str | None = Field(default=None, title="The description of the item")
    specs: dict[str, str] = Field(default={}, title="The product specifications from page")
    user_reviews: list[ProductReview] = Field(title="The reviews of the product")
    prediction_model: PredictionModels = Field(title="The model to use for prediction",
                                               default=PredictionModels.NAIVE_BAYES)
    page_url: str | None = Field(default=None, title="The URL of the product page")


class AggregatedReviewResults(BaseModel):
    adjusted_review_score: float | None = Field(default=None, title="The adjusted score based on the excluded reviews")
    feedback_from_model: str | None = Field(default=None, title="Additional feedback returned by the model")


class IndividualReviewResult(BaseModel):
    is_computer_generated: bool = Field(title="Whether the review is computer generated or not")
    feedback_from_model: str | dict | None = Field(default=None,
                                                   title="Additional feedback returned by the model")
    certainty: float | None = Field(default=None,
                                    title="The certainty of the model in the prediction between 0 and 1. 1 is highest certainty")


class ReviewPredictionResponse(BaseModel):
    reviews: list[IndividualReviewResult] = Field(title="The reviews of the product")
    aggregated_review_data: AggregatedReviewResults | None = Field(default=None,
                                                                   title="The aggregated review of the product")


@review_prediction_router.post("/review_prediction/")
def review_prediction(review_req: ProductReviewRequest) -> ReviewPredictionResponse:
    if review_req.prediction_model == PredictionModels.NAIVE_BAYES:
        from models.naive_bayes_lime import explain_review
        computed_reviews_by_model = []
        for review in review_req.user_reviews:
            is_computer_generated, influential_words = explain_review(review.text)
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=is_computer_generated,
                    feedback_from_model=influential_words
                )
            )
        return ReviewPredictionResponse(reviews=computed_reviews_by_model)
    elif review_req.prediction_model == PredictionModels.RANDOM:
        from models.random import predict_review

        computed_reviews_by_model = []
        for review in review_req.user_reviews:
            is_computer_generated, influential_words = predict_review(review.text)
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=is_computer_generated,
                    feedback_from_model=influential_words
                )
            )
        return ReviewPredictionResponse(reviews=computed_reviews_by_model)

    elif review_req.prediction_model == PredictionModels.BERT:
        from models.bert import load_model, explain_with_lime
        model, tokenizer = load_model('../models/bert/saved_model_distilbert')

        computed_reviews_by_model = []
        for review in review_req.user_reviews:
            explanation = explain_with_lime(review.text, model, tokenizer, device='mps',
                                            num_features=len(review.text.split(' ')))

            # Ensure explanation is a Python dictionary
            explanation_data = json.loads(explanation)  # Convert JSON string back to dictionary
            print(explanation_data, '0----------------------->')
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=explanation_data["predicted_label"],
                    feedback_from_model=None,  # This is already in a dictionary format
                    certainty=explanation_data["certainty"]
                )
            )

        return ReviewPredictionResponse(reviews=computed_reviews_by_model)

    # Return an empty response if the model type is not recognized
    return ReviewPredictionResponse(reviews=[])
