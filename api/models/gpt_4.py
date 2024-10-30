import functools
import json
from openai import OpenAI
import concurrent.futures


client = OpenAI()


@functools.lru_cache(maxsize=32)
def analyze_and_sumarize_gpt(description, reviews, specs, model):
    specs=dict(specs)
    reviews = [dict(review) for review in reviews]
    # List to hold review results (non-fake reviews and all reviews)
    review_results = []

    # Use ThreadPoolExecutor to parallelize the review analysis
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(analyze_review, specs, description, index, review, model): index
            for index, review in enumerate(reviews)
        }

        # Wait for the futures to complete and handle exceptions if any
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result = future.result()[0]
                review_results.append(result)  # This will also raise exceptions if any occurred in the thread
            except Exception as exc:
                print(f'Review {index + 1} generated an exception: {exc}')

    # Sort the reviews based on the original index as threadpool executes them in random order
    review_results = sorted(review_results, key=lambda x: x['index'])

    # Generate a summary using OpenAI API for non-fake reviews
    non_fake_reviews = [
        f"Review {i + 1}: {review['review_text']} (Confidence: {review['confidence']})"
        for i, review in enumerate(review_results) if review['label'] == "No"
    ]

    # Calculate the confidence as the ratio of non-fake reviews
    total_reviews = len(review_results)
    non_fake_count = sum(1 for review in review_results if review['label'] == "No")
    trust_ratio = non_fake_count / total_reviews if total_reviews > 0 else 0

    # Define system and user prompts for summary generation
    summary_system_prompt = (
        "You are a helpful assistant that provides summaries of product reviews. "
        "Generate a concise summary of genuine customer reviews, focusing on their main points, "
        "highlighting common praises, criticisms, and themes if they appear across reviews. "
        "This summary should not exceed 200 words."
    )
    summary_user_prompt = "Here are the reviews:\n\n" + "\n".join(non_fake_reviews)

    # Create the summary completion request with separate system and user prompts
    summary_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": summary_system_prompt},
            {"role": "user", "content": summary_user_prompt}
        ]
    )

    # Extract the summary text
    summary_text = summary_completion.choices[0].message.content

    # Return the processed data
    return {
        "reviews": review_results,
        "adjusted_review_score": trust_ratio,
        "feedback_from_model": summary_text
    }


def analyze_review(specs, description, index, review, model):
    # Extract review text and rating
    review_text = review["text"]
    review_rating = review["review_value"]

    # Results of the review
    review_results = []

    # System prompt defining the assistant's role and response format
    system_prompt = (
        "You are an assistant that analyzes product reviews to determine if they are fake or misleading. "
        "Base your analysis on the product specifications, description, and review details provided. "
        "Respond in JSON format as follows: "
        "{ \"label\": \"Yes\" or \"No\" (whether the review is fake or real), "
        "\"confidence\": a floating-point number between 0 and 1 representing confidence in your answer, "
        "\"explanation\": a brief explanation under 500 characters for why the output was chosen, "
        "mentioning any inconsistencies or indicators of a misleading review. }"
    )

    # User prompt with specific review details
    user_prompt = (
        f"Product Specs: {specs}, Product Description: {description}, "
        f"Review Rating: {review_rating}, Review Text: {review_text}."
    )

    # Create the completion request for each review with system and user prompts
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Attempt to parse the JSON response, handle errors if they arise
    try:
        # Ensure the response is a valid JSON string
        response_content = completion.choices[0].message.content

        # Check if response starts with "```json"
        if response_content.startswith("```json"):
            # Split into lines, remove the first and last line, and rejoin
            lines = response_content.splitlines()
            response_content = "\n".join(lines[1:-1])  # Remove first and last lines

        # Parse the potentially modified response content
        response_content = json.loads(response_content)

        # Append the relevant data to the review_results list
        review_results.append({
            "review_text": review_text,
            "label": response_content.get("label"),
            "confidence": response_content.get("confidence"),
            "explanation": response_content.get("explanation"),
            "index": index
        })

        return review_results

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for review {index + 1}: {e}")
        print("Raw response content:", completion.choices[0].message.content)
        raise e
