import { color, font } from "../../theme";

// columns: [{ key, header, width, align, render(row) }]
// Sur petit ecran la table bascule en cartes empilees (voir Sidebar/useIsNarrow).
export default function DataTable({ columns, rows, rowKey, onRowClick, stacked, empty }) {
  if (!rows.length) return empty || null;
  const grid = columns.map((c) => c.width || "1fr").join(" ");

  if (stacked) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {rows.map((row) => (
          <div key={rowKey(row)} onClick={() => onRowClick?.(row)}
            style={{ background: color.card, border: `1px solid ${color.border}`, padding: 14, display: "flex", flexDirection: "column", gap: 8, cursor: onRowClick ? "pointer" : "default" }}>
            {columns.map((c) => (
              <div key={c.key} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontFamily: font.mono, fontSize: 9.5, letterSpacing: "0.08em", color: color.muted, width: 84, flex: "none" }}>{c.header}</span>
                <span style={{ fontSize: 13, color: color.text, minWidth: 0 }}>{c.render ? c.render(row) : row[c.key]}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ display: "grid", gridTemplateColumns: grid, gap: 12, padding: "0 0 11px", borderBottom: `1px solid ${color.border}`, fontFamily: font.mono, fontSize: 9.5, letterSpacing: "0.09em", color: color.muted }}>
        {columns.map((c) => <span key={c.key} style={{ textAlign: c.align || "left" }}>{c.header}</span>)}
      </div>
      {rows.map((row) => (
        <div key={rowKey(row)} onClick={() => onRowClick?.(row)}
          style={{ display: "grid", gridTemplateColumns: grid, gap: 12, alignItems: "center", padding: "13px 0", borderBottom: `1px solid ${color.divider}`, cursor: onRowClick ? "pointer" : "default" }}>
          {columns.map((c) => (
            <span key={c.key} style={{ fontSize: 13.5, color: color.text, textAlign: c.align || "left", minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {c.render ? c.render(row) : row[c.key]}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}
