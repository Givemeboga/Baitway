import { color, font } from "../../theme";
import Button from "./Button";

// Aucun ecran ne doit rester blanc pendant une requete.

export function Skeleton({ widths = ["72%", "54%", "88%", "40%"] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
      {widths.map((w, i) => <div key={i} style={{ height: 9, width: w, background: color.divider }} />)}
    </div>
  );
}

export function LoadingState({ label = "Loading…", hint }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, padding: 4 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ width: 11, height: 11, border: `2px solid ${color.accent}`, borderRightColor: "transparent", display: "inline-block" }} />
        <span style={{ fontSize: 13.5, color: color.text }}>{label}</span>
      </div>
      <Skeleton />
      {hint && <span style={{ fontSize: 12, color: color.muted }}>{hint}</span>}
    </div>
  );
}

export function EmptyState({ title, message, action }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 13, textAlign: "center", padding: "34px 18px" }}>
      <div style={{ width: 34, height: 34, border: `1px solid ${color.border}` }} />
      <span style={{ fontSize: 14, color: color.text }}>{title}</span>
      {message && <span style={{ fontSize: 12.5, lineHeight: 1.5, color: color.muted, maxWidth: 280 }}>{message}</span>}
      {action}
    </div>
  );
}

// error : objet renvoye par normalizeError({ status, code, message })
export function ErrorState({ error, onRetry, tone }) {
  const fg = tone?.fg || "#EF4444";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        <span style={{ width: 8, height: 8, background: fg, flex: "none" }} />
        <span style={{ fontSize: 13.5, color: color.text }}>{error.message}</span>
      </div>
      <div style={{ background: color.bg, border: `1px solid ${color.border}`, padding: 12, fontFamily: font.mono, fontSize: 11, lineHeight: 1.65, color: color.muted }}>
        <div>status : <span style={{ color: fg }}>{error.status || "—"}</span></div>
        <div>code : <span style={{ color: color.text }}>{error.code}</span></div>
      </div>
      {onRetry && <Button variant="primary" onClick={onRetry} style={{ alignSelf: "flex-start" }}>Retry</Button>}
    </div>
  );
}
