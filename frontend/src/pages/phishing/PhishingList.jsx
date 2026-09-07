import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listSubmissions, analyzeEmail } from "../../api/phishing";
import { normalizeError } from "../../api/errors";
import { toneForVerdict } from "../../lib/verdict";
import { useViewport } from "../../lib/useIsNarrow";
import { color, font } from "../../theme";
import AppShell from "../../components/AppShell";
import { Card, Button, Input, DataTable, SeverityBadge, LoadingState, EmptyState, ErrorState } from "../../components/ui";

// POST /phishing/analyze attend { raw_email } (schemas/phishing.py AnalyzeRequest)
// et rejette une chaine vide avec un 400.
export default function PhishingList() {
  const [submissions, setSubmissions] = useState(null);
  const [error, setError] = useState(null);
  const [raw, setRaw] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState(null);
  const navigate = useNavigate();
  const { isMobile } = useViewport();

  const load = () => {
    setError(null);
    listSubmissions().then(setSubmissions).catch((e) => setError(normalizeError(e)));
  };
  useEffect(load, []);

  const handleAnalyze = async () => {
    if (!raw.trim() || analyzing) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const result = await analyzeEmail(raw);
      setRaw("");
      navigate(`/phishing/${result.submission_id}`);
    } catch (e) {
      setAnalyzeError(normalizeError(e));
    } finally {
      setAnalyzing(false);
    }
  };

  const pending = submissions?.filter((s) => s.status === "pending").length || 0;

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
    <AppShell pendingCount={pending} title="Phishing Portal" subtitle="Submit a raw email, then triage the queue by risk.">
      <Card title="New analysis" meta="POST /phishing/analyze">
        <Input
          textarea
          mono
          placeholder="Paste the raw .eml content here (headers included)…"
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          style={{ minHeight: 132 }}
        />
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <Button variant="primary" onClick={handleAnalyze} disabled={!raw.trim() || analyzing}>
            {analyzing ? "Analyzing…" : "Analyze email"}
          </Button>
          <span style={{ fontSize: 12.5, color: color.muted }}>
            Headers, URLs and attachments processed in a single request.
          </span>
        </div>
        {analyzing && <LoadingState label="Analyzing…" hint="The result opens as soon as it is ready." />}
        {analyzeError && <ErrorState error={analyzeError} />}
      </Card>

      <Card title="Triage queue" meta="highest risk first" padded={false}>
        <div style={{ padding: "0 18px 6px" }}>
          {error && <div style={{ padding: 18 }}><ErrorState error={error} onRetry={load} /></div>}
          {!error && !submissions && <div style={{ padding: 18 }}><LoadingState label="Loading…" /></div>}
          {submissions && (
            <DataTable
              columns={columns}
              rows={submissions}
              stacked={isMobile}
              rowKey={(r) => r.submission_id}
              onRowClick={(r) => navigate(`/phishing/${r.submission_id}`)}
              empty={<EmptyState title="No submissions" message="The queue is empty. Submit a suspicious email to start an analysis." />}
            />
          )}
        </div>
      </Card>
    </AppShell>
  );
}
