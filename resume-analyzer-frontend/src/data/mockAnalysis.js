// Placeholder response shaped to match the REAL FastAPI /analyze payload,
// confirmed from a live response on 2026-09-01. Kept for local UI preview
// with VITE_USE_MOCK=true. This example includes some matched skills (your
// live test run had none matched) so the matched-skills views are visible
// during preview.

function skillEntry({
  skill,
  importance,
  minYears,
  experienceType = "work",
  category,
  matchingScore = 0,
  experienceMonths = 0,
  resumeSkill = null,
}) {
  return {
    category,
    experience_months: experienceMonths,
    job_skill: {
      experience_type: experienceType,
      importance,
      min_years: minYears,
      skill,
    },
    matching_score: matchingScore,
    requirement_satisfaction: category === "Matched" ? "Yes" : "No",
    resume_skill: resumeSkill,
  };
}

const flutter = skillEntry({
  skill: "Flutter",
  importance: "required",
  minYears: 1,
  category: "Matched",
  matchingScore: 0.94,
  experienceMonths: 14,
  resumeSkill: "Flutter",
});

const restApi = skillEntry({
  skill: "REST API integration",
  importance: "required",
  minYears: 0.5,
  category: "Matched",
  matchingScore: 0.85,
  experienceMonths: 18,
  resumeSkill: "Flask / FastAPI REST APIs",
});

const sqlite = skillEntry({
  skill: "SQLite or relational databases",
  importance: "required",
  minYears: 0.5,
  category: "Matched",
  matchingScore: 0.88,
  experienceMonths: 16,
  resumeSkill: "SQLite",
});

const stateManagement = skillEntry({
  skill: "State management",
  importance: "preferred",
  minYears: 1,
  category: "Matched",
  matchingScore: 0.68,
  experienceMonths: 14,
  resumeSkill: "Provider / setState patterns",
});

const machineLearning = skillEntry({
  skill: "Machine Learning",
  importance: "preferred",
  minYears: 1,
});

const nlp = skillEntry({
  skill: "Natural Language Processing",
  importance: "preferred",
  minYears: 1,
});

const cicd = skillEntry({
  skill: "CI/CD pipelines",
  importance: "preferred",
  minYears: 0.5,
});

const dockerReq = skillEntry({
  skill: "Docker",
  importance: "required",
  minYears: 1,
});

const analysis = [flutter, restApi, sqlite, stateManagement, machineLearning, nlp, cicd, dockerReq];

const matched = analysis.filter((s) => s.category === "Matched");
const missing = analysis.filter((s) => s.category === "Missing");
const requiredMissing = missing.filter((s) => s.job_skill.importance === "required");
const preferredMissing = missing.filter((s) => s.job_skill.importance === "preferred");

export const mockAnalysis = {
  overall_score: 71.4,
  analysis,
  skill_breakdown: {
    required_skills: { total: 4, matched: 3, missing: 1 },
    preferred_skills: { total: 3, matched: 1, missing: 2 },
    unspecified_skills: { total: 1, matched: 0, missing: 1 },
  },
  summary: {
    matched_skills: matched,
    missing_skills: missing,
    required_missing_skills: requiredMissing,
    preferred_missing_skills: preferredMissing,
    related_skills: [],
  },
};
