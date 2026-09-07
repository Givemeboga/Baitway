import { color, font } from "../../theme";

export default function Input({ label, mono, textarea, style, ...rest }) {
  const field = {
    width: "100%",
    padding: textarea ? 11 : "0 14px",
    height: textarea ? undefined : 44,
    minHeight: textarea ? 72 : undefined,
    fontFamily: mono ? font.mono : "inherit",
    fontSize: 14,
    lineHeight: textarea ? 1.5 : undefined,
    color: color.text,
    background: color.bg,
    border: `1px solid ${color.border}`,
    outline: "none",
    resize: textarea ? "vertical" : undefined,
    boxSizing: "border-box",
    ...style,
  };
  const control = textarea ? <textarea style={field} {...rest} /> : <input style={field} {...rest} />;
  if (!label) return control;
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: "0.1em", color: color.muted }}>{label}</span>
      {control}
    </label>
  );
}
