# Resume Analyzer — Backend

A FastAPI service that compares a candidate's resume against a job description and
returns a structured skill-match report: which required/preferred skills are present,
how strong each match is, whether the candidate meets the stated experience
requirement per skill, and an overall weighted match score.

## How matching works

1. **Extraction** — the resume PDF and the job description text are each sent to an
   LLM (via Groq, model `openai/gpt-oss-120b`) with a structured JSON schema, pulling
   out skills, experience entries (with type — work vs. project — and date ranges),
   education, and certifications.
2. **Skill matching**, per job skill:
   - Exact normalized-string match against resume skills first.
   - If no exact match, semantic similarity via `sentence-transformers`
     (`all-MiniLM-L6-v2`) + cosine similarity against remaining unused resume skills.
   - Any semantic match is then verified by a second LLM call (`verify_skill`) that
     confirms the resume skill genuinely demonstrates the job skill — this filters out
     false positives from embedding similarity (e.g. "Python" incorrectly matching
     "Pandas").
   - Each match gets a `category`: `Very Strong` (≥0.90), `Strong` (≥0.75),
     `Partial` (≥0.60), `Somewhat Related` (≥0.45), or `Missing`.
3. **Experience verification** — for each matched skill, resume experience entries
   whose `domain` includes that skill are date-merged (overlapping ranges collapsed)
   and summed into total months, then compared against the job's stated
   `min_years * 12`.
4. **Scoring** — `overall_score` is a weighted average of per-skill matching scores:
   80% required-skill average + 20% preferred-skill average (×100). If only one
   category is present, its average alone is used. If neither required nor preferred
   skills exist, `overall_score` is `null`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root (never committed — see `.gitignore`):

```
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:

```bash
uvicorn main:app --reload
```

The API is live at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`.

## Endpoints

### `POST /analyze` — main endpoint

Multipart form data:
| Field | Type | Description |
|---|---|---|
| `file` | file (PDF) | Candidate's resume |
| `job_description` | text | Full job description text |

Response:

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

Notes:
- `matched_skills` includes entries with category `Very Strong`, `Strong`, or `Partial`.
- `related_skills` holds `Somewhat Related` matches — not counted as matched or missing.
- `overall_score` can be `null` if the job description has no required or preferred
  skills at all.

### `POST /upload_resume`

Parses a single resume PDF (no job description) and returns extracted skills,
experience, education, and certifications. Used standalone, separate from `/analyze`.

### `GET /`

Health check — returns `{"message": "API IS RUNNING NOW"}`.

### `/resumes` (GET, POST, PUT, DELETE `/resumes/{id}`)

Basic CRUD for a `resumes` table (`name`, `email`) in a local SQLite database
(`resume.db`, gitignored). Separate from the analysis flow — a simpler earlier feature
for storing contact records.

## Tech stack

FastAPI · pdfplumber (PDF text extraction) · sentence-transformers (semantic skill
matching) · scikit-learn (cosine similarity) · Groq (LLM extraction + verification) ·
SQLite

## Frontend

Pairs with a separate React/Vite frontend — see `resume-analyzer-frontend/`