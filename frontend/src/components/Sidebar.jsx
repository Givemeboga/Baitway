import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { currentUser } from "../lib/jwt";
import { useViewport } from "../lib/useIsNarrow";
import { color, font, layout } from "../theme";
import Logo from "./Logo";

const NAV = [
  { to: "/dashboard", label: "Dashboard", short: "DB" },
  { to: "/phishing", label: "Phishing Portal", short: "PH" },
  { to: "/ioc", label: "IOC Lookup", short: "IOC" },
];

function navStyle(isActive, collapsed) {
  return {
    display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "space-between",
    gap: 10, padding: collapsed ? "11px 0" : "11px 12px",
    borderLeft: `2px solid ${isActive ? color.accent : "transparent"}`,
    background: isActive ? color.elevated : "transparent",
    color: isActive ? color.text : color.muted,
    fontSize: 14.5, textDecoration: "none",
  };
}

export default function Sidebar({ pendingCount = 0 }) {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const { isTablet, isMobile } = useViewport();
  const user = currentUser(token);

  const handleLogout = () => { logout(); navigate("/login"); };

  // Mobile : la navigation passe en barre basse (voir AppShell).
  if (isMobile) return null;

  const collapsed = isTablet;
  return (
    <nav style={{
      width: collapsed ? layout.sidebarCollapsed : layout.sidebarWidth, flex: "none",
      background: color.sidebar, borderRight: `1px solid ${color.border}`,
      padding: collapsed ? "18px 0" : "22px 18px",
      display: "flex", flexDirection: "column", minHeight: "100vh", boxSizing: "border-box",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start", gap: 11, padding: collapsed ? 0 : "0 8px", marginBottom: 34 }}>
        <Logo size={collapsed ? 26 : 30} />
        {!collapsed && <span style={{ fontSize: 19, fontWeight: 700, letterSpacing: "0.045em", color: color.text }}>BAITWAY</span>}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {NAV.map((item) => (
          <NavLink key={item.to} to={item.to} style={({ isActive }) => navStyle(isActive, collapsed)}>
            <span>{collapsed ? item.short : item.label}</span>
            {!collapsed && item.to === "/phishing" && pendingCount > 0 && (
              <span style={{ fontFamily: font.mono, fontSize: 11, color: "#F87171" }}>{pendingCount}</span>
            )}
          </NavLink>
        ))}
      </div>

      {!collapsed && (
        <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: 14, padding: "0 12px" }}>
          <div style={{ height: 1, background: color.border }} />
          {user && (
            <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
              <span style={{ fontSize: 13, color: color.text, overflow: "hidden", textOverflow: "ellipsis" }}>{user.email}</span>
              <span style={{ fontFamily: font.mono, fontSize: 10.5, color: color.muted }}>{user.role}</span>
            </div>
          )}
          <button onClick={handleLogout} style={{ alignSelf: "flex-start", padding: "7px 13px", fontFamily: "inherit", fontSize: 12.5, color: color.muted, background: "transparent", border: `1px solid ${color.border}`, cursor: "pointer" }}>
            Sign out
          </button>
        </div>
      )}
    </nav>
  );
}
