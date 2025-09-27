import React from "react";

const Results = ({ results, title }) => {
  const safeResults = results || [];

  return (
    <div className="mt-8 px-10">
      {title && <h2 className="text-xl font-bold mb-4">{title}</h2>}
      {safeResults.length === 0 ? (
        <p className="text-gray-500">No results yet</p>
      ) : (
        safeResults.map((item, index) => (
          <div
            key={index}
            className="mb-6 p-4 border rounded shadow hover:bg-gray-50 transition"
          >
            <a
              href={item.url || item.Url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 font-semibold text-lg"
            >
              {item.title || item.Title || "No Title"}
            </a>
            <p className="text-gray-700 mt-2">{item.content}</p>
            <p className="text-sm text-gray-500 mt-1">{item.url || item.Url}</p>
          </div>
        ))
      )}
    </div>
  );
};

export default Results;
