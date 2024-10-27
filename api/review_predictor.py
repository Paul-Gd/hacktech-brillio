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
    elif review_req.prediction_model == PredictionModels.GPT_4:
        from models.gpt_4 import analyze_and_sumarize_gpt

        summary_and_rating_data = analyze_and_sumarize_gpt(review_req)
        computed_reviews_by_model = []
        for review in summary_and_rating_data["reviews"]:
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=review['label'] == "Yes",
                    feedback_from_model=review['explanation'],
                    certainty=review['confidence']
                )
            )
        aggregated_review_data = AggregatedReviewResults(
            adjusted_review_score=summary_and_rating_data["adjusted_review_score"],
            feedback_from_model=summary_and_rating_data["feedback_from_model"]
        )
        return ReviewPredictionResponse(reviews=computed_reviews_by_model,
                                        aggregated_review_data=aggregated_review_data)

    elif review_req.prediction_model == PredictionModels.BERT:
        # Access the preloaded BERT model and tokenizer from app state
        bert_model = request.app.state.bert_model
        bert_tokenizer = request.app.state.bert_tokenizer

        if bert_model is None or bert_tokenizer is None:
            raise HTTPException(status_code=500, detail="Model not loaded. Please try again later.")

        from models.bert import prediction
        computed_reviews_by_model = []
        total_certainty = 0.0
        positive_feedback = []

        # Prepare the list of reviews for batch prediction
        reviews = [review.text for review in review_req.user_reviews]
        responses = prediction(reviews, bert_model, bert_tokenizer, device='cpu', num_features=10)

        for response in responses:
            # Append each review result to computed_reviews_by_model
            computed_reviews_by_model.append(
                IndividualReviewResult(
                    is_computer_generated=response.get('predicted_label'),
                    feedback_from_model=response.get('explanation'),
                    certainty=response.get("certainty")
                )
            )

            # Accumulate certainty for adjusted score calculation
            total_certainty += response.get("certainty", 0.0)
            
            # Collect positive feedback explanation summaries for aggregation
            if response.get("predicted_label"):
                positive_feedback.append(response.get("explanation"))

        # Calculate aggregated review data
        adjusted_review_score = total_certainty / len(computed_reviews_by_model) if computed_reviews_by_model else None

        aggregated_review_data = AggregatedReviewResults(
            adjusted_review_score=adjusted_review_score,
            feedback_from_model=None
        )

        return ReviewPredictionResponse(
            reviews=computed_reviews_by_model,
            aggregated_review_data=aggregated_review_data
        )


    return ReviewPredictionResponse(reviews=[])
