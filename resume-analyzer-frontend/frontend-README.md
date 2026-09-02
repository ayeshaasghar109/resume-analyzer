# Resume Analyzer — Frontend

An editorial, analyst-workspace UI for the Resume Analyzer FastAPI backend.
Built with React + Vite, plain CSS custom properties (no CSS framework, no
component-kit look), and mock data so the whole flow is reviewable before
`/analyze` is deployed.

## Run it

```bash
npm install
npm run dev
```

Opens on the input screen. Attach any PDF and paste a job description,
then hit **Analyze resume** — it runs against `src/data/mockAnalysis.js`
by default (a 900ms delay simulates a real request).

## Wiring up the real backend

1. Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to your FastAPI host.
2. Set `VITE_USE_MOCK=false`.

The frontend is already matched to the real `/analyze` response shape,
confirmed directly against `main.py`:

```json
{
  "overall_score": 71.4,
  "analysis": [
    {
      "job_skill": { "skill": "Python", "importance": "required", "min_years": 2, "experience_type": "work" },
      "resume_skill": "Python",
      "matching_score": 1.0,
      "category": "Very Strong",
      "experience_months": 18,
      "requirement_satisfaction": "Yes"
    }
  ],
  "skill_breakdown": {
    "required_skills": { "total": 4, "matched": 3, "missing": 1 },
    "preferred_skills": { "total": 3, "matched": 1, "missing": 2 },
    "unspecified_skills": { "total": 1, "matched": 0, "missing": 1 }
  },
  "summary": {
    "matched_skills": [],
    "required_missing_skills": [],
    "preferred_missing_skills": [],
    "missing_skills": [],
    "related_skills": []
  }
}
```

Notes on things that are easy to assume wrong here:

- `category` is `Very Strong` / `Strong` / `Partial` / `Somewhat Related` / `Missing`,
  computed by the backend — the frontend displays this directly rather than
  recomputing a label from `matching_score`.
- `summary.matched_skills` only includes `Very Strong` / `Strong` / `Partial`
  entries. `Somewhat Related` entries land in `summary.related_skills` instead —
  the frontend doesn't currently render this field anywhere (a gap, not a bug).
- `overall_score` can be `null` (when the job description has no required or
  preferred skills to weight a score from). `ScoreDisplay` handles this —
  it renders `—` instead of crashing or animating toward `NaN`.
- There's no per-project `evidence` array with start/end dates — the backend
  only returns a total `experience_months` per skill. `ExperienceTimeline`
  reflects this: it draws a candidate-months-vs-required-months comparison
  bar per matched skill, not a calendar timeline. If the backend later adds
  per-project date evidence, that component would need a rebuild to show a
  real timeline.

All network calls live in `src/api/resumeAnalyzerService.js` — no component
calls `fetch` directly, so this is the file to touch if the backend's field
names ever change. The form fields it sends are `file` (the PDF) and
`job_description` (text), matching `main.py`'s `/analyze` signature exactly.

## Structure

```
src/
  api/            API layer (isolated from UI)
  components/     FileUpload, JobDescriptionInput, ScoreDisplay,
                  SkillAnalysis, SkillRow, ExperienceTimeline (months-
                  comparison, not calendar-based — see notes above),
                  SkillGapList, SummarySection, Footer
  screens/        InputScreen, ResultsScreen (compose the components)
  data/           mockAnalysis.js — placeholder /analyze response,
                  matched to the real backend shape above
  tokens.css      design system: color, type, spacing custom properties
```

## Design notes

- Palette: warm paper background, near-black ink, one functional accent
  (deep pine-ink `#1f4a44`) used for interaction states only. Green/red/amber
  are reserved for match status, per the brief.
- Type: **Fraunces** (editorial serif) for headings and the analysis
  summary; **Work Sans** for interface text; **IBM Plex Mono** for all
  numeric/technical data — scores, percentages, dates, labels — so numbers
  read as data rather than decoration.
- The overall score uses a large serif numeral with a segmented horizontal
  scale, not a circular progress ring.
- "Skill Analysis" and "Matched Skills" from the brief are the same
  component (`SkillAnalysis` / `SkillRow`): each row already carries
  skill, importance, match, experience, and requirement columns, and
  expands for full detail — a second, separate flat table would just
  repeat the same data in a different shape, so it stays as one component.

## Known gap

`summary.related_skills` (the backend's `Somewhat Related` category) isn't
displayed anywhere in the UI yet. Not a bug — just unbuilt. Worth a small
section if it turns out to matter to real users.
