<div align="center">

<img src="docs/assets/hero.png" alt="BaitWay — Analyze. Investigate. Triage. Phishing analysis and multi-source IOC intelligence for fast triage." width="100%"/>

# 🎣 BaitWay

**SOC analysis platform — Phishing Portal & IOC Lookup**

Two core SOC tasks brought together in a single interface: automated phishing
email analysis and indicator-of-compromise lookup.

<br/>

![status](https://img.shields.io/badge/status-in%20development-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

`Phishing Analysis` • `IOC Lookup` • `Threat Intelligence` • `Blue Team`

<br/>

[Overview](#-overview) ·
[Features](#-features) ·
[Architecture](#️-architecture) ·
[Installation](#-installation) ·
[Running the app](#️-running-the-app) ·
[API](#-api) ·
[Team](#-team)

</div>

---

## 📖 Overview

Security Operations Center (SOC) teams spend a significant share of their time on two repetitive tasks: analysing suspicious emails and checking indicators of compromise (IPs, domains, URLs, file hashes). These operations are often performed manually, juggling several tools and online services.

**BaitWay** brings both functions together in a single web interface. An analyst submits a suspicious email or an indicator and gets an instant **risk score** and **verdict**, enriched from multiple threat intelligence sources.

> [!NOTE]
> Project built during an internship at **ESPRIM** (École Supérieure Privée d'Ingénieurs de Monastir), with a modular architecture designed for pair development.

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🎣 Module A — Phishing Portal

![Module A](https://img.shields.io/badge/status-operational-34D399?style=flat-square)

- 📥 `.eml` email submission (paste raw content)
- 📨 **Headers** — SPF, DKIM, DMARC, Reply-To mismatch, display-name spoofing, originating IP
- 🔗 **URLs** — defanging, shorteners, typosquatting, punycode, raw-IP hosts, risky TLDs
- 📎 **Attachments** — MD5/SHA256, dangerous & double extensions, macros, archives
- 📝 **Content** — urgency, threats, credential requests, financial bait (FR + EN)
- 🎯 Weighted scoring → risk score **0–100** + verdict
- 📋 Triage queue sorted by risk, analyst verdict workflow

</td>
<td width="50%" valign="top">

### 🔍 Module B — IOC Lookup

![Module B](https://img.shields.io/badge/status-in%20development-F5A524?style=flat-square)

- 🧩 Automatic type detection (IP / domain / URL / hash)
- 🌐 **Multi-source** — VirusTotal, AbuseIPDB, URLhaus, MalwareBazaar, WHOIS
- ⚖️ Aggregation into a single verdict
- ⚡ Caching (respects API quotas)
- 🕓 Search history
- 📤 CSV / blocklist export

</td>
</tr>
</table>

**🛡️ Shared foundation** — JWT authentication · Analyst/admin roles · Unified dashboard · OpenAPI documentation

Both modules share the same verdict scale:

| Verdict | Score | Meaning |
|---|---|---|
| 🟢 `clean` | 0–30 | No sign of malicious activity |
| 🟠 `suspicious` | 31–70 | Questionable indicators, needs review |
| 🔴 `malicious` | 71–100 | Confirmed malicious |

---

## 🧠 Phishing analysis engine

`POST /phishing/analyze` runs a raw `.eml` through five analysis passes, then a weighted
scoring stage. Everything is computed locally — no external API keys required.

```
.eml ──▶ parser ──▶ headers ──▶ URLs ──▶ attachments ──▶ content ──▶ scoring ──▶ verdict
```

| Pass | Module | Detects |
|---|---|---|
| **Parse** | `parser.py` | headers, text/HTML bodies, attachments |
| **Headers** | `headers.py` | SPF/DKIM/DMARC results, Reply-To mismatch, spoofed display name, originating IP |
| **URLs** | `urls.py` | shorteners, typosquatting (homoglyphs + edit distance), punycode, raw-IP hosts, `@` obfuscation, credential paths, risky TLDs |
| **Attachments** | `attachments.py` | MD5/SHA256, executable & double extensions, macro-enabled documents, archives |
| **Content** | `content.py` | urgency, threats, credential requests, financial bait — French **and** English |
| **Scoring** | `scoring.py` | weighted signals, diminishing returns on repeats, → 0–100 → verdict |

Each signal carries a weight and a human-readable reason, so every score is explainable:

```
+30  url_typosquat                0oredoo.tn imitates ooredoo.tn
+30  attachment_dangerous         Executable extension (urgent_invoice.pdf.exe)
+15  auth_spf_fail                SPF check failed
+12  content_credentials          Request for credentials or personal data
```

> [!NOTE]
> Attachments are **never executed or written to disk** — they are only hashed in memory.
> URL reputation is heuristic and local; external threat-intelligence enrichment belongs to Module B.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    U[👤 SOC Analyst] --> FE[⚛️ React / Vite Frontend]
    FE -->|Axios + JWT| API[⚡ FastAPI Backend]

    subgraph Backend
        API --> AUTH[🔐 JWT Auth]
        API --> PH[🎣 Phishing Engine]
        API --> IOC[🔍 IOC Engine]
    end

    AUTH --> DB[(🐘 PostgreSQL)]
    PH --> DB
    IOC --> DB

    IOC -.->|enrichment| TI[🌐 Threat Intelligence<br/>VirusTotal · AbuseIPDB · URLhaus]
```

### 🧰 Tech stack

| Layer | Technology | Role |
|---|---|---|
| **Backend** | Python 3.11+ · FastAPI | REST API, analysis engines |
| **Frontend** | React 18 · Vite | Interfaces & app shell |
| **Database** | PostgreSQL 16 | Data persistence |
| **ORM / Migrations** | SQLAlchemy · Alembic | Schema modelling & versioning |
| **Auth** | JWT (python-jose) · bcrypt | Sessions & roles |
| **Containerisation** | Docker Compose | Isolated database |
| **HTTP client / Routing** | Axios · React Router | API communication & navigation |

---

## ⚙️ Prerequisites

| Tool | Min. version | Check |
|---|---|---|
| ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white) | 3.11 | `python --version` |
| ![Node](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodedotjs&logoColor=white) | 18 | `node --version` |
| ![Docker](https://img.shields.io/badge/Docker-recent-2496ED?style=flat-square&logo=docker&logoColor=white) | recent | `docker --version` |
| ![Git](https://img.shields.io/badge/Git-recent-F05032?style=flat-square&logo=git&logoColor=white) | recent | `git --version` |

> [!IMPORTANT]
> On Windows, Docker Desktop requires **WSL2** to be enabled. The commands in this README are written for `cmd.exe`.

---

## 🚀 Installation

### 1️⃣ Clone the repository

```cmd
git clone https://github.com/Givemeboga/Baitway.git
cd Baitway
```

### 2️⃣ Start the database

Docker Desktop must be running.

```cmd
docker compose up -d db
docker compose ps
```

> [!WARNING]
> The database is exposed on port **5433** (not 5432) to avoid conflicts with a local PostgreSQL instance. If 5433 is already taken, change the port in `docker-compose.yml` **and** in `.env`.

### 3️⃣ Set up the backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
```

### 4️⃣ Set up the frontend

```cmd
cd ..\frontend
npm install
```

---

## 🔧 Configuration

The backend is configured through `backend/.env` (Git-ignored — **never commit it**).

```env
DATABASE_URL=postgresql://baitway_admin:baitway_password@localhost:5433/baitway
JWT_SECRET=replace_with_a_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

> [!TIP]
> Generate a strong secret key:
>
> ```cmd
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

---

## ▶️ Running the app

Three terminals, in parallel:

<table>
<tr><td><strong>🐘 Database</strong></td><td>

```cmd
docker compose up -d db
```

</td></tr>
<tr><td><strong>⚡ Backend</strong></td><td>

```cmd
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

→ http://localhost:8000 · docs: `/docs`

</td></tr>
<tr><td><strong>⚛️ Frontend</strong></td><td>

```cmd
cd frontend
npm run dev
```

→ http://localhost:5173

</td></tr>
</table>

---

## 🎮 Usage

**Create an account** (no sign-up UI yet):

1. Open http://localhost:8000/docs
2. `POST /auth/register` → **Try it out** → fill in `email` + `password` → **Execute**
3. Expected response: `{"message": "Utilisateur cree"}`

**Load demo data** (optional, from `backend/` with the venv active):

```cmd
python -m scripts.seed_phishing
```

Inserts three example submissions covering all three verdicts. The script is idempotent.

**Log in and analyse**:

1. Open http://localhost:5173 and sign in → the dashboard shows the triage queue
2. Go to **Phishing Portal**, paste the raw content of a `.eml` file, and click **Analyze email**
3. The detail view opens with the verdict, header authentication, defanged URLs,
   attachment hashes and the extracted indicators
4. Use **Mark reviewed** / **Mark resolved** and the notes field to record your decision
5. **Investigate →** on any indicator hands it over to the IOC module

---

## 📂 Project structure

```
baitway/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 core/
│   │   │   ├── 📄 config · database · security · deps
│   │   │   └── 📁 phishing/  → analysis engine (parser, headers, urls,
│   │   │                        attachments, content, scoring, engine)
│   │   ├── 📁 models/        → user.py · phishing.py
│   │   ├── 📁 routers/       → auth · phishing (Youssef) · ioc (Iheb)
│   │   ├── 📁 schemas/       → Pydantic schemas
│   │   └── 📄 main.py        → FastAPI entry point
│   ├── 📁 migrations/        → Alembic migrations
│   ├── 📁 scripts/           → seed_phishing.py (demo data)
│   ├── 📄 .env.example
│   └── 📄 requirements.txt
│
├── 📁 frontend/
│   └── 📁 src/
│       ├── 📄 theme.js       → design tokens (colors, typography, spacing)
│       ├── 📁 lib/           → verdict scale · JWT claims · breakpoints
│       ├── 📁 api/           → client.js (Axios + JWT) · phishing.js · errors.js
│       ├── 📁 context/       → AuthContext.jsx
│       ├── 📁 components/    → AppShell · Sidebar · Logo · ProtectedRoute · ui/
│       ├── 📁 pages/         → Login · Dashboard · phishing/ · ioc/
│       ├── 📄 App.jsx        → routing
│       └── 📄 main.jsx       → AuthProvider
│
├── 📁 docs/
│   ├── 📄 api-contract.md    → shared API contract
│   └── 📁 assets/            → README images
├── 📄 docker-compose.yml
├── 📄 LICENSE
└── 📄 README.md
```

---

## 🔌 API

Full interactive documentation: http://localhost:8000/docs
Detailed contract: [`docs/api-contract.md`](docs/api-contract.md)

| Method | Endpoint | Description | 🔒 | Status |
|---|---|---|:---:|:---:|
| `GET` | `/health` | Server status | — | ✅ live |
| `POST` | `/auth/register` | Create an account | — | ✅ live |
| `POST` | `/auth/login` | Log in (JWT) | — | ✅ live |
| `POST` | `/phishing/analyze` | Analyse an email | ✅ | ✅ live |
| `GET` | `/phishing/submissions` | Triage queue | ✅ | ✅ live |
| `GET` | `/phishing/submissions/{id}` | Submission details | ✅ | ✅ live |
| `PATCH` | `/phishing/submissions/{id}` | Update a verdict | ✅ | ✅ live |
| `POST` | `/ioc/lookup` | Enrich an indicator | ✅ | 🚧 planned |
| `GET` | `/ioc/history` | Search history | ✅ | 🚧 planned |
| `GET` | `/ioc/lookups/{id}` | Lookup details | ✅ | 🚧 planned |
| `GET` | `/ioc/export` | Export indicators | ✅ | 🚧 planned |

**App routes** — `/login` · `/dashboard` · `/phishing` · `/phishing/:id` · `/ioc`

---

## 👥 Team organisation & Git workflow

| Scope | Owner | Branch |
|---|---|---|
| 🛡️ Shared foundation | Youssef & Iheb | `main` / `develop` |
| 🎣 Module A — Phishing | Youssef Ben Chaouacha | `feature/phishing-module` |
| 🔍 Module B — IOC | Iheb Ben Massaoud | `feature/ioc-module` |
| 🔗 Integration | Youssef & Iheb | `develop` → `main` |

**Rules:** `main` = stable only · `develop` = integration · every feature goes through a Pull Request reviewed by the other · **never commit directly to `main`/`develop`**.

**Commits** ([Conventional Commits](https://www.conventionalcommits.org/)): `feat:` · `fix:` · `docs:` · `chore:` · `refactor:`

```cmd
git checkout develop && git pull
git checkout -b feature/phishing-module
```

---

## 🩺 Troubleshooting

<details>
<summary><strong>❌ "password authentication failed for user 'baitway_admin'"</strong></summary>

<br/>

Another PostgreSQL instance is listening on the port. Check with:

```cmd
netstat -ano | findstr :5433
```

If several processes show up, change the port in `docker-compose.yml` (e.g. `5434:5432`), update `DATABASE_URL`, then:

```cmd
docker compose down -v
docker compose up -d db
alembic upgrade head
```

</details>

<details>
<summary><strong>❌ HTTP 500 on registration (bcrypt)</strong></summary>

<br/>

passlib / recent bcrypt incompatibility. Pin the version:

```cmd
pip install "bcrypt==4.0.1"
pip freeze > requirements.txt
```

</details>

<details>
<summary><strong>❌ "blocked by CORS policy"</strong></summary>

<br/>

Check that `app/main.py` includes the CORS middleware with `allow_origins=["http://localhost:5173"]`, then restart uvicorn.

</details>

<details>
<summary><strong>❌ The Alembic migration creates no tables</strong></summary>

<br/>

The model is not imported in `migrations/env.py`. Add `from app.models.user import User` and `target_metadata = Base.metadata`, then:

```cmd
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

</details>

<details>
<summary><strong>❌ "python" or "docker" is not recognised</strong></summary>

<br/>

The tool is not in your PATH. Reinstall it with "Add to PATH" checked, or restart your terminal.

</details>

---

## 🗺️ Roadmap

- [x] **Phase 0 — Shared foundation** · JWT auth · database · app shell · API contract
- [ ] **Phase 1 — Engines** · parallel development
  - [x] Module A — `.eml` analysis engine, persistence, weighted scoring
  - [ ] Module B — IOC enrichment across threat-intelligence sources
- [ ] **Phase 2 — Interfaces** · parallel UI development
  - [x] Module A — submission form, triage queue, detail view, verdict workflow
  - [ ] Module B — lookup form, sources, history
- [ ] **Phase 3 — Integration** · unified dashboard · cross-module linking · tests
- [ ] **Phase 4 — Bonus** · ML scoring · advanced export · PDF reports

---

## 👨‍💻 Team

<table>
<tr>
<td align="center" width="50%">
<strong>Youssef Ben Chaouacha</strong><br/>
🎣 Module A — Phishing Portal
</td>
<td align="center" width="50%">
<strong>Iheb Ben Massaoud</strong><br/>
🔍 Module B — IOC Lookup
</td>
</tr>
</table>

<div align="center">

Internship project · **ESPRIM** — École Supérieure Privée d'Ingénieurs de Monastir

</div>

---

## 📄 License

Released under the **MIT** License. See [`LICENSE`](LICENSE) for details.

<div align="center">
<br/>
Made with ☕ by Youssef & Iheb
</div>
