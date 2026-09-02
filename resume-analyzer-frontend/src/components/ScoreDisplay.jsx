import { useEffect, useRef, useState } from "react";
import "./ScoreDisplay.css";

function useCountUp(target, durationMs = 900) {
  const [value, setValue] = useState(0);
  const frame = useRef(null);

  useEffect(() => {
    if (target == null) return;
    const start = performance.now();
    const from = 0;

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / durationMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(from + (target - from) * eased);
      if (progress < 1) {
        frame.current = requestAnimationFrame(tick);
      }
    }

    frame.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame.current);
  }, [target, durationMs]);

  return value;
}

export default function ScoreDisplay({ score, skillBreakdown }) {
  const hasScore = typeof score === "number";
  const animated = useCountUp(hasScore ? score : 0);
  const marker = hasScore ? Math.min(Math.max(score, 0), 100) : 0;

  const rows = [
    { key: "required", label: "Required", ...skillBreakdown.required_skills },
    { key: "preferred", label: "Preferred", ...skillBreakdown.preferred_skills },
    { key: "other", label: "Other", ...skillBreakdown.unspecified_skills },
  ];

  return (
    <div className="score">
      <div className="score__primary">
        <div className="score__figure numeral">{hasScore ? animated.toFixed(1) : "—"}</div>
        <div className="score__label label">
          {hasScore ? "Overall match" : "No required or preferred skills to score"}
        </div>
      </div>

      <div className="score__scale-block">
        <div
          className="score__scale"
          role="img"
          aria-label={hasScore ? `Overall match ${score} of 100` : "No score available"}
        >
          <div className="score__scale-fill" style={{ width: `${marker}%` }} />
          {hasScore && <div className="score__scale-marker" style={{ left: `${marker}%` }} />}
          <div className="score__scale-ticks">
            {[0, 25, 50, 75, 100].map((tick) => (
              <span key={tick} className="score__tick numeral">
                {tick}
              </span>
            ))}
          </div>
        </div>

        <dl className="score__breakdown">
          {rows.map((row) => (
            <div className="score__breakdown-row" key={row.key}>
              <dt className="label">{row.label}</dt>
              <dd className="numeral">
                {row.matched} / {row.total}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}