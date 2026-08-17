import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PhishingList from "./pages/phishing/PhishingList";
import PhishingDetail from "./pages/phishing/PhishingDetail";
import IOCPlaceholder from "./pages/IOCPlaceholder";

// La coquille (barre laterale + zone de contenu) est portee par AppShell,
// utilise dans chaque page : plus besoin du Layout global d'origine.
function Private({ children }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Private><Dashboard /></Private>} />
        <Route path="/phishing" element={<Private><PhishingList /></Private>} />
        <Route path="/phishing/:id" element={<Private><PhishingDetail /></Private>} />
        <Route path="/ioc" element={<Private><IOCPlaceholder /></Private>} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
