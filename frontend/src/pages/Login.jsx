import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { normalizeError } from "../api/errors";
import { useAuth } from "../context/AuthContext";
import { color, font } from "../theme";
import Logo from "../components/Logo";
import { Button, Input } from "../components/ui";

// POST /auth/login prend email et password en QUERY PARAMS (routers/auth.py)
// et renvoie { access_token, token_type }. 401 si identifiants invalides.
const STEPS = [
  "Suspicious email submitted",
  "Phishing analysis - headers, URLs, attachments",
  "Extracted indicators",
  "Multi-source IOC lookup",
  "Analyst verdict",
];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError(null);
    setLoading(true);
    try {
      const res = await client.post("/auth/login", null, { params: { email, password } });
      login(res.data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(normalizeError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: color.bg, fontFamily: font.sans, color: color.text }}>
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <form onSubmit={handleSubmit} style={{ width: "100%", maxWidth: 392, display: "flex", flexDirection: "column", gap: 30 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <Logo size={44} />
            <span style={{ fontSize: 29, fontWeight: 700, letterSpacing: "0.045em" }}>BAITWAY</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <span style={{ fontSize: 24, fontWeight: 700, letterSpacing: "-0.02em" }}>Analyst sign-in</span>
            <span style={{ fontSize: 14, lineHeight: 1.5, color: color.muted }}>Restricted to SOC members.</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <Input label="EMAIL" type="email" autoComplete="username" required
              value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input label="PASSWORD" type="password" autoComplete="current-password" required
              value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          <Button type="submit" variant="primary" disabled={loading} style={{ height: 48, fontSize: 15 }}>
            {loading ? "Signing in…" : "Sign in"}
          </Button>

          {error && (
            <div role="alert" style={{ display: "flex", alignItems: "center", gap: 9, border: "1px solid #4A1A1E", background: "#1A0B0D", padding: 12 }}>
              <span style={{ width: 8, height: 8, background: "#EF4444", flex: "none" }} />
              <span style={{ fontSize: 13, color: color.text }}>{error.message}</span>
            </div>
          )}

          <span style={{ fontFamily: font.mono, fontSize: 11, lineHeight: 1.6, color: color.muted }}>
            JWT session stored in localStorage.
          </span>
        </form>
      </div>

      <aside style={{ width: 560, flex: "none", borderLeft: `1px solid ${color.border}`, padding: "60px 56px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 30 }}>
        <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: "0.12em", color: color.muted }}>INVESTIGATION FLOW</span>
        <ol style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column" }}>
          {STEPS.map((step, i) => (
            <li key={step}>
              <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 0" }}>
                <span style={{ fontFamily: font.mono, fontSize: 11, color: color.info, width: 22, flex: "none" }}>{String(i + 1).padStart(2, "0")}</span>
                <span style={{ fontSize: 16 }}>{step}</span>
              </div>
              {i < STEPS.length - 1 && <div style={{ width: 1, height: 14, background: color.border, marginLeft: 10 }} />}
            </li>
          ))}
        </ol>
      </aside>
    </div>
  );
}
