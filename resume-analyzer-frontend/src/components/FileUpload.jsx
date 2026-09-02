import { useCallback, useRef, useState } from "react";
import "./FileUpload.css";

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileUpload({ file, onFileSelect, onRemove, status = "idle" }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const selected = fileList?.[0];
      if (selected && selected.type === "application/pdf") {
        onFileSelect(selected);
      }
    },
    [onFileSelect]
  );

  return (
    <div className="upload">
      <div className="upload__head">
        <span className="label">Resume</span>
        <span className="upload__hint">PDF only</span>
      </div>

      {!file ? (
        <div
          className={`upload__intake ${isDragging ? "upload__intake--active" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
          }}
        >
          <div className="upload__marks" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
          </div>
          <p className="upload__instruction">
            Drop a resume file here, or <span className="upload__link">select a PDF</span>
          </p>
          <p className="upload__sub">Text will be extracted for skill and experience analysis.</p>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            className="upload__input"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      ) : (
        <div className="upload__file">
          <div className="upload__file-row">
            <div className="upload__file-meta">
              <span className="upload__file-name">{file.name}</span>
              <span className="upload__file-size numeral">{formatFileSize(file.size)}</span>
            </div>
            <button type="button" className="upload__remove" onClick={onRemove}>
              Remove
            </button>
          </div>
          <div className="upload__status-row">
            <span className={`upload__status upload__status--${status}`}>
              {status === "ready" && "File ready for analysis"}
              {status === "reading" && "Reading document…"}
              {status === "idle" && "File attached"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
