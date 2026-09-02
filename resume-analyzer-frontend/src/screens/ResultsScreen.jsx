import ScoreDisplay from "../components/ScoreDisplay.jsx";
import SummarySection from "../components/SummarySection.jsx";
import SkillAnalysis from "../components/SkillAnalysis.jsx";
import ExperienceTimeline from "../components/ExperienceTimeline.jsx";
import SkillGapList from "../components/SkillGapList.jsx";
import Footer from "../components/Footer.jsx";
import "./ResultsScreen.css";

export default function ResultsScreen({ result, fileName, onStartOver }) {
  const { overall_score: overallScore, skill_breakdown: skillBreakdown, summary } = result;
  const {
    matched_skills: matchedSkills,
    required_missing_skills: requiredMissingSkills,
    preferred_missing_skills: preferredMissingSkills,
  } = summary;

  const totalSkills =
    skillBreakdown.required_skills.total +
    skillBreakdown.preferred_skills.total +
    skillBreakdown.unspecified_skills.total;
  const totalMatched =
    skillBreakdown.required_skills.matched +
    skillBreakdown.preferred_skills.matched +
    skillBreakdown.unspecified_skills.matched;

  return (
    <div className="results-screen">
      <header className="results-masthead">
        <div>
          <span className="label">Candidate analysis</span>
          <h1 className="results-masthead__title">Job match report</h1>
        </div>
        <div className="results-masthead__meta">
          <span className="results-masthead__file numeral">{fileName}</span>
          <button type="button" className="results-masthead__reset" onClick={onStartOver}>
            New analysis
          </button>
        </div>
      </header>
      <hr className="rule" />

      <ScoreDisplay score={overallScore} skillBreakdown={skillBreakdown} />
      <hr className="rule" />

      <SummarySection matchedCount={totalMatched} totalCount={totalSkills} />
      <hr className="rule" />

      <SkillAnalysis entries={matchedSkills} />
      <hr className="rule" />

      <ExperienceTimeline entries={matchedSkills} />
      <hr className="rule" />

      <SkillGapList requiredGaps={requiredMissingSkills} preferredGaps={preferredMissingSkills} />
      <Footer />
    </div>
  );
}
