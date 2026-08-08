<div align="center">



\# BaitWay



\*\*Plateforme d'analyse SOC — Portail de phishing \& Recherche d'IOC\*\*



Une plateforme web qui réunit deux tâches clés d'un SOC en un seul endroit : l'analyse automatisée d'e-mails de phishing et la recherche d'indicateurs de compromission (IOC).



!\[Status](https://img.shields.io/badge/status-en%20d%C3%A9veloppement-orange)

!\[Backend](https://img.shields.io/badge/backend-FastAPI-009688)

!\[Frontend](https://img.shields.io/badge/frontend-React-61DAFB)

!\[Database](https://img.shields.io/badge/database-PostgreSQL-336791)

!\[License](https://img.shields.io/badge/license-MIT-green)



</div>



\---



\## Table des matières



\- \[Aperçu](#aperçu)

\- \[Fonctionnalités](#fonctionnalités)

\- \[Architecture](#architecture)

\- \[Stack technique](#stack-technique)

\- \[Prérequis](#prérequis)

\- \[Installation](#installation)

\- \[Configuration](#configuration)

\- \[Lancement](#lancement)

\- \[Utilisation](#utilisation)

\- \[Structure du projet](#structure-du-projet)

\- \[API](#api)

\- \[Organisation de l'équipe](#organisation-de-léquipe)

\- \[Workflow Git](#workflow-git)

\- \[Dépannage](#dépannage)

\- \[Feuille de route](#feuille-de-route)

\- \[Équipe](#équipe)



\---



\## Aperçu



Les équipes de sécurité opérationnelle (SOC) passent une part importante de leur temps sur deux tâches répétitives : analyser des e-mails suspects et vérifier des indicateurs de compromission (IP, domaines, URLs, empreintes de fichiers). Ces opérations sont souvent réalisées manuellement, en jonglant entre plusieurs outils et services en ligne.



\*\*BaitWay\*\* centralise ces deux fonctions dans une interface web unique. Un analyste soumet un e-mail suspect ou un indicateur, et obtient un score de risque et un verdict instantanés, enrichis à partir de plusieurs sources de threat intelligence.



Le projet est développé dans le cadre d'un stage à l'\*\*ESPRIM\*\* (École Supérieure Privée d'Ingénieurs de Monastir), avec une architecture modulaire conçue pour un développement en binôme.



\---



\## Fonctionnalités



\### Module A — Portail d'analyse de phishing

\- Soumission d'e-mails suspects (format `.eml`, copier-coller ou téléversement)

\- Analyse automatique des en-têtes : SPF, DKIM, DMARC, incohérences From/Reply-To, IP d'origine

\- Extraction et analyse des URLs : défang, détection de raccourcisseurs et de domaines sosies, réputation

\- Analyse des pièces jointes : empreintes MD5/SHA256, réputation, extensions dangereuses

\- Calcul d'un score de risque (0–100) et d'un verdict (Sain / Suspect / Malveillant)

\- File de triage triée par risque et gestion des verdicts par l'analyste



\### Module B — Recherche d'IOC \& Threat Intel

\- Soumission d'un indicateur (IP, domaine, URL, hash) avec détection automatique du type

\- Enrichissement multi-sources : VirusTotal, AbuseIPDB, URLhaus, MalwareBazaar, WHOIS, géolocalisation

\- Agrégation des sources en un verdict de risque unique

\- Mise en cache des résultats pour respecter les quotas d'API

\- Historique de recherche et export des indicateurs (CSV / liste noire)



\### Socle commun

\- Authentification par JWT avec gestion de rôles (analyste / administrateur)

\- Tableau de bord unifié et navigation entre les modules

\- Documentation d'API auto-générée (OpenAPI / Swagger)



\---



\## Architecture



```

┌─────────────────────────────────────────────────────────┐

│                    Navigateur (Analyste)                  │

│                   http://localhost:5173                   │

└───────────────────────────┬─────────────────────────────┘

&#x20;                           │  HTTP + JWT

┌───────────────────────────▼─────────────────────────────┐

│                   Frontend — React (Vite)                 │

│   App shell · Login · Dashboard · Module A · Module B     │

└───────────────────────────┬─────────────────────────────┘

&#x20;                           │  API REST

┌───────────────────────────▼─────────────────────────────┐

│                   Backend — FastAPI                       │

│   /auth/\*   ·   /phishing/\*   ·   /ioc/\*                   │

│   Auth JWT · Moteurs d'analyse · Enrichissement           │

└──────────┬──────────────────────────────┬───────────────┘

&#x20;          │                              │

┌──────────▼──────────┐      ┌────────────▼────────────────┐

│  PostgreSQL (Docker)│      │  APIs Threat Intel externes  │

│    port 5433        │      │  VirusTotal, AbuseIPDB, ...   │

└─────────────────────┘      └─────────────────────────────┘

```



\---



\## Stack technique



| Couche | Technologie | Rôle |

|---|---|---|

| Backend | Python 3.11+ / FastAPI | API REST, moteurs d'analyse et d'enrichissement |

| Frontend | React 18 (Vite) | Interfaces des deux modules et app shell |

| Base de données | PostgreSQL 16 | Persistance (utilisateurs, analyses, historiques) |

| ORM / Migrations | SQLAlchemy + Alembic | Modélisation et versionnement du schéma |

| Authentification | JWT (python-jose) + passlib/bcrypt | Sessions et rôles |

| Conteneurisation | Docker Compose | Base de données isolée et reproductible |

| Client HTTP (front) | Axios | Communication avec l'API |

| Routing (front) | React Router | Navigation et protection des routes |



\---



\## Prérequis



Avant de commencer, assure-toi d'avoir installé :



| Outil | Version minimale | Vérification |

|---|---|---|

| \[Python](https://www.python.org/downloads/) | 3.11 | `python --version` |

| \[Node.js](https://nodejs.org/) | 18 | `node --version` |

| \[Docker Desktop](https://www.docker.com/products/docker-desktop/) | récent | `docker --version` |

| \[Git](https://git-scm.com/) | récent | `git --version` |



> \*\*Windows :\*\* Docker Desktop nécessite WSL2 activé. Les commandes de ce README sont données pour `cmd.exe`.



\---



\## Installation



\### 1. Cloner le dépôt



```cmd

git clone https://github.com/Givemeboga/Baitway.git

cd Baitway

```



\### 2. Lancer la base de données



Assure-toi que \*\*Docker Desktop est démarré\*\*, puis :



```cmd

docker compose up -d db

```



Vérifie que le conteneur tourne :

```cmd

docker compose ps

```



> \*\*Note importante sur le port :\*\* la base est exposée sur le port \*\*5433\*\* (et non 5432 par défaut) pour éviter les conflits avec une éventuelle installation PostgreSQL locale. Si tu as déjà un PostgreSQL natif sur 5433, modifie le port dans `docker-compose.yml` et dans ton `.env`.



\### 3. Configurer le backend



```cmd

cd backend

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

```



Crée ton fichier de configuration à partir de l'exemple :

```cmd

copy .env.example .env

```



Ouvre `.env` et ajuste les valeurs si nécessaire (notamment `JWT\_SECRET` — voir \[Configuration](#configuration)).



Applique les migrations de la base :

```cmd

alembic upgrade head

```



\### 4. Configurer le frontend



Dans un nouveau terminal :

```cmd

cd Baitway\\frontend

npm install

```



\---



\## Configuration



Le backend se configure via un fichier `backend/.env`. Ne le committe \*\*jamais\*\* (il est ignoré par Git).



```env

\# Connexion à la base de données (port 5433 par défaut)

DATABASE\_URL=postgresql://baitway\_admin:baitway\_password@localhost:5433/baitway



\# Sécurité JWT — CHANGE cette clé pour une valeur aléatoire longue

JWT\_SECRET=remplace\_par\_une\_cle\_secrete

JWT\_ALGORITHM=HS256

JWT\_EXPIRE\_MINUTES=60

```



> \*\*Générer une clé secrète solide :\*\*

> ```cmd

> python -c "import secrets; print(secrets.token\_urlsafe(32))"

> ```

> Colle le résultat dans `JWT\_SECRET`.



Les clés d'API des services de threat intelligence (VirusTotal, AbuseIPDB, etc.) seront ajoutées à ce fichier au fur et à mesure du développement des modules.



\---



\## Lancement



Il faut \*\*deux terminaux\*\* ouverts simultanément.



\### Terminal 1 — Base de données (si pas déjà lancée)

```cmd

docker compose up -d db

```



\### Terminal 2 — Backend

```cmd

cd backend

venv\\Scripts\\activate

uvicorn app.main:app --reload

```

Le backend tourne sur \*\*http://localhost:8000\*\*

Documentation interactive : \*\*http://localhost:8000/docs\*\*



\### Terminal 3 — Frontend

```cmd

cd frontend

npm run dev

```

Le frontend tourne sur \*\*http://localhost:5173\*\*



\---



\## Utilisation



\### Créer un compte

Comme il n'existe pas encore d'interface d'inscription, crée ton premier compte via la documentation Swagger :



1\. Ouvre \*\*http://localhost:8000/docs\*\*

2\. Déplie `POST /auth/register` → \*\*Try it out\*\*

3\. Renseigne un `email` et un `password`, puis \*\*Execute\*\*

4\. Tu dois recevoir `{"message": "Utilisateur cree"}`



\### Se connecter

1\. Ouvre \*\*http://localhost:5173\*\*

2\. Connecte-toi avec les identifiants créés

3\. Tu arrives sur le tableau de bord, avec accès aux deux modules dans la barre latérale



\---



\## Structure du projet



```

baitway/

├── backend/

│   ├── app/

│   │   ├── core/

│   │   │   ├── config.py         # Configuration (lecture du .env)

│   │   │   ├── database.py        # Connexion SQLAlchemy

│   │   │   ├── security.py        # Hachage \& JWT

│   │   │   └── deps.py            # Dépendances (auth, rôles)

│   │   ├── models/

│   │   │   └── user.py            # Modèle User

│   │   ├── routers/

│   │   │   ├── auth.py            # Routes /auth

│   │   │   ├── phishing.py        # Routes /phishing (Youssef)

│   │   │   └── ioc.py             # Routes /ioc (Iheb)

│   │   ├── schemas/               # Schémas Pydantic

│   │   └── main.py               # Point d'entrée FastAPI

│   ├── migrations/               # Migrations Alembic

│   ├── .env.example              # Modèle de configuration

│   ├── alembic.ini

│   └── requirements.txt

│

├── frontend/

│   └── src/

│       ├── context/

│       │   └── AuthContext.jsx   # Gestion du token JWT

│       ├── api/

│       │   └── client.js         # Client Axios (intercepteur JWT)

│       ├── components/

│       │   ├── Sidebar.jsx

│       │   └── ProtectedRoute.jsx

│       ├── pages/

│       │   ├── Login.jsx

│       │   ├── Dashboard.jsx

│       │   ├── phishing/         # Écrans Module A (Youssef)

│       │   └── ioc/              # Écrans Module B (Iheb)

│       ├── App.jsx              # Routing principal

│       └── main.jsx             # AuthProvider + montage

│

├── docs/

│   └── api-contract.md          # Contrat d'API partagé

├── docker-compose.yml

├── .gitignore

└── README.md

```



\---



\## API



La documentation interactive complète est disponible sur \*\*http://localhost:8000/docs\*\* une fois le backend lancé.



Le contrat d'API détaillé (schémas de requêtes/réponses des deux modules, conventions communes) est documenté dans \[`docs/api-contract.md`](docs/api-contract.md).



\### Aperçu des endpoints



| Méthode | Endpoint | Description | Auth |

|---|---|---|---|

| GET | `/health` | Vérification de l'état du serveur | Non |

| POST | `/auth/register` | Créer un compte | Non |

| POST | `/auth/login` | Se connecter (renvoie un JWT) | Non |

| POST | `/phishing/analyze` | Analyser un e-mail | Oui |

| GET | `/phishing/submissions` | File de triage | Oui |

| GET | `/phishing/submissions/{id}` | Détail d'une soumission | Oui |

| PATCH | `/phishing/submissions/{id}` | Mettre à jour un verdict | Oui |

| POST | `/ioc/lookup` | Enrichir un indicateur | Oui |

| GET | `/ioc/history` | Historique des recherches | Oui |

| GET | `/ioc/lookups/{id}` | Détail d'une recherche | Oui |

| GET | `/ioc/export` | Exporter les indicateurs | Oui |



\---



\## Organisation de l'équipe



Le projet est développé en binôme, chacun responsable d'un module complet (moteur + interface).



| Périmètre | Responsable | Branche |

|---|---|---|

| Socle commun | Youssef \& Iheb | `main` / `develop` |

| Module A — Portail Phishing | \*\*Youssef Ben Chaouacha\*\* | `feature/phishing-module` |

| Module B — Recherche d'IOC | \*\*Iheb Ben Massaoud\*\* | `feature/ioc-module` |

| Intégration finale | Youssef \& Iheb | `develop` → `main` |



\---



\## Workflow Git



\- La branche `main` ne contient que des versions stables.

\- La branche `develop` sert d'intégration entre les modules.

\- Chaque membre travaille sur sa branche `feature/\*` et ouvre une \*\*Pull Request vers `develop`\*\*, relue par l'autre avant fusion.

\- Personne ne commit directement sur `main` ou `develop`.



\### Convention de commits

Format \[Conventional Commits](https://www.conventionalcommits.org/) :

```

feat:  nouvelle fonctionnalité

fix:   correction de bug

docs:  documentation

chore: tâches diverses (config, dépendances)

refactor: refactorisation sans changement de comportement

```



\### Démarrer sur son module

```cmd

git checkout develop

git pull

git checkout -b feature/phishing-module   # ou feature/ioc-module

```



\---



\## Dépannage



<details>

<summary><strong>« password authentication failed for user "baitway\_admin" »</strong></summary>



Un autre PostgreSQL écoute probablement sur le même port. Vérifie :

```cmd

netstat -ano | findstr :5433

```

Si plusieurs processus apparaissent, change le port exposé dans `docker-compose.yml` (ex. `5434:5432`) et mets à jour `DATABASE\_URL` dans `.env`. Puis :

```cmd

docker compose down -v

docker compose up -d db

alembic upgrade head

```

</details>



<details>

<summary><strong>Erreur 500 à l'inscription (bcrypt)</strong></summary>



Incompatibilité connue entre `passlib` et les versions récentes de `bcrypt`. Fixe la version :

```cmd

pip install "bcrypt==4.0.1"

pip freeze > requirements.txt

```

</details>



<details>

<summary><strong>« blocked by CORS policy » dans la console du navigateur</strong></summary>



Le backend doit autoriser l'origine du frontend. Vérifie que `app/main.py` contient le middleware CORS avec `allow\_origins=\["http://localhost:5173"]`, puis redémarre uvicorn.

</details>



<details>

<summary><strong>La migration Alembic ne crée aucune table</strong></summary>



Le modèle n'est pas importé dans `migrations/env.py`. Assure-toi d'y avoir `from app.models.user import User` et `target\_metadata = Base.metadata`, puis régénère :

```cmd

alembic revision --autogenerate -m "creation table users"

alembic upgrade head

```

</details>



<details>

<summary><strong>« python » ou « docker » non reconnu</strong></summary>



L'outil n'est pas dans le PATH. Réinstalle-le en cochant « Add to PATH », ou redémarre le terminal après installation.

</details>



\---



\## Feuille de route



\- \[x] \*\*Phase 0 — Socle commun\*\* : auth JWT, base de données, app shell, contrat d'API

\- \[ ] \*\*Phase 1 — Moteurs\*\* : développement parallèle des moteurs d'analyse (données mockées)

\- \[ ] \*\*Phase 2 — Interfaces\*\* : développement parallèle des interfaces

\- \[ ] \*\*Phase 3 — Intégration\*\* : tableau de bord unifié, lien inter-modules, tests

\- \[ ] \*\*Phase 4 — Optionnel\*\* : scoring ML, export avancé, génération de rapports PDF



\---



\## Équipe



| | |

|---|---|

| \*\*Youssef Ben Chaouacha\*\* | Module A — Portail d'analyse de phishing |

| \*\*Iheb Ben Massaoud\*\* | Module B — Recherche d'IOC \& Threat Intel |



Projet de stage — \*\*ESPRIM\*\* (École Supérieure Privée d'Ingénieurs de Monastir)



\---



\## Licence



Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

