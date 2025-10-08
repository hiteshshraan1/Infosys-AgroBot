

import streamlit as st
import json
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


@st.cache_resource
def get_nltk_lemmatizer():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
    return WordNetLemmatizer()

lemmatizer = get_nltk_lemmatizer()


@st.cache_resource
def load_knowledge_base():
    """
    Loads the bilingual JSON database.
    This function is now available for import in other files.
    """
    kb_path = "data/bilingual_knowledge_base.json"
    if os.path.exists(kb_path) and os.path.getsize(kb_path) > 0:
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}


def analyze_symptoms_by_text(sentence: str, lang_code: str):
    """
    Processes a text sentence to find the best matching disease based on keywords.
    """
    knowledge_base = load_knowledge_base() 
    if not knowledge_base:
        return None

    tokens = word_tokenize(sentence.lower())
    issue_scores = {}

    for issue_id, issue_data in knowledge_base.items():
        score = 0
        keywords_for_lang = issue_data.get("keywords", {}).get(lang_code, [])
        if not keywords_for_lang:
            continue

        for token in tokens:
            if token in keywords_for_lang:
                score += 1

        if score > 0:
            normalized_score = score / len(keywords_for_lang)
            issue_scores[issue_id] = normalized_score

    if not issue_scores:
        return None

    best_issue_id = max(issue_scores, key=issue_scores.get)
    return knowledge_base[best_issue_id]


def get_disease_info(disease_key: str):
    """
    Retrieves the full data for a given disease key from the knowledge base.
    """
    knowledge_base = load_knowledge_base() 
    return knowledge_base.get(disease_key)