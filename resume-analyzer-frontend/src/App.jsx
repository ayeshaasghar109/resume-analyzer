import { useState } from "react";
import InputScreen from "./screens/InputScreen.jsx";
import ResultsScreen from "./screens/ResultsScreen.jsx";
import { analyzeResume, ApiError } from "./api/resumeAnalyzerService.js";
import { mockAnalysis } from "./data/mockAnalysis.js";

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";

export default function App() {
  const [result, setResult] = useState(null);
  const [fileName, setFileName] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  async function handleAnalyze({ file, jobDescription }) {
    setIsAnalyzing(true);
    setError(null);
    try {
      const data = USE_MOCK
        ? await new Promise((resolve) => setTimeout(() => resolve(mockAnalysis), 900))
        : await analyzeResume({ file, jobDescription });
      setResult(data);
      setFileName(file.name);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Analysis failed. Check your connection and try again."
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  if (result) {
    return (
      <ResultsScreen
        result={result}
        fileName={fileName}
        onStartOver={() => {
          setResult(null);
          setError(null);
        }}
      />
    );
  }

  return <InputScreen onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} error={error} />;
}
