import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Results from "./components/Results";
import Logo from "./components/Logo";

function App() {
  const [topResults, setTopResults] = useState([]);
  const [allResults, setAllResults] = useState([]);
  const [llmAnswer, setLlmAnswer] = useState("");
  const [query, setQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (searchQuery) => {
    try {
      const response = await fetch("http:3.110.124.2:8000/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }), 
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Backend response:", data);

      setQuery(data.query || searchQuery);
      setTopResults(data.documents || []);
      setAllResults(data.all_documents || []);
      setLlmAnswer(data.llm_answer || "");
      setHasSearched(true);
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("Something went wrong. Check backend logs or Nginx config.");
    }
  };

  return (
    <div>
      <div className="app-container">
        <Logo />
      </div>

      {/* Pass search handler to SearchBar */}
      <SearchBar onSearch={handleSearch} />

      {query && (
        <div className="mt-4 text-center text-gray-600">
          Showing results for: <b>{query}</b>
        </div>
      )}

      {llmAnswer && (
        <div className="mt-4 text-center text-lg italic">{llmAnswer}</div>
      )}

      {hasSearched && (
        <>
          <Results results={topResults} title="Top 3 Results" />
          <Results results={allResults} title="All Results" />
        </>
      )}
    </div>
  );
}

export default App;
