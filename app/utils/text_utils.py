# Utility Functions-This contains functions for text cleaning and splitting.
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def clean_text(text):
    # Remove excessive newlines and extra spaces
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with one
    text = re.sub(r' {2,}', ' ', text)  # Replace multiple spaces with one
    text = text.strip()  # Remove any trailing/leading spaces
    #text = re.sub(r'\d+', '', text) #remove numbers
    text = re.sub(r'[^\w\s]', '', text) #remove punctuation
    # Remove ###, **, and -
    text = re.sub(r'[#\*\-]+', '', text)
    return text

def chunk_text(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for doc in documents:
        cleaned_text = clean_text(doc.page_content)
        chunks.extend(splitter.split_text(cleaned_text))
    return chunks