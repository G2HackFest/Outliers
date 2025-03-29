const CaseList = ({ cases }) => {
    return (
      <div>
        <h2>All Cases</h2>
        <ul>
          {cases.map((caseItem, index) => (
            <li key={index}>
              <strong>{caseItem.title}</strong> - {caseItem.description}
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  export default CaseList;
  