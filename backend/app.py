from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
import json
import re

# --- Additional Imports for RAG System ---
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
import google.generativeai as genai
import PyPDF2
import pytesseract
from PIL import Image

app = Flask(__name__)
CORS(app)

# --- Connect to MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["legalDB"]
cases_collection = db["cases"]

# --- Initialize Gemini API ---
genai.configure(api_key="AIzaSyBBdLK55edeg2WrhqacOGqxrcqgiLtUNyo")  # Replace with your key

# --- Load Cases from MongoDB & Generate Embeddings ---
def load_cases():
    cases = list(cases_collection.find({}, {"judgment": 0}))
    print(f"Loaded {len(cases)} cases from MongoDB.")
    return cases

case_data = load_cases()

# Load text embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')
for case in case_data:
    description = case.get("description", "")
    embedding = embedder.encode(description)
    case["embedding"] = embedding
print("Embeddings generated for all cases.")

def find_similar_cases(query, top_n=3):
    query_embedding = embedder.encode(query)
    similarities = [
        (str(case["_id"]), cosine_similarity([query_embedding], [case["embedding"]])[0][0])
        for case in case_data
    ]
    sorted_cases = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]
    print("🔎 Similarity Scores:", sorted_cases)
    similar_cases = []
    for case_id, score in sorted_cases:
        for case in case_data:
            if str(case["_id"]) == case_id:
                similar_cases.append({
                    "title": case.get("title"),
                    "description": case.get("description"),
                    "score": score
                })
                break
    return similar_cases

def extract_text_from_file(file_path):
    text = ""
    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    elif file_path.lower().endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file_path)
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    raise Exception("Empty text")
            except Exception as e:
                print("Page extraction failed, attempting OCR...")
                image_path = "temp_page.png"
                with open(image_path, "wb") as img_file:
                    img_file.write(page.get_contents())
                text += pytesseract.image_to_string(Image.open(image_path))
                os.remove(image_path)
    return text.strip()

def clean_text(text):
    # Remove noisy symbols (like # and *) and extra whitespace
    cleaned = re.sub(r'[#*]+', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def summarize_text(text):
    # Updated prompt: request output as bullet points (each on a new line)
    prompt = (
        f"Summarize the following legal document and extract key points.\n\n"
        f"Document:\n{text}\n\n"
        "Provide a concise summary and list each key point on a new line preceded by a bullet (e.g., - )."
    )
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(contents=prompt)
        summary = clean_text(response.text)
        # Prepend a document emoji for friendliness
        return "📄 " + summary
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return "Error: Could not generate summary."

def generate_response(query, document_summary):
    relevant_cases = find_similar_cases(query)
    past_case_descriptions = "\n".join(
        [f"- {case['title']}: {case['description']}" for case in relevant_cases]
    )
    prompt = (
        f"User Query: {query}\n\n"
        f"Summarized Document:\n{document_summary}\n\n"
        f"Relevant Past Cases:\n{past_case_descriptions}\n\n"
        "Provide a legal response in 10 detailed points with reasoning. "
        "List each point on a separate line preceded by a bullet (e.g., - )."
    )
    print("Prompt for Gemini API:\n", prompt)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(contents=prompt)
        final_response = clean_text(response.text)
        return "🤖 " + final_response
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Error: Could not generate legal response."

# --- Existing Endpoints for Case Management ---
@app.route("/cases", methods=["GET"])
def get_cases():
    cases = list(cases_collection.find({}, {"_id": 1, "title": 1, "description": 1, "imageUrl": 1}))
    for case in cases:
        case["_id"] = str(case["_id"])
    return jsonify(cases)

@app.route("/cases/add", methods=["POST"])
def add_case():
    data = request.json
    if not data or "title" not in data or "description" not in data or "imageUrl" not in data:
        return jsonify({"error": "Invalid data"}), 400
    new_case = {
        "title": data["title"],
        "description": data["description"],
        "imageUrl": data["imageUrl"],
    }
    cases_collection.insert_one(new_case)
    return jsonify({"message": "Case added successfully"}), 201

# --- New Endpoints for RAG System ---
@app.route("/rag/process", methods=["POST"])
def process_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    file_ext = os.path.splitext(file.filename)[1].lower()
    temp_filename = "temp_upload" + file_ext
    file.save(temp_filename)
    extracted_text = extract_text_from_file(temp_filename)
    if not extracted_text:
        os.remove(temp_filename)
        return jsonify({"error": "Failed to extract text from file"}), 400
    document_summary = summarize_text(extracted_text)
    os.remove(temp_filename)
    return jsonify({"document_summary": document_summary})

@app.route("/rag/query", methods=["POST"])
def query_response():
    data = request.json
    if not data or "legal_query" not in data or "document_summary" not in data:
        return jsonify({"error": "Invalid data"}), 400
    legal_query = data["legal_query"]
    document_summary = data["document_summary"]
    ai_response = generate_response(legal_query, document_summary)
    return jsonify({"ai_response": ai_response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
