# Review Analysis Script

This Python script analyzes product reviews for authenticity, leveraging the OpenAI API to flag potentially fake or misleading reviews. The analysis uses product specifications, descriptions, and the language used in each review to assess credibility and identify inconsistencies.

## Project Overview

1. **Data Loading**: Reads JSON data from `message.json`, containing product description, specifications, and multiple reviews.
2. **Review Parsing and Analysis**: For each review:
   - Checks whether the review's content aligns with the product specifications and description.
   - Examines the language for signs of artificiality or unnatural expressions.
   - Compares the review rating with the text to identify unusual or inflated ratings.
3. **Concurrency**: Utilizes multithreading for faster processing of multiple reviews.

## Files

- **`message.json`**: Input JSON file with keys `description`, `reviews`, and `specs`.
- **`review_analysis_<index>.json`**: Output JSON files containing analysis results for each review, labeled with an index.
- **`error_review_<index>.txt`**: Text files for reviews where errors occurred during JSON parsing, for debugging purposes.

## Requirements

- **Python 3.x**
- **OpenAI Python SDK**: Install with `pip install openai`
- **message.json**: A properly formatted input JSON file with:
  - `description`: String containing product details.
  - `reviews`: Array of dictionaries, each with:
    - `review_text`: The content of the review.
    - `review_value`: Rating given in the review.
  - `specs`: Dictionary with product specifications.

## Usage

1. Place `message.json` in the root directory.
2. Run the script:
   ```bash
   python analyze_reviews.py
