import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Results from "./components/Results";
import Logo from "./components/Logo";

function App() {
  const [topResults, setTopResults] = useState([]);
  const [allResults, setAllResults] = useState([]);
  const [llmAnswer, setLlmAnswer] = useState("");
  const [query, setQuery] = useState("");
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

      // Step 2: Poll backend for result
      const pollResult = async () => {
        try {
          const resultRes = await fetch(
            `https://searchengine-lqza.onrender.com/result/${jobId}`
          );
          const resultData = await resultRes.json();

          if (resultData.status === "completed") {
            setTopResults(resultData.result.documents || []);
            setAllResults(resultData.result.all_documents || []);
            setLlmAnswer(resultData.result.llm_answer || "");
            setLoading(false);
          } else if (resultData.status === "failed") {
            setErrorMsg("Job failed: " + resultData.error);
            setLoading(false);
          } else {
            // Still running, poll again in 2-3 seconds
            setTimeout(pollResult, 3000);
          }
        } catch (err) {
          console.error("Error polling job:", err);
          setErrorMsg("Error fetching results. Check backend logs.");
          setLoading(false);
        }
      };

      pollResult();
    } catch (err) {
      console.error("Error submitting query:", err);
      setErrorMsg("Failed to submit query. Check backend logs.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start px-4 py-10 bg-gray-50">
      {/* Logo */}
      <div className="mb-6">
        <Logo />
      </div>

      {/* Search bar */}
      <div className="w-full max-w-xl mb-6">
        <SearchBar onSearch={handleSearch} />
      </div>

      {/* Query display */}
      {query && (
        <div className="mt-2 text-center text-gray-600">
          Showing results for: <b>{query}</b>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="mt-4 text-center text-blue-600 font-semibold">
          Loading results...
        </div>
      )}

      {/* Error */}
      {errorMsg && !loading && (
        <div className="mt-4 text-center text-red-600 font-semibold">
          {errorMsg}
        </div>
      )}

      {/* LLM Answer */}
      {llmAnswer && !loading && !errorMsg && (
        <div className="mt-4 text-center text-lg italic">{llmAnswer}</div>
      )}

      {/* Results */}
      {!loading && !errorMsg && (topResults.length > 0 || allResults.length > 0) && (
        <div className="mt-6 w-full max-w-3xl">
          <Results results={topResults} title="Top 3 Results" />
          <Results results={allResults} title="All Results" />
        </div>
      )}
    </div>
  );
}

export default App;
