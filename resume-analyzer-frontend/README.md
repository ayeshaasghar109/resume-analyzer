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
3. Confirm the shape of your real `/analyze` response against the shape
   assumed in `src/data/mockAnalysis.js` and documented in
   `src/api/resumeAnalyzerService.js` — field names for the per-skill
   `evidence` array and `match_strength` string were inferred from the
   brief, not confirmed against a live payload. Adjust `ResultsScreen.jsx`'s
   destructuring if your backend's field names differ.

All network calls live in `src/api/resumeAnalyzerService.js` — no component
calls `fetch` directly, so this is the only file that needs to change.

## Structure

```
src/
  api/            API layer (isolated from UI)
  components/     FileUpload, JobDescriptionInput, ScoreDisplay,
                  SkillAnalysis, SkillRow, ExperienceTimeline,
                  SkillGapList, SummarySection
  screens/        InputScreen, ResultsScreen (compose the components)
  data/           mockAnalysis.js — placeholder /analyze response
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
  repeat the same data in a different shape.
