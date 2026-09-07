import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../../api/client";
import { normalizeError } from "../../api/errors";
import { toneForVerdict, formatDate } from "../../lib/verdict";
import { color, font, severity } from "../../theme";
import AppShell from "../../components/AppShell";
import {
  Card, Button, Input, Badge, SeverityBadge,
  LoadingState, EmptyState, ErrorState,
} from "../../components/ui";

// POST /ioc/lookup attend { indicator } ; le type est detecte cote serveur.
// La page lit ?indicator= (pont depuis l'analyse phishing) et ?from= (retour).
export default function IOCLookup() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const indicatorParam = params.get("indicator");
  const from = params.get("from");

  const [inputValue, setInputValue] = useState(indicatorParam || "");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function runLookup(indicator) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.post("/ioc/lookup", { indicator });
      setResult(response.data);
    } catch (err) {
      setError(normalizeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (indicatorParam) {
      setInputValue(indicatorParam);
      runLookup(indicatorParam);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [indicatorParam]);

  function handleSubmit(e) {
    e.preventDefault();
    const value = inputValue.trim();
    if (value && !loading) runLookup(value);
  }

  const tone = result ? toneForVerdict(result.verdict) : null;
  const sources = result?.sources || [];
  const enrichment = result?.enrichment || {};

  // Seules les cles renseignees sont affichees : on ne montre pas de champ vide.
  const facts = [
    ["type", result?.type],
    ["geolocation", enrichment.geolocation],
    ["asn", enrichment.asn],
    ["domain_age_days", enrichment.domain_age_days],
    ["registrar", enrichment.registrar],
    ["blacklisted", enrichment.blacklisted ? "yes" : "no"],
    ["looked_up_at", result ? formatDate(result.looked_up_at) : null],
  ].filter(([, v]) => v !== null && v !== undefined && v !== "");

  return (
    <AppShell
      title="IOC Lookup"
      subtitle="Investigate an IP, domain, URL or file hash across multiple sources."
      actions={
        from ? (
          <Button onClick={() => navigate(`/phishing/${from}`)}>← Back to analysis</Button>
        ) : undefined
      }
    >
      <Card title="New lookup" meta="POST /ioc/lookup">
        <form onSubmit={handleSubmit} style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Input
            mono
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="8.8.8.8 · example.com · https://… · sha256…"
            style={{ flex: 1, minWidth: 260 }}
          />
          <Button variant="primary" type="submit" disabled={!inputValue.trim() || loading}>
            {loading ? "Looking up…" : "Look up"}
          </Button>
        </form>
        <span style={{ fontSize: 12.5, color: color.muted }}>
          The indicator type is detected server-side — no need to say which it is.
        </span>
        {loading && <LoadingState label="Querying sources…" hint="Results are cached for 60 minutes." />}
        {error && <ErrorState error={error} />}
      </Card>

      {!loading && !error && !result && (
        <Card>
          <EmptyState
            title="No lookup yet"
            message="Enter an indicator above, or open one from a phishing analysis."
          />
        </Card>
      )}

      {result && (
        <>
          {/* QUEL RISQUE — verdict et score avant toute preuve. */}
          <Card>
            <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                <span style={{ fontSize: 44, fontWeight: 700, letterSpacing: "-0.04em", lineHeight: 1, color: tone.fg }}>
                  {result.risk_score}
                </span>
                <SeverityBadge value={result.verdict} dot={false} style={{ fontSize: 14 }} />
              </div>
              <div style={{ flex: 1, minWidth: 180, height: 5, background: color.divider }}>
                <div style={{ width: `${Math.min(result.risk_score, 100)}%`, height: "100%", background: tone.fg }} />
              </div>
              <span style={{ fontFamily: font.mono, fontSize: 13, color: color.text, wordBreak: "break-all" }}>
                {result.indicator}
              </span>
            </div>
          </Card>

          <div style={{ display: "flex", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
            {/* POURQUOI — ce que chaque source a repondu. */}
            <Card title="Sources" meta={`${sources.length}`} style={{ flex: 3, minWidth: 340 }}>
              {sources.length === 0 ? (
                <EmptyState
                  title="No source returned data"
                  message="No configured source covers this indicator type."
                />
              ) : (
                sources.map((s, i) => (
                  <div
                    key={`${s.name}-${i}`}
                    style={{
                      display: "flex", alignItems: "center", justifyContent: "space-between",
                      gap: 14, padding: "11px 0",
                      borderBottom: i < sources.length - 1 ? `1px solid ${color.divider}` : "none",
                    }}
                  >
                    <span style={{ fontSize: 13.5 }}>{s.name}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                      <span style={{ fontFamily: font.mono, fontSize: 11.5, color: color.muted }}>
                        {s.score}
                      </span>
                      <SeverityBadge value={s.result} />
                    </div>
                  </div>
                ))
              )}
            </Card>

            {/* CONTEXTE — metadonnees transverses. */}
            <Card title="Enrichment" style={{ flex: 2, minWidth: 280 }}>
              {facts.length === 0 ? (
                <EmptyState title="No metadata" message="No enrichment available for this indicator." />
              ) : (
                facts.map(([k, v]) => (
                  <div key={k} style={{ display: "flex", gap: 12, alignItems: "baseline" }}>
                    <span style={{ fontFamily: font.mono, fontSize: 10.5, letterSpacing: "0.06em", color: color.muted, width: 118, flex: "none" }}>
                      {k}
                    </span>
                    <span style={{ fontSize: 13, wordBreak: "break-word" }}>{String(v)}</span>
                  </div>
                ))
              )}
              {result.verdict === "clean" && sources.every((s) => s.result === "unknown") && (
                <div style={{ marginTop: 4 }}>
                  <Badge tone={severity.unknown} style={{ whiteSpace: "normal", lineHeight: 1.5 }}>
                    no source had data — absence of a report is not a verdict
                  </Badge>
                </div>
              )}
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}
