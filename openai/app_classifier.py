import json
from openai import OpenAI
import concurrent.futures

client = OpenAI()

# Step 1: Load JSON data from a file
with open('message.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Step 2: Access the description
description = data['description']
print("Description:", description)

# Step 3: Access the reviews
reviews = data['reviews']
for review in reviews:
    print("\nReview:", review['review_text'])
    print("Rating:", review['review_value'])

# Step 4: Access the specs
specs = data['specs']

# Define variables for the request
Product_Specs = specs
Product_Description = description

def analyze_review(index, review):
    # Extract review text and rating
    review_text = review['review_text']
    review_rating = review['review_value']

    # Create the completion request for each review
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Analyze the following review to determine if it is fake or misleading. "
                    "Please consider these criteria: 1. Does the review align with the product specifications and description? "
                    "2. Is the language used in the review natural and genuine? 3. Does the review rating correspond with the content of the review text? "
                    "4. Be aware that fake reviews often feature unusually high ratings. "
                    "Input: Product Specs: {}, Product Description: {}, Review Rating: {}, Review Text: {}. "
                    "Respond in JSON format as follows: "
                    "{{ \"label\": \"Yes\" or \"No\" (whether the review is real = Yes or fake = No), "
                    "\"confidence\": a floating-point number between 0 and 1 representing confidence in your answer, "
                    "\"explanation\": a brief explanation under 500 characters for why the output was chosen, "
                    "specifically mentioning any inconsistencies or indicators of a misleading review. }}"
                ).format(Product_Specs, Product_Description, review_rating, review_text)
            }
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

        # Save only the LLM response in a new JSON file
        file_name = f"review_analysis_{index + 1}.json"
        with open(file_name, "w", encoding="utf-8") as output_file:
            json.dump(response_content, output_file, indent=4)  # Save response content only

        # Optional: print the output for each review
        print("\nReview:", review_text)
        print("Rating:", review_rating)
        print("\n### LLM Response:", response_content)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for review {index + 1}: {e}")
        print("Raw response content:", completion.choices[0].message.content)

        # Save the raw response in a text file for debugging
        with open(f"error_review_{index + 1}.txt", "w", encoding="utf-8") as error_file:
            error_file.write(completion.choices[0].message.content)

# Use ThreadPoolExecutor to parallelize the review analysis
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(analyze_review, index, review): index for index, review in enumerate(reviews)}
    
    # Wait for the futures to complete and handle exceptions if any
    for future in concurrent.futures.as_completed(futures):
        index = futures[future]
        try:
            future.result()  # This will also raise exceptions if any occurred in the thread
        except Exception as exc:
            print(f'Review {index + 1} generated an exception: {exc}')