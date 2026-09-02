import "./ExperienceTimeline.css";

// Your backend returns a total experience_months per skill, not per-project
// date ranges — so this renders a candidate-vs-required months comparison
// per matched skill rather than a calendar timeline. If your backend later
// adds per-project evidence (project name + start/end dates), this can be
// rebuilt as a true Gantt-style timeline.

export default function ExperienceTimeline({ entries }) {
  const withExperience = entries.filter((e) => e.experience_months > 0);
  if (withExperience.length === 0) return null;

  const maxMonths = Math.max(
    ...withExperience.map((e) => Math.max(e.experience_months, e.job_skill.min_years * 12))
  );

  return (
    <section className="timeline">
      <div className="timeline__head">
        <span className="label">Experience evidence</span>
        <span className="timeline__hint">Candidate months against required months</span>
      </div>

      <div className="timeline__rows">
        {withExperience.map((entry, i) => {
          const requiredMonths = Math.round(entry.job_skill.min_years * 12);
          const candidatePct = (entry.experience_months / maxMonths) * 100;
          const requiredPct = (requiredMonths / maxMonths) * 100;
          return (
            <div className="timeline__row" key={entry.job_skill.skill}>
              <span className="timeline__row-label">{entry.job_skill.skill}</span>
              <div className="timeline__track">
                <div
                  className="timeline__bar"
                  style={{ width: `${candidatePct}%`, animationDelay: `${i * 90}ms` }}
                >
                  <span className="timeline__bar-value numeral">{entry.experience_months} mo</span>
                </div>
                <div className="timeline__required-marker" style={{ left: `${requiredPct}%` }}>
                  <span className="timeline__required-label numeral">req {requiredMonths} mo</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
