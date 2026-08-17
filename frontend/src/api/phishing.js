import client from "./client";

// Enveloppes fines autour du client Axios existant — pas une seconde
// abstraction : juste les routes reelles de backend/app/routers/phishing.py.

export function analyzeEmail(rawEmail) {
  return client.post("/phishing/analyze", { raw_email: rawEmail }).then((r) => r.data);
}

export function listSubmissions() {
  return client.get("/phishing/submissions").then((r) => r.data.submissions);
}

export function getSubmission(id) {
  return client.get(`/phishing/submissions/${id}`).then((r) => r.data);
}

// Champs acceptes par SubmissionUpdate : verdict, status, notes (tous optionnels).
export function updateSubmission(id, patch) {
  return client.patch(`/phishing/submissions/${id}`, patch).then((r) => r.data);
}
