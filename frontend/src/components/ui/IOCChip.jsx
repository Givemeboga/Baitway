import { color, font } from "../../theme";
import SeverityBadge from "./SeverityBadge";
import Button from "./Button";

// Le pivot du produit : un indicateur extrait d'un e-mail, et l'action qui
// l'emmene vers la recherche d'IOC. QUOI -> QUEL RISQUE -> POURQUOI -> QUOI FAIRE.
export default function IOCChip({ indicator, onInvestigate }) {
  const { type, value, severity, reason } = indicator;
  return (
    <div style={{ background: color.card, border: `1px solid ${color.border}`, padding: "13px 14px", display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ fontFamily: font.mono, fontSize: 9, letterSpacing: "0.09em", color: color.muted, background: color.bg, border: `1px solid ${color.border}`, padding: "3px 6px", flex: "none", textTransform: "uppercase" }}>{type}</span>
        <span style={{ fontFamily: font.mono, fontSize: 12.5, color: color.text, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{value}</span>
        <SeverityBadge kind="severity" value={severity} style={{ flex: "none" }} />
      </div>
      {reason && <span style={{ fontSize: 12, lineHeight: 1.45, color: color.muted }}>{reason}</span>}
      <Button variant="ghost" mono onClick={() => onInvestigate(indicator)} style={{ alignSelf: "flex-start", padding: "6px 11px" }}>
        Investigate →
      </Button>
    </div>
  );
}
