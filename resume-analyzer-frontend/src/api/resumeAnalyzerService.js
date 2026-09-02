// Dedicated API layer for the Resume Analyzer FastAPI backend.
// UI components never call fetch() directly — they call functions exported here.
// Swap BASE_URL / endpoint paths once the backend is deployed.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let details = null;
    try {
      details = await response.json();
    } catch {
      // response body wasn't JSON — ignore
    }
    throw new ApiError(
      details?.detail || `Request failed with status ${response.status}`,
      response.status,
      details
    );
  }
  return response.json();
}


export async function analyzeResume({ file, jobDescription, signal }) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
    signal,
  });

  return handleResponse(response);
}

export { ApiError };
