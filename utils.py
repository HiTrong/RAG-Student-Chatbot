import streamlit as st
from datetime import datetime
from underthesea import ner
import time

def typewriter_effect(placeholder, text, delay=0.02):
    typed_text = "" 
    for char in text:
        typed_text += char  
        placeholder.text(typed_text) 
        time.sleep(delay)
    placeholder.text("")
    return placeholder

def get_timestamp():
    return str(datetime.now().strftime("%Y%m%d_%H%M%S"))

def get_keyword_name(sentence):
    entities = ner(sentence)
    important_info = " ".join([entity[0] for entity in entities if entity[3] in ["B-ORG", "I-LOC","B-MISC", "B-PER", "B-DATE"] or (entity[2] in ['B-NP','B-AP','B-VP'] and entity[1] in ['N','A','V'])])
    chat_name = f"{important_info}"
    return chat_name