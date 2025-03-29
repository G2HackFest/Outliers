import { useState } from "react";
import axios from "axios";

const RagSystem = () => {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const handleFileUpload = async () => {
    if (!file) return alert("Please upload a file.");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:5001/upload", formData);
      setSummary(res.data.summary);
    } catch (err) {
      console.error("Error uploading file:", err);
    }
  };

  const handleQuerySubmit = async () => {
    if (!query || !summary) return alert("Please provide a query and upload a file first.");
    try {
      const res = await axios.post("http://127.0.0.1:5001/query", { query, summary });
      setResponse(res.data.response);
    } catch (err) {
      console.error("Error generating response:", err);
    }
  };

  return (
    <div className="rag-system-container">
      <h2>RAG System</h2>
      <div>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleFileUpload}>Upload and Summarize</button>
      </div>
      {summary && (
        <div>
          <h3>Document Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
      <div>
        <textarea
          placeholder="Enter your legal query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        ></textarea>
        <button onClick={handleQuerySubmit}>Generate Response</button>
      </div>
      {response && (
        <div>
          <h3>AI Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default RagSystem;
