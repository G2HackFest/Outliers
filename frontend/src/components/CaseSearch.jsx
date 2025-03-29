import { useState } from "react";
import { searchCases } from "../api";

const CaseSearch = ({ setCases }) => {
  const [query, setQuery] = useState("");

  const handleSearch = async () => {
    const results = await searchCases(query);
    setCases(results);
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search cases..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
};

export default CaseSearch;
