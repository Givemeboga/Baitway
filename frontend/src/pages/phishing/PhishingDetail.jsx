import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getSubmission, updateSubmission } from "../../api/phishing";
import { normalizeError } from "../../api/errors";
import { toneForVerdict, formatDate } from "../../lib/verdict";
import { severity, color, font } from "../../theme";
import AppShell from "../../components/AppShell";
import { Card, Button, Input, Badge, SeverityBadge, IOCChip, LoadingState, EmptyState, ErrorState } from "../../components/ui";

const AUTH_TONE = { pass: severity.safe, fail: severity.critical, none: severity.unknown };
const REPUTATION_TONE = {
  clean: severity.safe, suspicious: severity.high,
  malicious: severity.critical, unknown: severity.unknown,
};

function Section({ label, count, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: "0.1em", color: color.muted }}>
        {label}{count !== undefined && ` — ${count}`}
      </span>
      {children}
    </div>
  );
}

export default function PhishingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sub, setSub] = useState(null);
  const [error, setError] = useState(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () => {
    setError(null);
    setSub(null);
    getSubmission(id)
      .then((data) => { setSub(data); setNotes(data.notes || ""); })
      .catch((e) => setError(normalizeError(e)));
  };
  useEffect(load, [id]);

  // PATCH /phishing/submissions/{id} accepte verdict, status et notes (tous optionnels).
  const patch = async (body) => {
    setSaving(true);
    try {
      const updated = await updateSubmission(id, body);
      setSub(updated);
    } catch (e) {
      setError(normalizeError(e));
    } finally {
      setSaving(false);
    }
  };

  // Le pont entre les deux modules (contrat d'API, section 5).
  const investigate = (indicator) =>
    navigate(`/ioc?indicator=${encodeURIComponent(indicator.value)}&from=${id}`);

  if (error) return <AppShell title="Submission"><Card><ErrorState error={error} onRetry={load} /></Card></AppShell>;
  if (!sub) return <AppShell title="Submission"><Card><LoadingState label="Loading analysis…" /></Card></AppShell>;

  const tone = toneForVerdict(sub.verdict);
  const { headers, urls = [], attachments = [], indicators = [] } = sub;

  return (
    <AppShell
      title={sub.subject}
      subtitle={`${headers.from} · reply_to ${headers.reply_to} · ${formatDate(sub.analyzed_at)}`}
      actions={<Button onClick={() => navigate("/phishing")}>← Triage queue</Button>}
    >
      {/* QUEL RISQUE — verdict et score avant toute preuve. */}
      <Card>
        <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontSize: 44, fontWeight: 700, letterSpacing: "-0.04em", lineHeight: 1, color: tone.fg }}>{sub.risk_score}</span>
            <SeverityBadge value={sub.verdict} dot={false} style={{ fontSize: 14 }} />
          </div>
          <div style={{ flex: 1, minWidth: 180, height: 5, background: color.divider }}>
            <div style={{ width: `${sub.risk_score}%`, height: "100%", background: tone.fg }} />
          </div>
          <div style={{ display: "flex", gap: 9, flexWrap: "wrap" }}>
            <Button variant="primary" disabled={saving || sub.status === "resolved"}
              onClick={() => patch({ status: "resolved" })}>Mark resolved</Button>
            <Button disabled={saving || sub.status !== "pending"}
              onClick={() => patch({ status: "reviewed" })}>Mark reviewed</Button>
          </div>
          <span style={{ fontFamily: font.mono, fontSize: 11, color: color.muted }}>status: {sub.status}</span>
        </div>
      </Card>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
        {/* POURQUOI — les preuves. */}
        <Card title="Evidence" style={{ flex: 3, minWidth: 420 }}>
          <Section label="HEADER AUTHENTICATION">
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {["spf", "dkim", "dmarc"].map((k) => {
                const t = AUTH_TONE[headers[k]] || severity.unknown;
                return (
                  <div key={k} style={{ flex: 1, minWidth: 96, border: `1px solid ${t.border}`, background: t.bg, padding: 13, display: "flex", flexDirection: "column", gap: 7 }}>
                    <span style={{ fontFamily: font.mono, fontSize: 10.5, color: color.muted }}>{k.toUpperCase()}</span>
                    <span style={{ fontFamily: font.mono, fontSize: 15, color: t.fg }}>{headers[k]}</span>
                  </div>
                );
              })}
            </div>
            <div style={{ display: "flex", gap: 10, fontFamily: font.mono, fontSize: 12 }}>
              <span style={{ color: color.muted, width: 78, flex: "none" }}>origin_ip</span>
              <span>{headers.origin_ip}</span>
            </div>
          </Section>

          <Section label="URL" count={urls.length}>
            {urls.length === 0 && <span style={{ fontSize: 13, color: color.muted }}>No URLs in this email.</span>}
            {urls.map((u) => {
              const t = REPUTATION_TONE[u.reputation] || severity.unknown;
              return (
                <div key={u.url} style={{ border: `1px solid ${color.border}`, background: color.elevated, padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14 }}>
                    <span style={{ fontFamily: font.mono, fontSize: 12.5, wordBreak: "break-all" }}>{u.defanged || u.url}</span>
                    <span style={{ fontFamily: font.mono, fontSize: 11, color: t.fg, flex: "none" }}>{u.reputation}</span>
                  </div>
                  {u.flags?.length > 0 && (
                    <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
                      {u.flags.map((flag) => <Badge key={flag} tone={severity.high}>{flag}</Badge>)}
                    </div>
                  )}
                </div>
              );
            })}
          </Section>

          <Section label="ATTACHMENTS" count={attachments.length}>
            {attachments.length === 0 && <span style={{ fontSize: 13, color: color.muted }}>No attachments.</span>}
            {attachments.map((a) => {
              const t = REPUTATION_TONE[a.reputation] || severity.unknown;
              return (
                <div key={a.sha256} style={{ border: `1px solid ${color.border}`, background: color.elevated, padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14 }}>
                    <span style={{ fontSize: 13.5 }}>{a.filename}</span>
                    <span style={{ fontFamily: font.mono, fontSize: 11, color: t.fg, flex: "none" }}>{a.reputation}</span>
                  </div>
                  <span style={{ fontFamily: font.mono, fontSize: 11.5, color: color.muted, wordBreak: "break-all" }}>sha256 {a.sha256}</span>
                  {a.flags?.length > 0 && (
                    <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
                      {a.flags.map((flag) => <Badge key={flag} tone={severity.critical}>{flag}</Badge>)}
                    </div>
                  )}
                </div>
              );
            })}
          </Section>
        </Card>

        {/* QUOI FAIRE — le passage vers le module IOC. */}
        <Card title="Extracted indicators" meta={`${indicators.length} — clickable`} style={{ flex: 2, minWidth: 340 }}>
          {indicators.length === 0 ? (
            <EmptyState title="No indicators" message="The analysis extracted no IP, domain, URL or hash." />
          ) : (
            <>
              <span style={{ fontSize: 12.5, lineHeight: 1.5, color: color.muted }}>
                Each button opens the IOC lookup with the indicator pre-filled.
              </span>
              {indicators.map((ind) => (
                <IOCChip key={`${ind.type}:${ind.value}`} indicator={ind} onInvestigate={investigate} />
              ))}
            </>
          )}

          <div style={{ marginTop: "auto", paddingTop: 16, borderTop: `1px solid ${color.border}`, display: "flex", flexDirection: "column", gap: 9 }}>
            <span style={{ fontFamily: font.mono, fontSize: 10, letterSpacing: "0.1em", color: color.muted }}>ANALYST NOTES</span>
            <Input textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Context, decision, actions taken…" />
            <Button disabled={saving || notes === (sub.notes || "")} onClick={() => patch({ notes })} style={{ alignSelf: "flex-start" }}>
              {saving ? "Saving…" : "Save note"}
            </Button>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
