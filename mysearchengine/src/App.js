import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Results from "./components/Results";
import Logo from "./components/Logo";

function App() {
  const [query, setQuery] = useState("");
  const [llmAnswer, setLlmAnswer] = useState("");
  const [topResults, setTopResults] = useState([]);
  const [allResults, setAllResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery);
    setLoading(true);
    setErrorMsg("");
    setTopResults([]);
    setAllResults([]);
    setLlmAnswer("");

    try {
        const res = await fetch("http://127.0.0.1:8000/", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
      const data = await res.json();

      setTopResults(data.documents || []);
      setAllResults(data.all_documents || []);
      setLlmAnswer(data.llm_answer || "");
      setLoading(false);
    } catch (err) {
      setErrorMsg("Failed to submit query. Check backend logs.");
      setLoading(false);
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <Logo />
      <div className="w-full max-w-2xl mt-6">
        <SearchBar onSearch={handleSearch} />
      </div>

      {query && (
        <div className="mt-4 text-center text-gray-600">
          Showing results for: <b>{query}</b>
        </div>
      )}

      {loading && (
        <div className="mt-4 text-center text-blue-600 font-semibold">
          Loading results...
        </div>
      )}

      {errorMsg && !loading && (
        <div className="mt-4 text-center text-red-600 font-semibold">
          {errorMsg}
        </div>
      )}

      {llmAnswer && !loading && !errorMsg && (
        <div className="mt-6 w-full max-w-2xl bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-2">LLM Answer:</h2>
          <p className="italic text-gray-700">{llmAnswer}</p>
        </div>
      )}

      {!loading && !errorMsg && topResults.length > 0 && (
        <div className="mt-6 w-full max-w-2xl">
          <Results results={topResults} title="Top 3 Results" />
          <Results results={allResults} title="All Results" />
        </div>
      )}
    </div>
  );
}

export default App;
