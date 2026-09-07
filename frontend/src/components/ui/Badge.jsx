import { font } from "../../theme";

// Puce generique. La couleur vient toujours d'un jeton de severite,
// jamais d'une valeur ecrite en dur a l'appel.
export default function Badge({ tone, children, style }) {
  return (
    <span style={{
      fontFamily: font.mono, fontSize: 10, letterSpacing: "0.04em",
      color: tone.fg, border: `1px solid ${tone.border}`,
      padding: "3px 7px", whiteSpace: "nowrap", ...style,
    }}>
      {children}
    </span>
  );
}
