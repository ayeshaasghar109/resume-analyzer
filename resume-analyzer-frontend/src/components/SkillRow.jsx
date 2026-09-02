import { useState } from "react";
import "./SkillRow.css";

export default function SkillRow({ entry, index }) {
  const [open, setOpen] = useState(false);
  const { job_skill: jobSkill, resume_skill: resumeSkill, matching_score: matchingScore, category, experience_months: experienceMonths, requirement_satisfaction: requirementSatisfaction } = entry;
  const satisfied = requirementSatisfaction === "Yes";
  const requiredMonths = Math.round(jobSkill.min_years * 12);

  return (
    <div className="skill-row" style={{ animationDelay: `${Math.min(index, 8) * 45}ms` }}>
      <button
        type="button"
        className="skill-row__summary"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <div className="skill-row__name-block">
          <span className="skill-row__name">{jobSkill.skill}</span>
          <span className={`skill-row__importance label skill-row__importance--${jobSkill.importance}`}>
            {jobSkill.importance}
          </span>
        </div>

        <div className="skill-row__match">
          <span className="skill-row__match-strength">{category}</span>
          <span className="skill-row__match-pct numeral">
            {Math.round(matchingScore * 100)}%
          </span>
        </div>

        <div className="skill-row__exp numeral">
          {experienceMonths} / {requiredMonths} mo
        </div>

        <div className={`skill-row__status skill-row__status--${satisfied ? "positive" : "negative"}`}>
          {satisfied ? "Requirement satisfied" : "Not satisfied"}
        </div>

        <span className={`skill-row__chevron ${open ? "skill-row__chevron--open" : ""}`} aria-hidden="true">
          ▾
        </span>
      </button>

      <div className={`skill-row__detail ${open ? "skill-row__detail--open" : ""}`}>
        <div className="skill-row__detail-inner">
          <hr className="rule" />
          <dl className="skill-row__detail-grid">
            <div>
              <dt className="label">Resume skill</dt>
              <dd>{resumeSkill || "No match found"}</dd>
            </div>
            <div>
              <dt className="label">Experience</dt>
              <dd className="numeral">{experienceMonths} months</dd>
            </div>
            <div>
              <dt className="label">Required</dt>
              <dd className="numeral">{requiredMonths} months ({jobSkill.experience_type})</dd>
            </div>
            <div>
              <dt className="label">Requirement</dt>
              <dd>{satisfied ? "Satisfied" : "Not satisfied"}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}