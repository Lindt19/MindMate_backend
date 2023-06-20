import spacy
import torch
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from spacytextblob.spacytextblob import SpacyTextBlob
from textblob_de import TextBlobDE
from textblob import TextBlob
from googletrans import Translator
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Initialize translator, NLP models, and pipelines
translator = Translator()
nlp_en = spacy.load('en_core_web_sm')
nlp_en.add_pipe('spacytextblob')
nltk.download('averaged_perceptron_tagger')
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)


def __sentences(text):
    return TextBlob(text).sentences


def __translate_to_english(text):
    """
    Translate the input text from German to English.

    Args:
        text (str): The input text.

    Returns:
        str: The translated text in English.
    """

    translated_text = translator.translate(text=text.replace("\n", "\n"), src='de', dest='en').text
    return translated_text


def __get_emotion(text):
    """
    Calculate the average emotion scores for the input text.

    Args:
        text (str): The input text.

    Returns:
        dict: A dictionary containing the average emotion scores.
    """
    sentences = nltk.sent_tokenize(text)
    split_text = []
    current_text = ""

    # create shorter texts so the nlp can handle the length (< 512)
    for sentence in sentences:
        if len(current_text) + len(sentence) < 512:
            current_text += sentence
        else:
            split_text.append(current_text)
            current_text = sentence

    split_text.append(current_text)

    emotion_averages = {}
    for text in split_text:
        result = emotion_classifier(text, truncation=True)

        if len(emotion_averages) == 0:
            emotion_averages = result
        else:
            for new_classification in result:
                for avg, curr in zip(emotion_averages[0], new_classification):
                    avg["score"] = (avg["score"] + curr["score"]) / 2

    return emotion_averages[0]


def __get_subjective(text):
    """
    Calculate the subjectivity score of the input text.

    Args:
        text (str): The input text.

    Returns:
        float: The subjectivity score in the range [0.0, 1.0] (objective to subjective).
    """
    doc = nlp_en(text)
    return doc._.blob.subjectivity


def __get_polarity(text):
    """
    Calculate the polarity score of the input text.

    Args:
        text (str): The input text.

    Returns:
        float: The polarity score in the range [-1.0, 1.0].
    """
    doc = nlp_en(text)
    return doc._.blob.sentiment.polarity


def __get_first_person_count(text):
    """
    Count the occurrences of first-person pronouns in the input text.

    Args:
        text (str): The input text.

    Returns:
        int: The count of first-person pronouns.
    """
    countElements = 0
    doc = nlp_en(text)
    for token in doc:
        if token.pos_ == "PRON" and token.morph.get("Person") == ["1"]:
            countElements = countElements + 1
    return countElements


def __get_future(text):
    """
    Count the number of future tense verbs in the input text.

    Args:
        text (str): The input text.

    Returns:
        int: The count of future tense verbs.
    """
    words = word_tokenize(text)

    # Tag the parts of speech in the text
    tagged_words = pos_tag(words)

    # Filter for verbs in the future tense
    future_verbs = [word for (word, tag) in tagged_words if tag == 'MD' and (word.lower() == 'will' or word.lower() == 'would')]
    return len(future_verbs)


def __get_past(text):
    """
    Count the number of past tense verbs in the input text.

    Args:
        text (str): The input text.

    Returns:
        int: The count of past tense verbs.
    """
    words = word_tokenize(text)

    # Tag the parts of speech in the text
    tagged_words = pos_tag(words)

    # Filter for verbs in the future tense
    past_tense_verbs = [word for word, tag in tagged_words if tag == "VBD"]
    return len(past_tense_verbs)


def __get_named_entities(text):
    """
    Extract the named entities from the input text.

    Args:
        text (str): The input text.

    Returns:
        list: A list of tuples containing the named entities and their labels.
    """
    doc = nlp_en(text)
    named_entities = [(entity.text, entity.label_) for entity in doc.ents]
    print("Named Entities:", named_entities)
    return named_entities


def __get_causal_keywords(text):
    """
    Check if the input text contains causal keywords.

    Args:
        text (str): The input text.

    Returns:
        int: 1 if causal keywords are found, 0 otherwise.
    """
    keywords = ["cause", "result", "because", "due to", "lead to", "caused", "causes", "causing", "resulted", "results"]

    found_keywords = [keyword for keyword in keywords if keyword in text.lower()]

    if found_keywords:
        return 1
    else:
        return 0
