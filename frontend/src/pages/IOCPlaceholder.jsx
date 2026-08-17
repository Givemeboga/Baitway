import { useSearchParams } from "react-router-dom";
import AppShell from "../components/AppShell";
import { Card, EmptyState } from "../components/ui";
import { color, font } from "../theme";

// Placeholder du Module B (responsable : Iheb). La vraie page vit dans
// pages/ioc/ sur sa branche : ne rien ecrire ici qui empiete sur son module.
// Le lien « Enqueter » des indicateurs pointe deja ici avec ?indicator=... :
// il fonctionnera sans modification des que la page IOC sera livree.
export default function IOCPlaceholder() {
  const [params] = useSearchParams();
  const indicator = params.get("indicator");

  return (
    <AppShell
      title="IOC Lookup"
      subtitle="Module B — under development by Iheb Ben Massaoud."
    >
      <Card title="Module unavailable" meta="POST /ioc/lookup">
        <EmptyState
          title="The IOC lookup module has not shipped yet"
          message="The /ioc router is not mounted on the backend and its interface is being built on another branch. This page will hand over once it ships."
        />
        {indicator && (
          <div
            style={{
              marginTop: 16,
              padding: 14,
              border: `1px solid ${color.border}`,
              borderRadius: 8,
              background: color.elevated,
            }}
          >
            <div style={{ fontSize: 12, color: color.muted, marginBottom: 6 }}>
              Indicator passed from the phishing analysis:
            </div>
            <code style={{ fontFamily: font.mono, fontSize: 13, color: color.info }}>
              {indicator}
            </code>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
