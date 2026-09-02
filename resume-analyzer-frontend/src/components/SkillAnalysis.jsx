import SkillRow from "./SkillRow.jsx";
import "./SkillAnalysis.css";

export default function SkillAnalysis({ entries }) {
  return (
    <section className="skill-analysis">
      <div className="skill-analysis__head">
        <span className="label">Matched skills</span>
        <span className="skill-analysis__count numeral">{entries.length} skills matched</span>
      </div>

      <div className="skill-analysis__columns label" aria-hidden="true">
        <span>Skill</span>
        <span>Match</span>
        <span>Experience</span>
        <span>Requirement</span>
        <span />
      </div>
      <hr className="rule" />

      {entries.length === 0 ? (
        <p className="skill-analysis__empty">No skills matched between this resume and job description.</p>
      ) : (
        <div className="skill-analysis__list">
          {entries.map((entry, index) => (
            <SkillRow entry={entry} index={index} key={entry.job_skill.skill} />
          ))}
        </div>
      )}
    </section>
  );
}
