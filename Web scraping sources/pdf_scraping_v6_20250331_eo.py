# -*- coding: utf-8 -*-
"""PDF Scraping v6 20250331 eo.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Q1JoAdMT7An7sF8XYmNU-x-sjidsWSXb
"""

!apt-get install -y tesseract-ocr
!pip install pytesseract pymupdf pdf2image
!apt-get install -y poppler-utils

import requests
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os

# Converted Google Drive links to Downloadable file IDs in my drive.
file_ids = [
    "156cEB1WauwkgjaPwPR_D0B3qQcXxGCfF",
    "1RwKejaEbKJVAirFfHPjDKg5F6SpDS5Y5",
    "1tZbvaR66aMJtfmv95v37esLpkyfz-ynl",
    "1mwct2zOZYjR1ld_t5qFSKAmeF8FIDR6a",
    "1pzFBTu6qky8wz2GexXa7oBJgoUKIRhj7"
]

# My directory Folder to save PDFs after downloading from link for processing
pdf_folder = "/content/pdfs"
os.makedirs(pdf_folder, exist_ok=True)

# Download PDFs from Google Drive
def download_pdf(file_id, save_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded: {save_path}")

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""

    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")  # Extract normal text

        # Use OCR if no text is found
        if not text.strip():
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            for img in images:
                text += pytesseract.image_to_string(img)

        all_text += f"\n\n--- Page {page_num + 1} ---\n{text}"

    return all_text

# Process all PDFs
pdf_texts = {}
for file_id in file_ids:
    pdf_path = os.path.join(pdf_folder, f"{file_id}.pdf")
    download_pdf(file_id, pdf_path)
    extracted_text = extract_text_from_pdf(pdf_path)
    pdf_texts[pdf_path] = extracted_text

# Print **all** extracted text
for pdf, text in pdf_texts.items():
    print(f"\n🔹 Extracted from {pdf}:\n{text}\n")

for pdf, text in pdf_texts.items():
    output_file = pdf.replace(".pdf", ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f" Saved full text: {output_file}")

!pip install nltk textblob spacy wordcloud
!python -m spacy download en_core_web_sm

import re
import spacy
import nltk
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from collections import Counter

nltk.download('punkt')

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

# 🔹 Sample extracted text (Replace this with your PDF extracted data)
pdf_texts = {
    "/content/pdfs/156cEB1WauwkgjaPwPR_D0B3qQcXxGCfF.txt",
    "document_2": "The customer satisfaction was rated 4.5 stars. Issues were reported in logistics.",
    "document_3": "The economy is improving, but inflation is still high. Future predictions are uncertain.",
}

# 🎯 Text Cleaning Function
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove special characters
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.strip()
    return text

# 🎯 NLP Processing Function
def process_text(text):
    doc = nlp(text)

    # Extract nouns and verbs (important words)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "VERB"]]

    # Sentiment Analysis
    sentiment = TextBlob(text).sentiment.polarity  # Range: -1 (negative) to 1 (positive)

    return {
        "cleaned_text": text,
        "keywords": keywords,
        "sentiment": sentiment
    }

# 🔄 Process all PDFs
processed_results = {}
for doc, text in pdf_texts.items():
    cleaned_text = clean_text(text)
    analysis = process_text(cleaned_text)
    processed_results[doc] = analysis

# 📌 Convert Results to DataFrame
df = pd.DataFrame.from_dict(processed_results, orient="index")
print(df)

# 🎨 Word Cloud Visualization
all_text = " ".join(df["cleaned_text"])
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

from google.colab import drive
drive.mount('/content/drive')

df.to_csv("processed_text_results.csv", index=True)
print("✅ Saved results to CSV!")