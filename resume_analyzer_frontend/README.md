# Resume Analyzer — Flutter Web Frontend

## 1. Backend: add CORS (required)

A browser blocks cross-origin requests by default. Your Flutter web app
will run on a different port than uvicorn, so without this every request
fails silently with a CORS error in the browser console — not a
Python-side error, so it won't show up in your backend logs.

Add this to `main.py`, right after `app = FastAPI()`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying anywhere public
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Run the backend as usual:
```
uvicorn main:app --reload
```

## 2. Frontend: set up the Flutter project

You already have Flutter installed. From this folder:

```
flutter pub get
flutter run -d chrome
```

If `flutter run -d chrome` doesn't find a Chrome device, run
`flutter config --enable-web` once, then retry.

## 3. Point it at your backend

`lib/services/api_service.dart` hardcodes `baseUrl` to
`http://127.0.0.1:8000`. That's correct for local dev against
`uvicorn main:app --reload`. Change it when you deploy either side
elsewhere.

## What's built

- **Resumes list** (`resume_list_screen.dart`) — GET /resumes, delete,
  tap to edit, + to add.
- **Add/Edit form** (`resume_form_screen.dart`) — POST/PUT /resumes.
- **Analyze flow** (`analyze_screen.dart` → `analyze_result_screen.dart`) —
  pick a PDF, paste a job description, POST /analyze (multipart), then
  shows overall score, the required/preferred/unspecified breakdown, and
  a per-skill list color-coded by category.

## Known rough edges (backend-side, not fixed here)

- `GET /resumes` / `GET /resumes/{id}` return raw arrays
  (`[id, name, email]`) instead of objects — `Resume.fromRow` parses
  them positionally. Fragile if the column order ever changes.
- `POST /resumes` doesn't return the created row, so the app refetches
  the whole list after creating one instead of inserting locally.
