import { font } from "../../theme";
import { toneForVerdict, toneForSeverity, toneForStatus } from "../../lib/verdict";

const RESOLVERS = { verdict: toneForVerdict, severity: toneForSeverity, status: toneForStatus };

// kind: "verdict" (clean|suspicious|malicious) | "severity" (low|medium|high) | "status"
// dot=true ajoute un carre de couleur pour que la severite se lise sans lire le mot.
export default function SeverityBadge({ kind = "verdict", value, dot = true, style }) {
  const tone = RESOLVERS[kind](value);
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, ...style }}>
      {dot && <span style={{ width: 7, height: 7, background: tone.fg, flex: "none" }} />}
      <span style={{ fontFamily: font.mono, fontSize: 11, color: tone.fg }}>{value ?? "unknown"}</span>
    </span>
  );
}
