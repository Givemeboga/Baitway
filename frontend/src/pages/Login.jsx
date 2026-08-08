import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async () => {
    setError("");
    try {
      const res = await client.post("/auth/login", null, {
        params: { email, password },
      });
      login(res.data.access_token);
      navigate("/dashboard");
    } catch {
      setError("Identifiants invalides");
    }
  };

  return (
    <div style={{ maxWidth: "320px", margin: "100px auto", fontFamily: "sans-serif" }}>
      <h1>BaitWay</h1>
      <h3>Connexion</h3>
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ display: "block", width: "100%", padding: "8px", marginBottom: "10px" }}
      />
      <input
        type="password"
        placeholder="Mot de passe"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ display: "block", width: "100%", padding: "8px", marginBottom: "10px" }}
      />
      <button onClick={handleSubmit} style={{ padding: "10px 20px", cursor: "pointer" }}>
        Se connecter
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}