import { color, font } from "../../theme";

// Une seule valeur, sa provenance en clair. Pas de metrique inventee :
// tout ce qui s'affiche ici est derive de GET /phishing/submissions.
export default function StatCard({ label, value, hint, tone }) {
  return (
    <div style={{ flex: 1, minWidth: 150, background: color.card, border: `1px solid ${color.border}`, padding: 18, display: "flex", flexDirection: "column", gap: 12 }}>
      <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: "0.1em", color: color.muted }}>{label}</span>
      <div style={{ display: "flex", alignItems: "baseline", gap: 9 }}>
        <span style={{ fontSize: 34, fontWeight: 700, letterSpacing: "-0.035em", lineHeight: 1, color: tone ? tone.fg : color.text }}>{value}</span>
        {hint && <span style={{ fontSize: 12.5, color: color.muted }}>{hint}</span>}
      </div>
    </div>
  );
}
