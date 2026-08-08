\# Contrat d'API — BaitWay



Ce document définit les conventions communes et les schémas d'échange entre le frontend et le backend. \*\*Il doit être validé par Youssef et Iheb avant le développement des modules.\*\* Une fois figé, chacun peut développer son module de façon autonome en se basant sur ces schémas (et en mockant les données de l'autre si besoin).



\---



\## 1. Conventions générales



\### Base URL

```

http://localhost:8000

```



\### Format de réponse standard

Toutes les réponses suivent la même enveloppe :



```json

{

&#x20; "success": true,

&#x20; "data": { ... },

&#x20; "error": null

}

```



En cas d'erreur :

```json

{

&#x20; "success": false,

&#x20; "data": null,

&#x20; "error": {

&#x20;   "code": "string",

&#x20;   "message": "string"

&#x20; }

}

```



\### Préfixes de routes

| Domaine | Préfixe | Responsable |

|---|---|---|

| Authentification | `/auth/\*` | Commun |

| Portail Phishing | `/phishing/\*` | Youssef |

| Recherche d'IOC | `/ioc/\*` | Iheb |



\### Authentification

\- Toutes les routes des modules (`/phishing/\*`, `/ioc/\*`) sont protégées par JWT.

\- Le token est envoyé dans l'en-tête : `Authorization: Bearer <token>`.

\- Un token expiré ou invalide renvoie `401 Unauthorized`.



\### Codes de statut HTTP utilisés

| Code | Signification |

|---|---|

| 200 | Succès |

| 201 | Ressource créée |

| 400 | Requête invalide (données manquantes/mal formées) |

| 401 | Non authentifié (token absent/invalide) |

| 403 | Non autorisé (rôle insuffisant) |

| 404 | Ressource introuvable |

| 422 | Erreur de validation |

| 500 | Erreur serveur |



\### Format des dates

Toutes les dates sont en \*\*ISO 8601 UTC\*\* : `2026-08-08T22:18:07Z`.



\### Vocabulaire commun des verdicts

Les deux modules utilisent \*\*exactement\*\* les mêmes valeurs de verdict et la même échelle de score :



| Verdict | Score (0-100) | Signification |

|---|---|---|

| `clean` | 0 – 30 | Aucun signe de malveillance |

| `suspicious` | 31 – 70 | Signaux préoccupants, à examiner |

| `malicious` | 71 – 100 | Malveillant avéré |



\---



\## 2. Module commun — Authentification (`/auth`)



\### POST /auth/register

Crée un nouvel utilisateur.



\*\*Requête\*\* (query parameters) :

| Champ | Type | Requis |

|---|---|---|

| email | string | oui |

| password | string | oui |



\*\*Réponse 200 :\*\*

```json

{

&#x20; "message": "Utilisateur cree"

}

```



\*\*Erreurs :\*\* `400` si l'email est déjà utilisé.



\---



\### POST /auth/login

Authentifie un utilisateur et renvoie un token JWT.



\*\*Requête\*\* (query parameters) :

| Champ | Type | Requis |

|---|---|---|

| email | string | oui |

| password | string | oui |



\*\*Réponse 200 :\*\*

```json

{

&#x20; "access\_token": "eyJhbGciOi...",

&#x20; "token\_type": "bearer"

}

```



\*\*Erreurs :\*\* `401` si les identifiants sont invalides.



\---



\## 3. Module A — Portail Phishing (`/phishing`)  — Responsable : Youssef



\### POST /phishing/analyze

Soumet un e-mail (au format `.eml`, brut ou téléversé) pour analyse.



\*\*Requête :\*\*

```json

{

&#x20; "raw\_email": "string (contenu brut du .eml)"

}

```

> Alternative : envoi du fichier via `multipart/form-data` avec un champ `file`. À trancher ensemble à l'implémentation ; le schéma de réponse ci-dessous reste identique quelle que soit la méthode d'envoi.



\*\*Réponse 200 :\*\*

```json

{

&#x20; "submission\_id": "string",

&#x20; "verdict": "clean | suspicious | malicious",

&#x20; "risk\_score": 0,

&#x20; "headers": {

&#x20;   "spf": "pass | fail | none",

&#x20;   "dkim": "pass | fail | none",

&#x20;   "dmarc": "pass | fail | none",

&#x20;   "from": "string",

&#x20;   "reply\_to": "string",

&#x20;   "origin\_ip": "string"

&#x20; },

&#x20; "urls": \[

&#x20;   {

&#x20;     "url": "string",

&#x20;     "defanged": "string",

&#x20;     "reputation": "clean | suspicious | malicious | unknown",

&#x20;     "flags": \["shortener", "typosquat", "ip\_based", "..."]

&#x20;   }

&#x20; ],

&#x20; "attachments": \[

&#x20;   {

&#x20;     "filename": "string",

&#x20;     "sha256": "string",

&#x20;     "reputation": "clean | suspicious | malicious | unknown",

&#x20;     "flags": \["dangerous\_extension", "double\_extension", "macro\_enabled", "..."]

&#x20;   }

&#x20; ],

&#x20; "indicators": \[

&#x20;   {

&#x20;     "type": "ip | domain | url | hash",

&#x20;     "value": "string",

&#x20;     "severity": "low | medium | high",

&#x20;     "reason": "string"

&#x20;   }

&#x20; ],

&#x20; "analyzed\_at": "2026-08-08T22:18:07Z"

}

```



\---



\### GET /phishing/submissions

Liste les soumissions, triées par risque décroissant (file de triage).



\*\*Réponse 200 :\*\*

```json

{

&#x20; "submissions": \[

&#x20;   {

&#x20;     "submission\_id": "string",

&#x20;     "subject": "string",

&#x20;     "from": "string",

&#x20;     "verdict": "clean | suspicious | malicious",

&#x20;     "risk\_score": 0,

&#x20;     "status": "pending | reviewed | resolved",

&#x20;     "analyzed\_at": "2026-08-08T22:18:07Z"

&#x20;   }

&#x20; ]

}

```



\---



\### GET /phishing/submissions/{submission\_id}

Récupère le détail complet d'une soumission (même structure que la réponse de `POST /phishing/analyze`, enrichie du statut et des notes analyste).



\---



\### PATCH /phishing/submissions/{submission\_id}

Met à jour le verdict / statut par l'analyste.



\*\*Requête :\*\*

```json

{

&#x20; "verdict": "clean | suspicious | malicious",

&#x20; "status": "pending | reviewed | resolved",

&#x20; "notes": "string"

}

```



\*\*Réponse 200 :\*\* l'objet soumission mis à jour.



\---



\## 4. Module B — Recherche d'IOC (`/ioc`)  — Responsable : Iheb



\### POST /ioc/lookup

Soumet un indicateur pour enrichissement multi-sources.



\*\*Requête :\*\*

```json

{

&#x20; "indicator": "string"

}

```

> Le type (`ip`, `domain`, `url`, `hash`) est \*\*détecté automatiquement\*\* côté serveur. Le client n'a pas besoin de le préciser.



\*\*Réponse 200 :\*\*

```json

{

&#x20; "lookup\_id": "string",

&#x20; "indicator": "string",

&#x20; "type": "ip | domain | url | hash",

&#x20; "verdict": "clean | suspicious | malicious",

&#x20; "risk\_score": 0,

&#x20; "sources": \[

&#x20;   {

&#x20;     "name": "VirusTotal | AbuseIPDB | URLhaus | MalwareBazaar | WHOIS | ...",

&#x20;     "result": "clean | suspicious | malicious | unknown",

&#x20;     "score": 0,

&#x20;     "raw": { }

&#x20;   }

&#x20; ],

&#x20; "enrichment": {

&#x20;   "geolocation": "string (pour IP)",

&#x20;   "asn": "string (pour IP)",

&#x20;   "domain\_age\_days": 0,

&#x20;   "registrar": "string (pour domaine)",

&#x20;   "blacklisted": true

&#x20; },

&#x20; "looked\_up\_at": "2026-08-08T22:18:07Z"

}

```

> Le champ `raw` de chaque source contient la réponse brute du service externe (utile pour le débogage / l'affichage détaillé). Le champ `enrichment` regroupe les métadonnées transverses ; ses clés varient selon le type d'indicateur.



\---



\### GET /ioc/history

Liste l'historique des recherches, triées par date décroissante.



\*\*Réponse 200 :\*\*

```json

{

&#x20; "lookups": \[

&#x20;   {

&#x20;     "lookup\_id": "string",

&#x20;     "indicator": "string",

&#x20;     "type": "ip | domain | url | hash",

&#x20;     "verdict": "clean | suspicious | malicious",

&#x20;     "risk\_score": 0,

&#x20;     "looked\_up\_at": "2026-08-08T22:18:07Z"

&#x20;   }

&#x20; ]

}

```



\---



\### GET /ioc/lookups/{lookup\_id}

Récupère le détail complet d'une recherche (même structure que la réponse de `POST /ioc/lookup`).



\---



\### GET /ioc/export

Exporte les indicateurs (format CSV ou liste noire).



\*\*Query parameters :\*\*

| Champ | Type | Valeurs | Défaut |

|---|---|---|---|

| format | string | `csv` \\| `blocklist` | `csv` |

| verdict | string | `all` \\| `malicious` \\| `suspicious` | `malicious` |



\*\*Réponse 200 :\*\* fichier téléchargeable (CSV ou texte).



\---



\## 5. Lien inter-modules (Phase 3)



En phase d'intégration, la vue de détail d'une soumission phishing (Module A) proposera un bouton \*\*« Rechercher cet indicateur »\*\* sur chaque IP / domaine / URL / hash extrait. Ce bouton redirige vers le Module B avec l'indicateur pré-rempli :



```

/ioc?indicator=<valeur>

```



Le Module B lit ce paramètre d'URL au chargement et lance automatiquement `POST /ioc/lookup`.



\---



\## 6. Règles de collaboration



\- \*\*Aucune modification de ce contrat sans accord des deux.\*\* Toute évolution passe par une discussion et une mise à jour de ce fichier, avec un commit dédié (`docs: ...`).

\- Chacun peut créer un fichier de données mockées respectant ces schémas (`mock\_phishing.json`, `mock\_ioc.json`) pour développer son interface sans dépendre du moteur de l'autre.

\- Les valeurs de `verdict` et l'échelle de `risk\_score` sont \*\*communes et non négociables individuellement\*\* — elles garantissent la cohérence visuelle entre les deux modules (mêmes couleurs, même logique d'affichage).



\---



\_Version 1.0 — à valider par Youssef Ben Chaouacha et Iheb Ben Massaoud avant le démarrage de la Phase 1.\_

