import "./JobDescriptionInput.css";

export default function JobDescriptionInput({ value, onChange, maxLength = 6000 }) {
  return (
    <div className="jd">
      <div className="jd__head">
        <span className="label">Job description</span>
        <span className={`jd__count numeral ${value.length > maxLength ? "jd__count--over" : ""}`}>
          {value.length.toLocaleString()} / {maxLength.toLocaleString()}
        </span>
      </div>
      <textarea
        className="jd__field"
        placeholder="Paste the job description here — including required and preferred skills, and any stated experience requirements."
        value={value}
        maxLength={maxLength}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
      />
    </div>
  );
}
