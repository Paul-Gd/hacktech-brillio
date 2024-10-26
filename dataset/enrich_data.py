import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')

import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from textblob import TextBlob
from textstat import (
    flesch_reading_ease,
    flesch_kincaid_grade,
    gunning_fog,
    smog_index,
    automated_readability_index,
    coleman_liau_index,
)
from collections import Counter
import string
import re

stop_words = set(stopwords.words('english'))

def extract_features(text):
    features = {}
    
    
    text_lower = text.lower()
    words = word_tokenize(text_lower)
    sentences = sent_tokenize(text)
    features['char_count'] = len(text)
    features['word_count'] = len(words)
    features['sentence_count'] = len(sentences)
    
    
    features['avg_sentence_length'] = features['word_count'] / features['sentence_count'] if features['sentence_count'] > 0 else 0
    
    
    features['vocab_richness'] = len(set(words)) / features['word_count'] if features['word_count'] > 0 else 0
    
    
    pos_tags = pos_tag(words)
    pos_counts = Counter(tag for word, tag in pos_tags)
    total_pos = sum(pos_counts.values())
    pos_ratios = {tag: count / total_pos for tag, count in pos_counts.items()}
    
    for tag in ['NN', 'JJ', 'RB', 'VB']:
        features[f'pos_ratio_{tag}'] = pos_ratios.get(tag, 0)
    
    
    blob = TextBlob(text)
    features['polarity'] = blob.sentiment.polarity
    features['subjectivity'] = blob.sentiment.subjectivity
    
    
    try:
        features['flesch_reading_ease'] = flesch_reading_ease(text)
    except:
        features['flesch_reading_ease'] = None
    try:
        features['flesch_kincaid_grade'] = flesch_kincaid_grade(text)
    except:
        features['flesch_kincaid_grade'] = None
    try:
        features['gunning_fog'] = gunning_fog(text)
    except:
        features['gunning_fog'] = None
    try:
        features['smog_index'] = smog_index(text)
    except:
        features['smog_index'] = None
    try:
        features['automated_readability_index'] = automated_readability_index(text)
    except:
        features['automated_readability_index'] = None
    try:
        features['coleman_liau_index'] = coleman_liau_index(text)
    except:
        features['coleman_liau_index'] = None
    
    
    stopword_count = sum(1 for word in words if word in stop_words)
    features['stopword_ratio'] = stopword_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    numerals_count = sum(1 for word in words if word.isdigit())
    features['numerals_ratio'] = numerals_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    features['punctuation_ratio'] = punctuation_count / features['char_count'] if features['char_count'] > 0 else 0
        
    
    personal_pronouns = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}
    personal_pronoun_count = sum(1 for word in words if word in personal_pronouns)
    features['personal_pronoun_ratio'] = personal_pronoun_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    hedging_words = {'maybe', 'probably', 'possibly', 'might', 'could', 'seems', 'appears', 'likely', 'presumably', 'apparently'}
    hedging_count = sum(1 for word in words if word in hedging_words)
    features['hedging_ratio'] = hedging_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    certainty_words = {'definitely', 'certainly', 'absolutely', 'always', 'never', 'undoubtedly', 'surely', 'must', 'will', 'guaranteed'}
    certainty_count = sum(1 for word in words if word in certainty_words)
    features['certainty_ratio'] = certainty_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    repeated_phrases = re.findall(r'(\b\w+\b(?:\s+\b\w+\b){0,3})\s+\1', text_lower)
    features['repeated_phrases_count'] = len(repeated_phrases)
    
    
    all_caps_count = sum(1 for word in words if word.isupper() and len(word) > 1)
    features['all_caps_ratio'] = all_caps_count / features['word_count'] if features['word_count'] > 0 else 0
    
    
    exclamation_count = text.count('!')
    features['exclamation_ratio'] = exclamation_count / features['char_count'] if features['char_count'] > 0 else 0
    
    
    question_count = text.count('?')
    features['question_ratio'] = question_count / features['char_count'] if features['char_count'] > 0 else 0
    
    
    word_lengths = [len(word) for word in words if word.isalpha()]
    features['avg_word_length'] = np.mean(word_lengths) if word_lengths else 0
    
    return features
df = pd.read_csv('BrillioDataset/train-dataset_clean.csv')  


if 'review' not in df.columns:
    raise ValueError("The CSV file must contain a 'review' column.")


features_list = []


for idx, row in df.iterrows():
    text = str(row['review'])  
    features = extract_features(text)
    features_list.append(features)

features_df = pd.DataFrame(features_list)

enriched_df = pd.concat([df.reset_index(drop=True), features_df.reset_index(drop=True)], axis=1)

enriched_df.to_csv('BrillioDataset/enriched_reviews.csv', index=False)

print("Feature extraction complete. Enriched data saved to 'enriched_reviews.csv'.")