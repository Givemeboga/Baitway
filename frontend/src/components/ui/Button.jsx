import { color, font } from "../../theme";

// variant: "primary" (action) | "secondary" | "ghost"
// Le bleu est reserve aux actions : il ne code jamais une severite.
export default function Button({ variant = "secondary", disabled, mono, children, style, ...rest }) {
  const base = {
    padding: "9px 15px",
    fontFamily: mono ? font.mono : "inherit",
    fontSize: mono ? 11.5 : 13,
    border: "1px solid transparent",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    lineHeight: 1.2,
  };
  const variants = {
    primary: { background: color.accent, color: color.text, borderColor: color.accent },
    secondary: { background: "transparent", color: color.muted, borderColor: color.border },
    ghost: { background: "transparent", color: color.info, borderColor: color.accent },
  };
  return (
    <button disabled={disabled} style={{ ...base, ...variants[variant], ...style }} {...rest}>
      {children}
    </button>
  );
}
