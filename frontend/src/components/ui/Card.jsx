import { color, font } from "../../theme";

// Carte standard : fond #11161D sur fond application #080A0D, jamais sans bordure
// (une carte ne doit pas se fondre dans l'arriere-plan).
export default function Card({ title, meta, actions, padded = true, children, style }) {
  return (
    <div style={{ background: color.card, border: `1px solid ${color.border}`, display: "flex", flexDirection: "column", ...style }}>
      {(title || actions) && (
        <div style={{ padding: "14px 18px", borderBottom: `1px solid ${color.border}`, display: "flex", alignItems: "baseline", gap: 12 }}>
          {title && <span style={{ fontSize: 15, fontWeight: 500, color: color.text }}>{title}</span>}
          {meta && <span style={{ fontFamily: font.mono, fontSize: 10.5, color: color.muted }}>{meta}</span>}
          {actions && <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>{actions}</div>}
        </div>
      )}
      <div style={{ padding: padded ? 18 : 0, display: "flex", flexDirection: "column", gap: 14, flex: 1 }}>
        {children}
      </div>
    </div>
  );
}
