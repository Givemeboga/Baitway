// FastAPI renvoie ses erreurs sous la forme { detail: "..." } (HTTPException)
// ou { detail: [...] } pour une erreur de validation 422.
// Le contrat d'API decrit une enveloppe { success, data, error } : elle n'est
// pas encore implementee cote backend. Cette fonction accepte les deux formes
// pour ne rien casser le jour ou l'enveloppe arrivera.
export function normalizeError(err) {
  const status = err?.response?.status ?? 0;
  const data = err?.response?.data;

  if (data?.error?.message) {
    return { status, code: data.error.code || String(status), message: data.error.message };
  }

  const detail = data?.detail;
  if (typeof detail === "string") {
    return { status, code: String(status), message: detail };
  }
  if (Array.isArray(detail) && detail.length) {
    return { status, code: "422", message: detail[0]?.msg || "Donnees invalides" };
  }
  if (status === 0) {
    return { status, code: "NETWORK", message: "Le serveur BaitWay est injoignable" };
  }
  return { status, code: String(status), message: "Unexpected error" };
}
