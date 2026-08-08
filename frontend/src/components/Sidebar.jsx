import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const { logout } = useAuth();
  return (
    <nav style={{ width: "220px", background: "#16233f", color: "#fff", padding: "20px", height: "100vh" }}>
      <h2 style={{ marginBottom: "30px" }}>BaitWay</h2>
      <NavLink to="/phishing" style={{ display: "block", color: "#cdd6e4", padding: "10px 0", textDecoration: "none" }}>
        Portail Phishing
      </NavLink>
      <NavLink to="/ioc" style={{ display: "block", color: "#cdd6e4", padding: "10px 0", textDecoration: "none" }}>
        Recherche d'IOC
      </NavLink>
      <button onClick={logout} style={{ marginTop: "30px", padding: "8px 16px", cursor: "pointer" }}>
        Déconnexion
      </button>
    </nav>
  );
}