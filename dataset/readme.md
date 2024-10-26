1. char_count (Character Count)

	•	Description: Total number of characters in the review text.
	•	Purpose: Measures the length of the review. Extremely short or excessively long reviews might be indicative of spam or deceptive content.

2. word_count

	•	Description: Total number of words in the review text.
	•	Purpose: Similar to char_count, it provides insight into the length of the review. Unusually short or long reviews might signal unnatural writing.

3. sentence_count

	•	Description: Total number of sentences in the review text.
	•	Purpose: Helps assess the complexity and verbosity of the review. Reviews with very few or many sentences might be atypical.

4. avg_sentence_length (Average Sentence Length)

	•	Description: Average number of words per sentence, calculated as word_count / sentence_count.
	•	Purpose: Indicates the complexity of sentence structures. Extremely long or short sentences can be a sign of unnatural writing or automated text generation.

5. vocab_richness (Vocabulary Richness)

	•	Description: The ratio of unique words to total words, calculated as number of unique words / word_count.
	•	Purpose: Measures the diversity of vocabulary used. Low vocabulary richness might indicate repetitive or templated language, common in fake reviews.

6. pos_ratio_NN (Noun Ratio)

	•	Description: Proportion of nouns (NN) in the text relative to all part-of-speech (POS) tags.
	•	Purpose: High noun usage can indicate focus on specific entities or objects, which is typical in genuine reviews.

7. pos_ratio_JJ (Adjective Ratio)

	•	Description: Proportion of adjectives (JJ) in the text relative to all POS tags.
	•	Purpose: Adjectives describe qualities and attributes. Excessive use may suggest exaggeration or overemphasis, which can be characteristic of fake reviews.

8. pos_ratio_RB (Adverb Ratio)

	•	Description: Proportion of adverbs (RB) in the text relative to all POS tags.
	•	Purpose: Adverbs modify verbs and adjectives, often intensifying them. Overuse may indicate an attempt to exaggerate or manipulate sentiment.

9. pos_ratio_VB (Verb Ratio)

	•	Description: Proportion of base form verbs (VB) in the text relative to all POS tags.
	•	Purpose: Verbs are essential for action and state descriptions. An unusual verb ratio might indicate unnatural language patterns.

10. polarity

	•	Description: Sentiment polarity score of the review, ranging from -1 (very negative) to +1 (very positive).
	•	Purpose: Indicates the overall sentiment expressed. Extreme sentiments might be a sign of biased or fake reviews attempting to sway opinions.

11. subjectivity

	•	Description: Subjectivity score of the review, ranging from 0 (very objective) to 1 (very subjective).
	•	Purpose: Measures how subjective or objective the language is. Highly subjective reviews may be more opinion-based, which could be a trait of deceptive reviews.

12. flesch_reading_ease

	•	Description: A readability score indicating how easy the text is to read. Higher scores mean easier readability.
	•	Purpose: Helps assess the complexity of the text. Extremely simple or complex language might indicate unnatural writing.

13. flesch_kincaid_grade

	•	Description: Indicates the U.S. school grade level required to understand the text.
	•	Purpose: Provides insight into the complexity of the language used. Unusually high or low grade levels may be atypical for standard reviews.

14. gunning_fog

	•	Description: Readability index estimating the years of formal education needed to understand the text.
	•	Purpose: Another measure of text complexity. Helps identify if the review is unusually complex or simplistic.

15. smog_index

	•	Description: Estimates the years of education needed to understand the text based on the number of complex words.
	•	Purpose: Assesses the level of complexity, focusing on polysyllabic words.

16. automated_readability_index

	•	Description: Readability metric based on characters per word and words per sentence.
	•	Purpose: Evaluates text complexity, helpful in identifying abnormal writing styles.

17. coleman_liau_index

	•	Description: Readability measure based on characters per word and sentences per word.
	•	Purpose: Provides another angle on text complexity and readability.

18. stopword_ratio

	•	Description: Proportion of stopwords (common words like ‘the’, ‘and’, ‘is’) to total words.
	•	Purpose: Natural language tends to have a higher stopword ratio. Low ratios might indicate unnatural or generated text.

19. numerals_ratio

	•	Description: Proportion of numeric digits to total words.
	•	Purpose: Reviews with many numbers may provide specific details or could be spammy if overused.

20. punctuation_ratio

	•	Description: Proportion of punctuation marks to total characters.
	•	Purpose: Excessive punctuation may indicate emotional emphasis or unnatural writing patterns.

21. personal_pronoun_ratio

	•	Description: Proportion of personal pronouns (e.g., ‘I’, ‘we’, ‘my’, ‘our’) to total words.
	•	Purpose: Genuine reviews often include personal experiences, reflected by the use of personal pronouns.

22. hedging_ratio

	•	Description: Proportion of hedging words (e.g., ‘maybe’, ‘probably’, ‘might’) to total words.
	•	Purpose: Hedging indicates uncertainty or caution. Unusual levels might suggest deceptive language aiming to appear genuine.

23. certainty_ratio

	•	Description: Proportion of certainty words (e.g., ‘definitely’, ‘absolutely’, ‘always’) to total words.
	•	Purpose: High certainty can indicate overconfidence or exaggeration, possibly reflecting fake reviews trying to persuade.

24. repeated_phrases_count

	•	Description: Number of repeated phrases within the review text.
	•	Purpose: Repetition may signal templated or automated content, common in fake reviews.

25. all_caps_ratio

	•	Description: Proportion of words in all uppercase letters to total words.
	•	Purpose: All caps are often used for emphasis or to convey strong emotions. Excessive use may indicate emotional manipulation.

26. exclamation_ratio

	•	Description: Proportion of exclamation marks to total characters.
	•	Purpose: Excessive exclamation marks may signify exaggerated enthusiasm or urgency, potentially indicating a fake review.

27. question_ratio

	•	Description: Proportion of question marks to total characters.
	•	Purpose: Unusual use of questions can be a rhetorical device in deceptive reviews or may indicate confusion.

28. avg_word_length (Average Word Length)

	•	Description: Average length of words in the text, calculated by the mean number of characters per word.
	•	Purpose: Indicates the complexity of vocabulary. Extremely long or short average word lengths might be atypical.
