import { NavLink } from "react-router-dom";
import { useViewport } from "../lib/useIsNarrow";
import { color, font } from "../theme";
import Logo from "./Logo";
import Sidebar from "./Sidebar";

const NAV = [
  { to: "/dashboard", label: "Home" },
  { to: "/phishing", label: "Phishing" },
  { to: "/ioc", label: "IOC" },
];

// Coquille commune : barre laterale persistante en desktop, barre basse en mobile.
export default function AppShell({ pendingCount, title, subtitle, actions, children }) {
  const { isMobile } = useViewport();

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: color.bg, fontFamily: font.sans, color: color.text }}>
      <Sidebar pendingCount={pendingCount} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {isMobile && (
          <header style={{ padding: 16, borderBottom: `1px solid ${color.border}`, display: "flex", alignItems: "center", gap: 10, background: color.sidebar }}>
            <Logo size={26} />
            <span style={{ fontSize: 17, fontWeight: 700, letterSpacing: "0.045em" }}>BAITWAY</span>
            {pendingCount > 0 && <span style={{ fontFamily: font.mono, fontSize: 11, color: "#F87171", marginLeft: "auto" }}>{pendingCount}</span>}
          </header>
        )}

        <main style={{ flex: 1, padding: isMobile ? 16 : "34px 38px", display: "flex", flexDirection: "column", gap: 26, minWidth: 0 }}>
          {(title || actions) && (
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 24, flexWrap: "wrap" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                {title && <h1 style={{ margin: 0, fontSize: isMobile ? 21 : 27, fontWeight: 700, letterSpacing: "-0.025em" }}>{title}</h1>}
                {subtitle && <span style={{ fontSize: 14, color: color.muted }}>{subtitle}</span>}
              </div>
              {actions && <div style={{ display: "flex", gap: 9 }}>{actions}</div>}
            </div>
          )}
          {children}
        </main>

        {isMobile && (
          <nav style={{ display: "flex", borderTop: `1px solid ${color.border}`, background: color.sidebar, position: "sticky", bottom: 0 }}>
            {NAV.map((item) => (
              <NavLink key={item.to} to={item.to} style={({ isActive }) => ({
                flex: 1, padding: 14, textAlign: "center", fontSize: 12, textDecoration: "none",
                color: isActive ? color.text : color.muted,
                background: isActive ? color.elevated : "transparent",
                borderRight: `1px solid ${color.border}`,
              })}>
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}
      </div>
    </div>
  );
}
