import random

def predict_review(review):
    word_list = ["apple", "banana", "orange", "grape", "mango", "strawberry", "kiwi", "watermelon", "pineapple",
                 "blueberry"]

    return random.choice([True, False]), random.choice(word_list)