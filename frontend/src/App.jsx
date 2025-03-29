import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Search, PlusCircle, ArrowLeftCircle } from "lucide-react";
import "./styles.css";

function App() {
  // Tab state: "cases" or "rag"
  const [activeTab, setActiveTab] = useState("cases");

  // States for Legal Case Manager (existing functionality)
  const [cases, setCases] = useState([]);
  const [filteredCases, setFilteredCases] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCase, setSelectedCase] = useState(null);
  const [error, setError] = useState("");

  // States for RAG System interface
  const [ragFile, setRagFile] = useState(null);
  const [ragFileName, setRagFileName] = useState("");
  const [documentSummary, setDocumentSummary] = useState("");
  const [legalQuery, setLegalQuery] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [ragError, setRagError] = useState("");

  useEffect(() => {
    if (activeTab === "cases") {
      fetchCases();
    }
  }, [activeTab]);

  // Existing functions for Case Manager
  const fetchCases = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5001/cases");
      setCases(response.data);
      setFilteredCases(response.data);
    } catch (err) {
      console.error("Error fetching cases:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim() || !imageUrl.trim()) {
      setError("Please fill in all fields.");
      return;
    }
    if (!isValidUrl(imageUrl)) {
      setError("Please provide a valid image URL.");
      return;
    }
    try {
      await axios.post("http://127.0.0.1:5001/cases/add", {
        title,
        description,
        imageUrl,
      });
      fetchCases();
      setTitle("");
      setDescription("");
      setImageUrl("");
      setError("");
    } catch (err) {
      console.error("Error adding case:", err);
      setError("Failed to add case.");
    }
  };

  const isValidUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch (_) {
      return false;
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    const filtered = cases.filter((caseItem) =>
      caseItem.title.toLowerCase().includes(query.toLowerCase()) ||
      caseItem.description.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredCases(filtered);
  };

  // New functions for RAG System
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setRagFile(e.target.files[0]);
      setRagFileName(e.target.files[0].name);
    }
  };

  const handleProcessDocument = async () => {
    if (!ragFile) {
      setRagError("Please select a file.");
      return;
    }
    setRagError("");
    const formData = new FormData();
    formData.append("file", ragFile);
    try {
      const response = await axios.post(
        "http://127.0.0.1:5001/rag/process",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setDocumentSummary(response.data.document_summary);
    } catch (err) {
      console.error("Error processing document:", err);
      setRagError("Failed to process document.");
    }
  };

  const handleGenerateResponse = async () => {
    if (!legalQuery || !documentSummary) {
      setRagError("Please process the document and provide your legal query.");
      return;
    }
    setRagError("");
    try {
      const response = await axios.post("http://127.0.0.1:5001/rag/query", {
        legal_query: legalQuery,
        document_summary: documentSummary,
      });
      setAiResponse(response.data.ai_response);
    } catch (err) {
      console.error("Error generating response:", err);
      setRagError("Failed to generate legal response.");
    }
  };

  return (
    <div className="app-container">
      {/* Navbar to switch between tabs */}
      <div className="navbar">
        <a onClick={() => setActiveTab("cases")} style={{ cursor: "pointer" }}>
          Legal Case
        </a>
        <a onClick={() => setActiveTab("rag")} style={{ cursor: "pointer" }}>
          RAG System
        </a>
      </div>
      <div className="main-container">
        {activeTab === "cases" ? (
          <>
            {selectedCase ? (
              <div>
                <button
                  className="back-button"
                  onClick={() => setSelectedCase(null)}
                >
                  <ArrowLeftCircle className="icon" />
                  Back to List
                </button>
                <motion.div
                  className="case-details"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                >
                  <img
                    src={selectedCase.imageUrl}
                    alt="Case"
                    className="case-image"
                  />
                  <h2 className="case-title">{selectedCase.title}</h2>
                  <p className="case-description">{selectedCase.description}</p>
                </motion.div>
              </div>
            ) : (
              <>
                <h1 className="app-title">LexGenie - Combination of law and Ai expert</h1>
                <div className="search-container">
                  <Search className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search cases..."
                    className="search-input"
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                  />
                </div>
                <form onSubmit={handleSubmit} className="form-container">
                  <h2 className="form-title">Add New Case</h2>
                  <input
                    type="text"
                    placeholder="Case Title"
                    className="form-input"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                  <textarea
                    placeholder="Case Description"
                    className="form-textarea"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  ></textarea>
                  <input
                    type="text"
                    placeholder="Image URL"
                    className="form-input"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                  />
                  {error && <p className="error-message">{error}</p>}
                  <button type="submit" className="submit-button">
                    <PlusCircle className="icon" />
                    Add Case
                  </button>
                </form>
                <h2 className="list-title">Case List</h2>
                <div className="case-grid">
                  {filteredCases.length === 0 ? (
                    <p className="no-cases">No cases found.</p>
                  ) : (
                    filteredCases.map((caseItem, index) => (
                      <motion.div
                        key={index}
                        className="case-card"
                        whileHover={{ scale: 1.05 }}
                        onClick={() => setSelectedCase(caseItem)}
                      >
                        <img
                          src={caseItem.imageUrl}
                          alt="Case"
                          className="card-image"
                        />
                        <h3 className="card-title">{caseItem.title}</h3>
                        <p className="card-description">
                          {caseItem.description}
                        </p>
                      </motion.div>
                    ))
                  )}
                </div>
              </>
            )}
          </>
        ) : (
          // RAG System UI
          <div className="rag-system-container">
            <h2>RAG System Interface</h2>
            <div>
              <label htmlFor="fileUpload">Upload Document (TXT or PDF):</label>
              <input
                type="file"
                id="fileUpload"
                accept=".txt, .pdf"
                onChange={handleFileChange}
              />
              {ragFileName && <p>Selected File: {ragFileName}</p>}
              <button onClick={handleProcessDocument}>Process Document</button>
            </div>
            {documentSummary && (
              <div>
                <h3>Document Summary and Key Points:</h3>
                <textarea
                  readOnly
                  value={documentSummary}
                  style={{ width: "100%", height: "120px" }}
                ></textarea>
              </div>
            )}
            <div style={{ marginTop: "20px" }}>
              <label htmlFor="legalQuery">Enter your legal query:</label>
              <textarea
                id="legalQuery"
                value={legalQuery}
                onChange={(e) => setLegalQuery(e.target.value)}
                placeholder="Type your legal query here..."
                style={{ width: "100%", height: "80px" }}
              ></textarea>
              <button onClick={handleGenerateResponse}>
                Generate Legal Response
              </button>
            </div>
            {aiResponse && (
              <div style={{ marginTop: "20px" }}>
                <h3>AI Legal Response:</h3>
                <textarea
                  readOnly
                  value={aiResponse}
                  style={{ width: "100%", height: "150px" }}
                ></textarea>
              </div>
            )}
            {ragError && <p className="error-message">{ragError}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
