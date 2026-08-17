import { severity } from "../theme";

// Echelle commune aux deux modules (docs/api-contract.md section 1) :
// clean 0-30, suspicious 31-70, malicious 71-100.
export function verdictFromScore(score) {
  if (score <= 30) return "clean";
  if (score <= 70) return "suspicious";
  return "malicious";
}

// verdict du contrat -> jeton de severite visuel
const VERDICT_TONE = {
  clean: "safe",
  suspicious: "high",
  malicious: "critical",
  unknown: "unknown",
};

// severite d'indicateur du contrat -> jeton de severite visuel
const SEVERITY_TONE = {
  low: "unknown",
  medium: "medium",
  high: "high",
};

export function toneForVerdict(verdict) {
  return severity[VERDICT_TONE[verdict] || "unknown"];
}

export function toneForSeverity(level) {
  return severity[SEVERITY_TONE[level] || "unknown"];
}

// Statut analyste (pending | reviewed | resolved)
export function toneForStatus(status) {
  if (status === "resolved") return severity.safe;
  if (status === "pending") return severity.high;
  return severity.unknown;
}

export const INDICATOR_TYPES = ["ip", "domain", "url", "hash"];

export function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}
