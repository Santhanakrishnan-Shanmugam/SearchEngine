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
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Function to handle search submission
  const handleSearch = async (searchQuery) => {
    try {
      setLoading(true);
      setHasSearched(true);
      setQuery(searchQuery);
      setErrorMsg("");

      // Step 1: Submit query to backend
      const res = await fetch("https://searchengine-lqza.onrender.com/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);

      const data = await res.json();
      const jobId = data.job_id;
      console.log("Job submitted, ID:", jobId);

      // Step 2: Poll backend for job result
      const pollResult = async () => {
        try {
          const resultRes = await fetch(
            `https://searchengine-lqza.onrender.com/result/${jobId}`
          );
          const resultData = await resultRes.json();

          if (resultData.status === "completed") {
            // Update UI with results
            setTopResults(resultData.result.documents || []);
            setAllResults(resultData.result.all_documents || []);
            setLlmAnswer(resultData.result.llm_answer || "");
            setLoading(false);
          } else if (resultData.status === "failed") {
            // Show error if job failed
            setErrorMsg("Job failed: " + resultData.error);
            setLoading(false);
          } else {
            // Job still running, poll again in 3 seconds
            setTimeout(pollResult, 3000);
          }
        } catch (error) {
          console.error("Error polling job:", error);
          setErrorMsg("Error polling job. Check backend logs.");
          setLoading(false);
        }
      };

      pollResult();
    } catch (error) {
      console.error("Error submitting query:", error);
      setErrorMsg("Something went wrong. Check backend logs.");
      setLoading(false);
    }
  };

  return (
    <div className="app-container px-4 py-6">
      <Logo />

      {/* Search bar component */}
      <SearchBar onSearch={handleSearch} />

      {/* Query display */}
      {query && (
        <div className="mt-4 text-center text-gray-600">
          Showing results for: <b>{query}</b>
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="mt-4 text-center text-blue-600 font-semibold">
          Loading results...
        </div>
      )}

      {/* Error message */}
      {errorMsg && !loading && (
        <div className="mt-4 text-center text-red-600 font-semibold">
          {errorMsg}
        </div>
      )}

      {/* LLM answer */}
      {llmAnswer && !loading && !errorMsg && (
        <div className="mt-4 text-center text-lg italic">{llmAnswer}</div>
      )}

      {/* Results */}
      {hasSearched && !loading && !errorMsg && (
        <>
          <Results results={topResults} title="Top 3 Results" />
          <Results results={allResults} title="All Results" />
        </>
      )}
    </div>
  );
}

export default App;
