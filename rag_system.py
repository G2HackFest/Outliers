# rag_system.py

# ✅ Step 1: Import Dependencies
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
import google.generativeai as genai  # Gemini API client
import json
import os

# For file extraction
import PyPDF2
import pytesseract
from PIL import Image

# For file upload in Colab (if used; otherwise, you can run locally with your own file paths)
try:
    from google.colab import files
    COLAB_MODE = True
except ImportError:
    COLAB_MODE = False

# ✅ Step 2: Configure Gemini API
genai.configure(api_key="AIzaSyDcHA-3G5Je9p8xAtCb423chuAVxt2zPsk")  # Replace with your API key

# ✅ Step 3: Connect to Local MongoDB Database
client = MongoClient("mongodb://localhost:27017/")
db = client["legalDB"]
cases_collection = db["cases"]

# ✅ Step 4: Load Cases from MongoDB
# Assuming each document has at least: _id, title, description, imageUrl
def load_cases():
    # Exclude the judgment field if it exists
    cases = list(cases_collection.find({}, {"judgment": 0}))
    print(f"Loaded {len(cases)} cases from MongoDB.")
    return cases

case_data = load_cases()

# ✅ Step 5: Load Text Embedding Model and Embed Each Case Description
embedder = SentenceTransformer('all-MiniLM-L6-v2')

for case in case_data:
    # We use the "description" field for embeddings
    description = case.get("description", "")
    embedding = embedder.encode(description)
    case["embedding"] = embedding

print("Embeddings generated for all cases.")

# ✅ Step 6: Function to Retrieve Similar Cases Based on Query
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

# ✅ Step 7: Functions for File Upload, Extraction, and Summarization

# (a) Extract text from TXT or PDF (using OCR for image-based PDFs)
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
                # Fallback: save page as image and use OCR
                print("Page extraction failed, attempting OCR...")
                # (This is a simplified approach; you might need a more robust conversion)
                image_path = "temp_page.png"
                with open(image_path, "wb") as img_file:
                    img_file.write(page.get_contents())
                text += pytesseract.image_to_string(Image.open(image_path))
                os.remove(image_path)
    return text.strip()

# (b) Summarize Extracted Text using Gemini API
def summarize_text(text):
    prompt = (
        f"Summarize the following legal document and extract key points:\n\n{text}\n\n"
        "Provide a concise summary and list the key points:"
    )
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(contents=prompt)
        return response.text
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return "Error: Could not generate summary."

# ✅ Step 8: Function to Generate a Legal Response Using Gemini API
def generate_response(query, document_summary):
    # Retrieve similar cases from MongoDB (using description embeddings)
    relevant_cases = find_similar_cases(query)
    # Build the prompt including the document summary and past case details
    past_case_descriptions = "\n".join(
        [f"- {case['title']}: {case['description']}" for case in relevant_cases]
    )
    prompt = (
        f"User Query: {query}\n\n"
        f"Summarized Document:\n{document_summary}\n\n"
        f"Relevant Past Cases:\n{past_case_descriptions}\n\n"
        "Provide a legal response in 10 detailed points with reasoning:"
    )
    print("Prompt for Gemini API:\n", prompt)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(contents=prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Error: Could not generate legal response."

# ✅ Step 9: Visualization of RAG Workflow (Optional)
def visualize_rag_workflow(query):
    similar_cases = find_similar_cases(query)
    G = nx.DiGraph()
    G.add_node("User Query")
    for idx, case in enumerate(similar_cases):
        G.add_node(f"Case {idx+1}: {case['title']}")
        G.add_edge("User Query", f"Case {idx+1}: {case['title']}")
    G.add_node("AI Response")
    for idx in range(len(similar_cases)):
        G.add_edge(f"Case {idx+1}: {similar_cases[idx]['title']}", "AI Response")
    
    plt.figure(figsize=(10, 6))
    nx.draw_networkx(G, with_labels=True, node_size=2000, node_color="lightblue", font_size=9, font_color="black")
    plt.title("RAG Workflow Visualization")
    plt.show()

# ✅ Step 10: Main Execution Block
if __name__ == "__main__":
    # --- Part A: Process File Upload and Summarize Document ---
    if COLAB_MODE:
        print("Please upload a TXT or PDF file:")
        uploaded = files.upload()  # For Colab: upload file interactively
        file_path = list(uploaded.keys())[0]
    else:
        file_path = input("Enter the path to your TXT or PDF file: ")
    
    print(f"Processing file: {file_path}")
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        print("Error: Could not extract text from the file.")
        exit()
    
    document_summary = summarize_text(extracted_text)
    print("\n🔹 Document Summary and Key Points:\n", document_summary)
    
    # --- Part B: Query-Based Response Generation ---
    user_query = input("\nEnter your legal query: ")``
    ai_response = generate_response(user_query, document_summary)
    print("\n🔹 AI Legal Response:\n", ai_response)
    
    # Optionally visualize the RAG workflow
    visualize_option = input("\nWould you like to visualize the RAG workflow? (y/n): ")
    if visualize_option.lower() == "y":
        visualize_rag_workflow(user_query)
