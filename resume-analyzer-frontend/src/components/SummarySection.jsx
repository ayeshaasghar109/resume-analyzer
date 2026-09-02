import "./SummarySection.css";

// Your backend's `summary` field is a data grouping (matched_skills,
// missing_skills, etc.), not a narrative paragraph — so there's no
// human-readable analysis text to display here yet. This shows the
// matched/total ratio in plain language instead. If your backend later
// adds a text field (e.g. `narrative_summary`), swap it in here.

export default function SummarySection({ matchedCount, totalCount }) {
  return (
    <section className="summary">
      <div className="summary__head">
        <span className="label">Analysis</span>
      </div>
      <p className="summary__text">
        {matchedCount} of {totalCount} evaluated skills matched between this resume and the job
        description.
      </p>
    </section>
  );
}
