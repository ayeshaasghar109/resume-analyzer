import "./SkillGapList.css";

function GapColumn({ title, gaps, tone }) {
  return (
    <div className="gap-col">
      <div className={`gap-col__head gap-col__head--${tone}`}>
        <span className="label">{title}</span>
        <span className="numeral gap-col__count">{gaps.length}</span>
      </div>
      {gaps.length === 0 ? (
        <p className="gap-col__empty">No gaps detected.</p>
      ) : (
        <ol className="gap-col__list">
          {gaps.map((gap, i) => (
            <li className="gap-item" key={gap.job_skill.skill}>
              <span className="gap-item__index numeral">{String(i + 1).padStart(2, "0")}</span>
              <div className="gap-item__body">
                <span className="gap-item__name">{gap.job_skill.skill}</span>
                <span className="gap-item__note">
                  {gap.resume_skill ? `Closest resume skill: ${gap.resume_skill}` : "No matching experience found"}
                </span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default function SkillGapList({ requiredGaps, preferredGaps }) {
  return (
    <section className="skill-gaps">
      <div className="skill-gaps__head">
        <span className="label">Skill gaps</span>
      </div>
      <div className="skill-gaps__grid">
        <GapColumn title="Required gaps" gaps={requiredGaps} tone="negative" />
        <GapColumn title="Preferred gaps" gaps={preferredGaps} tone="neutral" />
      </div>
    </section>
  );
}
