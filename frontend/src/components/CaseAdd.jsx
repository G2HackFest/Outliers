import { useState } from "react";
import { addCase, getCases } from "../api";

const CaseAdd = ({ setCases }) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [judgment, setJudgment] = useState("");

  const handleAddCase = async () => {
    await addCase({ title, description, judgment });
    const updatedCases = await getCases();
    setCases(updatedCases);
    setTitle("");
    setDescription("");
    
  };

  return (
    <div>
      <h2>Add a New Case</h2>
      <input
        type="text"
        placeholder="Case Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        type="text"
        placeholder="Case Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      
      <button onClick={handleAddCase}>Add Case</button>
    </div>
  );
};

export default CaseAdd;
