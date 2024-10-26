from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from models.model_types import PredictionModels

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
def review_prediction(review_req: ProductReviewRequest, request: Request) -> ReviewPredictionResponse:
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
        # Access the preloaded BERT model and tokenizer from app state
        bert_model = request.app.state.bert_model
        bert_tokenizer = request.app.state.bert_tokenizer
        
        if bert_model is None or bert_tokenizer is None:
            raise HTTPException(status_code=500, detail="Model not loaded. Please try again later.")

        # Use the preloaded model and tokenizer
        from models.bert import prediction
        computed_reviews_by_model = []
        for review in review_req.user_reviews:
            response = prediction(review.text, bert_model, bert_tokenizer, device='cpu',
                                            num_features=len(review.text.split(' ')))
            
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=response.get('predicted_label'),
                    feedback_from_model=response.get('explanation'),
                    certainty=response.get("certainty")
                )
            )

        return ReviewPredictionResponse(reviews=computed_reviews_by_model)

    return ReviewPredictionResponse(reviews=[])