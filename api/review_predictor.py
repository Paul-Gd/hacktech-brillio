from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.model_types import PredictionModels

review_prediction_router = APIRouter()


class ProductReviewRequest(BaseModel):
    description: str | None = Field(default=None, title="The description of the item")
    specs: dict[str, str] = Field(default={}, title="The product specifications from page")
    user_reviews: list[str] = Field(title="The reviews of the product")
    prediction_model: PredictionModels = Field(title="The model to use for prediction",
                                               default=PredictionModels.NAIVE_BAYES)


class AggregatedReviewResults(BaseModel):
    adjusted_review_score: float | None = Field(default=None, title="The adjusted score based on the excluded reviews")
    feedback_from_model: str | None = Field(default=None, title="Additional feedback returned by the model")


class IndividualReviewResult(BaseModel):
    is_computer_generated: bool = Field(title="Whether the review is computer generated or not")
    feedback_from_model: str | None = Field(default=None, title="Additional feedback returned by the model")


class ReviewPredictionResponse(BaseModel):
    reviews: list[IndividualReviewResult] = Field(title="The reviews of the product")
    aggregated_review_data: AggregatedReviewResults | None = Field(default=None,
                                                                   title="The aggregated review of the product")


@review_prediction_router.post("/review_prediction/")
def review_prediction(review_req: ProductReviewRequest) -> ReviewPredictionResponse:
    if review_req.prediction_model == PredictionModels.NAIVE_BAYES:
        from models.naive_bayes import predict_review_is_cg

        computed_reviews_by_model = [IndividualReviewResult(is_computer_generated=predict_review_is_cg(review)) for
                                     review in review_req.user_reviews]
        return ReviewPredictionResponse(reviews=computed_reviews_by_model,
                                        aggregated_review_data=None)
    return ReviewPredictionResponse(reviews=[])
