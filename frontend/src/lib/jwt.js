// Le backend signe un JWT contenant { sub: email, role } (voir routers/auth.py).
// On lit la charge utile cote client pour afficher l'analyste connecte :
// aucune route /auth/me n'existe, et en inventer une serait hors contrat.
export function decodeToken(token) {
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function currentUser(token) {
  const claims = decodeToken(token);
  if (!claims) return null;
  return { email: claims.sub || "", role: claims.role || "" };
}
