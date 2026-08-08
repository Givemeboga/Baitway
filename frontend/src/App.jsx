import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

function Layout({ children }) {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <div style={{ flex: 1 }}>{children}</div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout><Dashboard /></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/phishing"
          element={
            <ProtectedRoute>
              <Layout><div style={{ padding: 40 }}><h1>Module Phishing (à venir)</h1></div></Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ioc"
          element={
            <ProtectedRoute>
              <Layout><div style={{ padding: 40 }}><h1>Module IOC (à venir)</h1></div></Layout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}