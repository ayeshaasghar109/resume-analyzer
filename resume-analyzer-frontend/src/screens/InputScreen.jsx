import { useState } from "react";
import FileUpload from "../components/FileUpload.jsx";
import JobDescriptionInput from "../components/JobDescriptionInput.jsx";
import Footer from "../components/Footer.jsx";
import "./InputScreen.css";

export default function InputScreen({ onAnalyze, isAnalyzing, error }) {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");

  const canAnalyze = Boolean(file) && jobDescription.trim().length > 0 && !isAnalyzing;

  return (
    <div className="input-screen">
      <header className="masthead">
        <span className="label">Candidate / job analysis system</span>
        <h1 className="masthead__title">
          Resume
          <br />
          Analyzer
        </h1>
      </header>
      <hr className="rule" />

      <div className="input-screen__grid">
        <section className="input-screen__col input-screen__col--narrow">
          <FileUpload
            file={file}
            status={file ? "ready" : "idle"}
            onFileSelect={setFile}
            onRemove={() => setFile(null)}
          />
        </section>
        <div className="input-screen__divider" aria-hidden="true" />
        <section className="input-screen__col input-screen__col--wide">
          <JobDescriptionInput value={jobDescription} onChange={setJobDescription} />
        </section>
      </div>

      <hr className="rule" />

      <div className="analyze-bar">
        <p className="analyze-bar__status">
          Comparison covers matched and missing skills, experience type, experience duration,
          and stated requirement satisfaction.
        </p>
        <button
          type="button"
          className="analyze-bar__button"
          disabled={!canAnalyze}
          onClick={() => onAnalyze({ file, jobDescription })}
        >
          {isAnalyzing ? "Analyzing…" : "Analyze resume"}
        </button>
      </div>
      {error && <p className="analyze-bar__error">{error}</p>}
      <Footer />
    </div>
  );
}
