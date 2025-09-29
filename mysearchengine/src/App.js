import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Results from "./components/Results";
import Logo from "./components/Logo";

function App() {
  const [topResults, setTopResults] = useState([]);    // top 3
  const [allResults, setAllResults] = useState([]);    // all 10
  const [llmAnswer, setLlmAnswer] = useState("");
  const [query, setQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false); // track if search happened

  const handleSearch = async (query) => {
    try {
      const response = await fetch("http://3.110.124.2:8080/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      console.log("Backend response:", data);

      setQuery(data.query || query);
      setTopResults(data.documents || []);          // top 3
      setAllResults(data.all_documents || []);     // all 10
      setLlmAnswer(data.llm_answer || "");
      setHasSearched(true);                         // mark search done
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <div>
      <div className="app-container">
       <Logo />
      </div>
      <SearchBar onSearch={handleSearch} />

      {query && (
        <div className="mt-4 text-center text-gray-600">
          Showing results for: <b>{query}</b>
        </div>
      )}

      {llmAnswer && (
        <div className="mt-4 text-center text-lg italic">{llmAnswer}</div>
      )}

      {/* Only show results after a search */}
      {hasSearched && (
        <>
          {/* Top 3 Results */}
          <Results results={topResults} title="Top 3 Results" />

          {/* All 10 Results */}
          <Results results={allResults} title="All Results" />
        </>
      )}
    </div>
  );
}

export default App;
