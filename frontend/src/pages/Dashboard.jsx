import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listSubmissions } from "../api/phishing";
import { normalizeError } from "../api/errors";
import { toneForVerdict, formatDate } from "../lib/verdict";
import { useViewport } from "../lib/useIsNarrow";
import { severity, color, font } from "../theme";
import AppShell from "../components/AppShell";
import { Card, StatCard, DataTable, SeverityBadge, Button, LoadingState, EmptyState, ErrorState } from "../components/ui";

// Toutes les valeurs affichees ici sont DERIVEES de GET /phishing/submissions.
// Le backend n'expose aucune route de metriques : rien n'est invente.
function derive(submissions) {
  return {
    pending: submissions.filter((s) => s.status === "pending").length,
    malicious: submissions.filter((s) => s.verdict === "malicious").length,
    suspicious: submissions.filter((s) => s.verdict === "suspicious").length,
    total: submissions.length,
    // La file arrive deja triee par risque decroissant (routers/phishing.py).
    queue: submissions.filter((s) => s.status === "pending"),
    recent: [...submissions].sort((a, b) => new Date(b.analyzed_at) - new Date(a.analyzed_at)).slice(0, 5),
  };
}

export default function Dashboard() {
  const [submissions, setSubmissions] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { isMobile } = useViewport();

  const load = () => {
    setError(null);
    setSubmissions(null);
    listSubmissions().then(setSubmissions).catch((e) => setError(normalizeError(e)));
  };
  useEffect(load, []);

  const d = submissions ? derive(submissions) : null;

  const columns = [
    { key: "risk_score", header: "SCORE", width: "56px",
      render: (r) => <span style={{ fontFamily: font.mono, fontSize: 15, color: toneForVerdict(r.verdict).fg }}>{r.risk_score}</span> },
    { key: "subject", header: "SUBJECT" },
    { key: "from", header: "SENDER", width: "180px",
      render: (r) => <span style={{ fontFamily: font.mono, fontSize: 12, color: color.muted }}>{r.from}</span> },
    { key: "verdict", header: "VERDICT", width: "116px", render: (r) => <SeverityBadge value={r.verdict} /> },
    { key: "status", header: "STATUS", width: "96px",
      render: (r) => <span style={{ fontFamily: font.mono, fontSize: 11, color: color.muted }}>{r.status}</span> },
  ];

  return (
    <AppShell
      pendingCount={d?.pending || 0}
      title="What needs your attention"
      subtitle={d ? `${d.pending} submission(s) awaiting triage out of ${d.total} analyzed.` : undefined}
      actions={<Button variant="primary" onClick={() => navigate("/phishing")}>Analyze an email</Button>}
    >
      {error && <Card><ErrorState error={error} onRetry={load} /></Card>}
      {!error && !submissions && <Card><LoadingState label="Loading the triage queue…" /></Card>}

      {d && (
        <>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            <StatCard label="AWAITING TRIAGE" value={d.pending} hint="status pending" tone={d.pending ? severity.high : undefined} />
            <StatCard label="VERDICT MALICIOUS" value={d.malicious} hint="to block" tone={d.malicious ? severity.critical : undefined} />
            <StatCard label="VERDICT SUSPICIOUS" value={d.suspicious} hint="to review" tone={d.suspicious ? severity.high : undefined} />
            <StatCard label="TOTAL ANALYZED" value={d.total} hint="submissions" />
          </div>

          <Card title="Triage queue" meta="highest risk first" padded={false}
            actions={<Button onClick={() => navigate("/phishing")}>View all</Button>}>
            <div style={{ padding: "0 18px 6px" }}>
              <DataTable
                columns={columns}
                rows={d.queue}
                stacked={isMobile}
                rowKey={(r) => r.submission_id}
                onRowClick={(r) => navigate(`/phishing/${r.submission_id}`)}
                empty={<EmptyState title="Nothing pending" message="All submissions have been handled." />}
              />
            </div>
          </Card>

          <div style={{ display: "flex", gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>
            <Card title="Recent analyses" style={{ flex: 3, minWidth: 320 }} padded={false}>
              <div style={{ padding: "4px 18px 14px" }}>
                {d.recent.map((s) => (
                  <div key={s.submission_id} onClick={() => navigate(`/phishing/${s.submission_id}`)}
                    style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 0", borderBottom: `1px solid ${color.divider}`, cursor: "pointer" }}>
                    <span style={{ fontFamily: font.mono, fontSize: 14, color: toneForVerdict(s.verdict).fg, width: 28, flex: "none" }}>{s.risk_score}</span>
                    <span style={{ fontSize: 13.5, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.subject}</span>
                    <span style={{ fontFamily: font.mono, fontSize: 11, color: color.muted, flex: "none" }}>{formatDate(s.analyzed_at)}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* GET /ioc/history n'existe pas encore : on le dit, on ne simule pas. */}
            <Card title="IOC activity" meta="GET /ioc/history" style={{ flex: 2, minWidth: 280 }}>
              <EmptyState
                title="IOC module unavailable"
                message="The /ioc router is not mounted on the backend yet. This card will show the lookup history once it ships."
                action={<Button onClick={() => navigate("/ioc")}>Open IOC lookup</Button>}
              />
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}
