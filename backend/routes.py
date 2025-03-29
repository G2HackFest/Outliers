from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embedder = SentenceTransformer('all-MiniLM-L6-v2')

@app.route("/cases/similar", methods=["POST"])
def find_similar_cases():
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    query_embedding = embedder.encode(query)
    cases = list(cases_collection.find({}, {"_id": 1, "text": 1, "judgment": 1}))
    for case in cases:
        case["embedding"] = embedder.encode(case["text"])

    similarities = [
        (case["_id"], cosine_similarity([query_embedding], [case["embedding"]])[0][0])
        for case in cases
    ]
    sorted_cases = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]
    similar_cases = [case for case_id, _ in sorted_cases for case in cases if str(case["_id"]) == case_id]
    return jsonify(similar_cases)
