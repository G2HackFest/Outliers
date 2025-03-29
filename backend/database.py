from pymongo import MongoClient

# Connect to MongoDB (Use local or MongoDB Atlas)
client = MongoClient("mongodb://localhost:27017/")
db = client["legalDB"]
cases_collection = db["cases"]

# Sample case document structure
sample_case = {
    "case_id": "12345",
    "title": "Smith v. Jones",
    "date": "2024-01-10",
    "summary": "This case involves a dispute over contract obligations...",
    "full_text": "Complete judgment text here...",
    "keywords": ["contract", "dispute", "obligations"],
    "outcome": "Ruled in favor of Smith",
}

# Insert a sample case if not already present
if cases_collection.count_documents({"case_id": "12345"}) == 0:
    cases_collection.insert_one(sample_case)
