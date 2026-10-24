<div align="center">

<img src="docs/assets/hero.png" alt="BaitWay — Analyze. Investigate. Triage. Phishing analysis and multi-source IOC intelligence for fast triage." width="100%"/>

# 🎣 BaitWay

**A SOC analysis platform — phishing triage and multi-source IOC intelligence**

Two of the most repetitive jobs in a Security Operations Centre, brought into
one interface: working out whether a reported email is phishing, and finding
out what is already known about an indicator of compromise.

<br/>

![release](https://img.shields.io/badge/release-v1.0.1-6366F1?style=flat-square)
![status](https://img.shields.io/badge/status-both%20modules%20operational-34D399?style=flat-square)
![tests](https://img.shields.io/badge/tests-55%20passing-34D399?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

`Phishing Analysis` • `IOC Lookup` • `Threat Intelligence` • `Blue Team`

<br/>

**Start here** &nbsp;·&nbsp;
[The problem](#-the-problem) ·
[How it came about](#-how-it-came-about) ·
[Quick start](#-quick-start)

**Reference** &nbsp;·&nbsp;
[Module A](#-module-a--phishing-portal) ·
[Module B](#-module-b--ioc-lookup) ·
[Architecture](#-architecture) ·
[Testing](#-testing) ·
[API](#-api) ·
[Troubleshooting](#-troubleshooting)

</div>

---

## 📖 The problem

When someone forwards a suspicious email to the security team, an analyst opens
it and starts working through it by hand. Read the technical headers. Copy each
URL into an online scanner. Hash the attachments. Check the sender domain on one
threat-intelligence site, the originating IP on another.

It takes several minutes per message, the answer depends on who happens to be
looking, and when it is over nothing is written down. The next analyst who sees
the same indicator starts again from nothing.

**BaitWay** collapses that into a single pass. An analyst submits a raw email or
a bare indicator and immediately gets a **risk score**, a **verdict**, and — the
part that matters — **the list of signals that produced them**, so the reasoning
can be audited rather than trusted.

Both modules answer on the same scale:

| Verdict | Score | Meaning |
|:---|:---:|:---|
| 🟢 `clean` | 0–30 | No sign of malicious activity |
| 🟠 `suspicious` | 31–70 | Questionable indicators, needs review |
| 🔴 `malicious` | 71–100 | Confirmed malicious |

> [!NOTE]
> **`unknown` is never treated as `clean`.** A source with nothing to report is
> excluded from the verdict rather than counted as a zero. An indicator nobody
> has reported yet is not a safe indicator — it is an unknown one, and the
> difference matters most exactly when an indicator is new.

---

## 🎓 How it came about

BaitWay was built during a two-month technician internship at
**VadaSoft**, a software development and IT services company in Monastir,
Tunisia, running from **1 July to 31 August 2026**. Both of us are students at
**ESPRIM** (École Supérieure Privée d'Ingénieurs de Monastir). The internship
was supervised directly by **Mr Nacef Sayed**, the company's manager.

The brief was open: build something useful for a SOC. We were two interns, which
shaped every structural decision that followed.

**The project was split into two modules so that two people could work at full
speed without waiting on each other.** One handles reported emails, the other
handles indicators. They share a database, an authentication layer, a verdict
scale and a visual system — and nothing else.

**The API contract was written and agreed before a single line of application
code.** That one decision is why the parallel work converged at the end without
renegotiation: each of us built against a document, not against the other's
half-finished code. It lives at [`docs/api-contract.md`](docs/api-contract.md)
and neither of us was allowed to change it alone.

There was no in-house stack or coding standard to inherit, so every technical
choice here had to be argued from first principles rather than adopted by
default. Where a decision was non-obvious, the reasoning is recorded in this
README rather than left implicit.

| | |
|:---|:---|
| **Host company** | VadaSoft — software development & IT services, Monastir |
| **Supervisor** | Mr Nacef Sayed, Manager |
| **Period** | 1 July – 31 August 2026 |
| **School** | ESPRIM, Monastir |
| **Team** | Youssef Ben Chaouacha (Module A) · Iheb Ben Massaoud (Module B) |

---

## 🎣 Module A — Phishing Portal

![Module A](https://img.shields.io/badge/status-operational-34D399?style=flat-square)
![keys](https://img.shields.io/badge/API%20keys-none%20required-34D399?style=flat-square)

`POST /phishing/analyze` takes the raw text of an `.eml` file and runs it through
five independent passes, then a single weighted scoring stage.

```
.eml ──▶ parse ──▶ headers ──▶ URLs ──▶ attachments ──▶ content ──▶ scoring ──▶ verdict
```

| Pass | Module | What it looks for |
|:---|:---|:---|
| **Parse** | `parser.py` | headers, plain-text and HTML bodies, attachments |
| **Headers** | `headers.py` | SPF/DKIM/DMARC results, Reply-To vs From divergence, spoofed display name, originating IP |
| **URLs** | `urls.py` | shorteners, typosquatting (homoglyphs + edit distance), punycode, raw-IP hosts, `@` obfuscation, credential paths, risky TLDs |
| **Attachments** | `attachments.py` | MD5/SHA-256, executable and double extensions, macro-enabled documents, archives |
| **Content** | `content.py` | urgency, threats, credential requests, financial bait — French **and** English |
| **Scoring** | `scoring.py` | weighted signals, diminishing returns on repeats → 0–100 → verdict |

**No pass returns a score.** Each returns *signals* — a technical identifier
paired with a human-readable reason. Scoring happens once, at the end, in one
function. That separation keeps the scoring logic in a single place and makes
the explanation of a score free, because every signal already carries its own
justification:

```
+30  url_typosquat          0oredoo.tn imitates ooredoo.tn
+15  auth_spf_fail          SPF verification failed
+12  reply_to_mismatch      Reply-To (mail.ru) differs from From (0oredoo.tn)
+12  content_credentials    Request for credentials or personal data
```

Repeated signals of the same type suffer **diminishing returns** — the second
occurrence counts half, later ones are ignored. Without that, ten shortened URLs
would max out the score on a single kind of evidence.

> [!IMPORTANT]
> Attachments are **never executed and never written to disk**. Their bytes are
> read in memory only, to compute hashes. A tool for analysing malicious mail
> must not become a way to run it.

> [!NOTE]
> Everything here is computed locally. Module A needs **no API keys** and works
> offline. URL and attachment reputation is heuristic by design; external
> enrichment is Module B's job.

---

## 🔍 Module B — IOC Lookup

![Module B](https://img.shields.io/badge/status-operational-34D399?style=flat-square)
![keys](https://img.shields.io/badge/API%20keys-required-F59E0B?style=flat-square)

`POST /ioc/lookup` takes a bare indicator, works out what it is, and queries only
the sources that apply to that type.

```
indicator ──▶ type detection ──▶ cache hit? ──▶ sources ──▶ aggregation ──▶ verdict
```

**Type detection runs most-specific first and refuses to guess.** A 32/40/64
character hex string is a hash; an `http(s)://` prefix is a URL; anything that
parses as an address is an IP; a validated hostname pattern is a domain. Anything
else is **rejected** — a domain is not a blind fallback, because guessing a type
produces a confident answer to a question nobody asked.

| Source | Applies to | API key |
|:---|:---|:---:|
| VirusTotal | IP · domain · URL · hash | required |
| AbuseIPDB | IP | required |
| URLhaus | URL · domain · IP | required |
| MalwareBazaar | hash | required |
| WHOIS / RDAP | domain — registrar, age | — |

At most **three** sources apply to any one indicator, so a lookup showing two or
three results is working correctly:

| Indicator type | Sources queried |
|:---|:---|
| IP | VirusTotal · AbuseIPDB · URLhaus |
| Domain | VirusTotal · URLhaus · WHOIS |
| URL | VirusTotal · URLhaus |
| Hash | VirusTotal · MalwareBazaar |

**Every source returns the same four fields** — `name`, `result`, `score`, `raw`
— so the dispatcher never branches on which provider answered. Adding a provider
means adding one file and one line.

A few decisions worth knowing:

- **URLhaus is queried on two endpoints.** `/url/` for a full URL, `/host/` for
  the domain or IP serving it. A known malicious URL hosted somewhere is evidence
  about that host, which is why URLhaus covers three types rather than one.
- **One abuse.ch key covers both** URLhaus and MalwareBazaar.
- **WHOIS/RDAP always scores `0`** and can never move a verdict — it reports
  registration facts, not reputation. It is still listed among the sources so the
  analyst can see that it ran. A test asserts this.
- **Aggregation takes the highest score**, not the average, among sources that
  actually returned data. Averaging dilutes a single strong signal: one confirmed
  malware hash must not be watered down by four sources that simply had nothing
  to say.

> [!TIP]
> Lookups are cached for **60 minutes**. Repeating an indicator returns the stored
> record without touching a provider, which is what keeps free-tier quotas intact
> through a working day.

> [!NOTE]
> Without API keys the module still runs: keyed sources report `unknown` and are
> excluded from the verdict rather than failing the request. **Only WHOIS/RDAP
> works without a key.**

---

## 🏗 Architecture

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

    IOC -.->|enrichment| TI[🌐 Threat Intelligence<br/>VirusTotal · AbuseIPDB<br/>URLhaus · MalwareBazaar · RDAP]
    PH -.->|extracted indicators| IOC
```

Three tiers, so the interface and the analysis engines can change independently.

| Layer | Technology | Why |
|:---|:---|:---|
| **Backend** | Python 3.11+ · FastAPI | Pydantic validates request data automatically and generates OpenAPI docs, which makes it easy to check the contract is honoured |
| **Frontend** | React 19 · Vite | Reusable components, instant reload |
| **Database** | PostgreSQL 16 | Native JSONB, suited to nested analysis blocks and provider answers of differing shape |
| **ORM / Migrations** | SQLAlchemy · Alembic | Models in Python and a versioned schema — indispensable with two people sharing one database |
| **Auth** | JWT (python-jose) · bcrypt | Self-contained token: the server stays stateless and the client reads the role without another call |
| **HTTP client** | httpx | One timeout-bounded client for every external source, so a slow provider cannot hang a request |
| **Containerisation** | Docker Compose | An identical, isolated database on both machines |

**The nested blocks are stored as JSONB**, not as separate tables. Headers, URLs,
attachments and indicators are always read as a whole, so four tables would mean
four joins on every read for no benefit. Risk score, verdict and status stay
ordinary columns, because sorting cannot work efficiently on a value buried
inside a JSON document.

---

## 🚀 Quick start

### Prerequisites

| Tool | Min. version | Check |
|:---|:---|:---|
| ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white) | 3.11 | `python --version` |
| ![Node](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodedotjs&logoColor=white) | 18 | `node --version` |
| ![Docker](https://img.shields.io/badge/Docker-recent-2496ED?style=flat-square&logo=docker&logoColor=white) | recent | `docker --version` |
| ![Git](https://img.shields.io/badge/Git-recent-F05032?style=flat-square&logo=git&logoColor=white) | recent | `git --version` |

> [!IMPORTANT]
> On Windows, Docker Desktop requires **WSL2**. The commands below are written for
> `cmd.exe`.

### 1 · Clone and start the database

Docker Desktop must be running.

```cmd
git clone https://github.com/Givemeboga/Baitway.git
cd Baitway
docker compose up -d db
docker compose ps
```

> [!WARNING]
> The database is exposed on port **5433**, not 5432, to avoid colliding with a
> local PostgreSQL instance. If 5433 is also taken, change it in
> `docker-compose.yml` **and** in `backend/.env`.

### 2 · Set up the backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
```

### 3 · Set up the frontend

```cmd
cd ..\frontend
npm install
```

### 4 · Configure

Edit `backend/.env` — Git-ignored, **never commit it**:

```env
DATABASE_URL=postgresql://baitway_admin:baitway_password@localhost:5433/baitway
JWT_SECRET=replace_with_a_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Module B — threat-intelligence sources
# Blank is allowed: that source reports "unknown" and is excluded from the verdict.
VIRUSTOTAL_API_KEY=
ABUSEIPDB_API_KEY=
ABUSECH_AUTH_KEY=      # covers URLhaus and MalwareBazaar together
```

> [!TIP]
> Generate a strong secret:
>
> ```cmd
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5 · Run it

Three terminals, in this order:

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

→ http://localhost:8000 · docs at `/docs`

</td></tr>
<tr><td><strong>⚛️ Frontend</strong></td><td>

```cmd
cd frontend
npm run dev
```

→ http://localhost:5173

</td></tr>
</table>

> [!NOTE]
> `ModuleNotFoundError: No module named 'pydantic_settings'` means the virtual
> environment is not active and you are running system Python. Either re-run
> `venv\Scripts\activate`, or skip activation entirely:
> `venv\Scripts\python -m uvicorn app.main:app --reload`

---

## 🎮 First steps

**Create an account** — there is no sign-up screen yet:

1. Open http://localhost:8000/docs
2. `POST /auth/register` → **Try it out** → fill in `email` and `password` → **Execute**
3. Expected: `{"message": "Account created"}`

**Load demo data** (optional, from `backend/` with the venv active):

```cmd
python -m scripts.seed_phishing
```

Inserts three example submissions covering all three verdicts. Idempotent.

**Analyse an email:**

1. Sign in at http://localhost:5173 — the dashboard opens on the triage queue
2. Go to **Phishing Portal**, paste the raw content of an `.eml`, click **Analyze email**
3. The detail view shows the verdict, header authentication, defanged URLs,
   attachment hashes and the extracted indicators
4. Record your decision with **Mark reviewed** / **Mark resolved** and the notes field
5. **Investigate →** on any indicator opens the IOC lookup pre-filled, runs the
   enrichment, and links back to the originating analysis

**Look up an indicator directly:** go to **IOC Lookup** and paste an IP, domain,
URL or hash — the type is detected server-side. Results are cached for an hour,
and the history exports as CSV or as a blocklist.

> [!TIP]
> For a demonstration, look up an **IP or a domain** — those are the two types
> that reach three sources. A URL or a hash reaches two, by design.

---

## 🧪 Testing

A `pytest` suite of **55 tests** runs against a real PostgreSQL instance.

```cmd
cd backend
venv\Scripts\activate
pytest
```

| File | Tests | Covers |
|:---|:---:|:---|
| `test_engine.py` | 21 | Verdict thresholds, defanging, typosquatting, attachments, originating IP, weighting, end-to-end analysis |
| `test_api_contract.py` | 13 | Response shapes, status codes, controlled vocabulary |
| `test_ioc_sources.py` | 11 | Source routing and verdict aggregation for Module B |
| `test_auth.py` | 10 | Registration, sign-in, route protection |

**Continuous integration** runs on every push and pull request
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):

- Backend tests against a genuine **PostgreSQL 16 service container**, not a
  substitute database — JSONB columns do not behave identically elsewhere
- A check that Alembic has **exactly one head**, which catches the divergence two
  developers generating migrations in parallel would otherwise produce
- Frontend lint and production build

> [!NOTE]
> An `autouse` fixture makes any outbound network call raise during the test run,
> so the suite can never quietly reach a live threat-intelligence API and pass for
> the wrong reason.

---

## 🔌 API

Interactive docs: http://localhost:8000/docs · Contract: [`docs/api-contract.md`](docs/api-contract.md)

| Method | Endpoint | Description | 🔒 |
|:---|:---|:---|:---:|
| `GET` | `/health` | Server status | — |
| `POST` | `/auth/register` | Create an account | — |
| `POST` | `/auth/login` | Log in, returns a JWT | — |
| `POST` | `/phishing/analyze` | Analyse a raw email | ✅ |
| `GET` | `/phishing/submissions` | Triage queue, sorted by risk | ✅ |
| `GET` | `/phishing/submissions/{id}` | Submission detail | ✅ |
| `PATCH` | `/phishing/submissions/{id}` | Update verdict, status, notes | ✅ |
| `POST` | `/ioc/lookup` | Enrich an indicator | ✅ |
| `GET` | `/ioc/history` | Lookup history | ✅ |
| `GET` | `/ioc/lookups/{id}` | Lookup detail | ✅ |
| `GET` | `/ioc/export` | Export as CSV or blocklist | ✅ |

**App routes** — `/login` · `/dashboard` · `/phishing` · `/phishing/:id` · `/ioc`

---

## 📂 Project structure

```
baitway/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 core/
│   │   │   ├── 📄 config · database · security · deps
│   │   │   └── 📁 phishing/  → Module A engine (parser, headers, urls,
│   │   │                        attachments, content, scoring, engine)
│   │   ├── 📁 services/      → Module B
│   │   │   ├── 📄 ioc_detector.py   → indicator type detection
│   │   │   ├── 📄 ioc_enrichment.py → which sources for which type
│   │   │   ├── 📄 verdict.py        → score aggregation
│   │   │   └── 📁 enrichment/       → virustotal · abuseipdb · urlhaus
│   │   │                              malwarebazaar · whois_rdap
│   │   ├── 📁 models/        → user.py · phishing.py · ioc.py
│   │   ├── 📁 routers/       → auth · phishing (Youssef) · ioc (Iheb)
│   │   ├── 📁 schemas/       → Pydantic schemas
│   │   └── 📄 main.py        → FastAPI entry point
│   ├── 📁 migrations/        → Alembic migrations
│   ├── 📁 tests/             → pytest suite
│   ├── 📁 scripts/           → seed_phishing.py (demo data)
│   └── 📄 requirements.txt
│
├── 📁 frontend/
│   └── 📁 src/
│       ├── 📄 theme.js       → design tokens (colours, typography, spacing)
│       ├── 📁 lib/           → verdict scale · JWT claims · breakpoints
│       ├── 📁 api/           → client.js (Axios + JWT) · phishing.js · ioc.js
│       ├── 📁 context/       → AuthContext.jsx
│       ├── 📁 components/    → AppShell · Sidebar · Logo · ProtectedRoute · ui/
│       ├── 📁 pages/         → Login · Dashboard · phishing/ · ioc/
│       └── 📄 App.jsx        → routing
│
├── 📁 .github/workflows/     → ci.yml
├── 📁 docs/
│   ├── 📄 api-contract.md    → the shared contract
│   └── 📁 assets/
├── 📄 docker-compose.yml
└── 📄 README.md
```

---

## 🤝 How we worked

| Scope | Owner | Branch |
|:---|:---|:---|
| 🛡️ Shared foundation | Youssef & Iheb | `main` |
| 🎣 Module A — Phishing | Youssef Ben Chaouacha | `feature/phishing-module` |
| 🔍 Module B — IOC | Iheb Ben Massaoud | `feature/ioc-module` |
| 🔗 Integration | Youssef & Iheb | merged to `main` |

Both module branches are merged and released. Development ran under three rules:

- `main` holds stable code only — **never commit to it directly**
- Every feature goes through a Pull Request **reviewed by the other person**
- **Nobody edits `docs/api-contract.md` alone** — it is the one file both modules
  depend on

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:` · `fix:` · `docs:` · `chore:` · `refactor:` · `test:`

```cmd
git checkout main && git pull
git checkout -b feature/my-feature
```

---

## 💡 What we learned

The technical lessons that cost us the most time, kept here because they are the
genuinely transferable part of the project.

**An analysis pipeline can fail without ever throwing an exception.** Three
separate bugs produced silently incomplete results and raised nothing:

- The originating IP came back empty every time. Python's standard library
  classifies the documentation address ranges as private — and those were exactly
  the ranges in our test data.
- Lookalike domains went undetected because the comparison ran against the raw
  domain, which still contained the visual substitution, instead of its normalised
  form.
- Three API keys were configured but only two sources ever appeared. URLhaus was
  being asked only about URLs when it also answers about the host serving them,
  and WHOIS ran but returned nothing the analyst could see. Fixed in **v1.0.1**.

None of these looked like failures. Each was found by comparing what *should*
have happened with what actually did — which is the argument for the test suite
and for showing every source individually instead of only the aggregate.

**A cache will happily show you the past.** After fixing the source-coverage bug
above, the module still looked broken: the indicator used to retest it had a
cached result older than the fix. The fix was correct; the evidence was stale.

**Interfaces between people matter more than volume of code.** The API contract,
written and agreed before any implementation, is the single reason two modules
built in parallel by two people converged at the end without renegotiation.

---

## 🩺 Troubleshooting

<details>
<summary><strong>❌ ModuleNotFoundError: No module named 'pydantic_settings'</strong></summary>

<br/>

The virtual environment is not active, so the command is running under system
Python. Re-activate it, or call the venv's interpreter directly:

```cmd
venv\Scripts\activate
uvicorn app.main:app --reload
```

```cmd
venv\Scripts\python -m uvicorn app.main:app --reload
```

</details>

<details>
<summary><strong>❌ "password authentication failed for user 'baitway_admin'"</strong></summary>

<br/>

Another PostgreSQL instance is listening on the port. Check with:

```cmd
netstat -ano | findstr :5433
```

If several processes show up, change the port in `docker-compose.yml` (e.g.
`5434:5432`), update `DATABASE_URL`, then:

```cmd
docker compose down -v
docker compose up -d db
alembic upgrade head
```

</details>

<details>
<summary><strong>❌ An IOC lookup shows fewer sources than expected</strong></summary>

<br/>

This is usually correct behaviour. At most three sources apply to any indicator:
IP and domain reach three, URL and hash reach two. See the table in
[Module B](#-module-b--ioc-lookup).

If a source you expect is genuinely missing, check in this order: the key is set
in `backend/.env`; the server was restarted after setting it; and the result is
not a **cached** row from before a fix — lookups are cached for 60 minutes, so
retest with a different indicator rather than the same one.

</details>

<details>
<summary><strong>❌ HTTP 500 on registration (bcrypt)</strong></summary>

<br/>

A passlib / recent-bcrypt incompatibility. Pin the version:

```cmd
pip install "bcrypt==4.0.1"
pip freeze > requirements.txt
```

</details>

<details>
<summary><strong>❌ "blocked by CORS policy"</strong></summary>

<br/>

Check that `app/main.py` includes the CORS middleware with
`allow_origins=["http://localhost:5173"]`, then restart uvicorn.

</details>

<details>
<summary><strong>❌ "Multiple head revisions are present" on <code>alembic upgrade head</code></strong></summary>

<br/>

Two branches each added a migration on top of the same parent, so Alembic has two
heads and cannot pick one. List them, then reunite them with a merge revision:

```cmd
alembic heads
alembic merge -m "merge heads" <revision1> <revision2>
alembic upgrade head
```

Commit the generated merge revision — it belongs in the repository like any other
migration. CI fails the build if more than one head exists.

</details>

<details>
<summary><strong>❌ The Alembic migration creates no tables</strong></summary>

<br/>

The model is not imported in `migrations/env.py`. Alembic only detects models
that are actually loaded. Add `from app.models.user import User` and
`target_metadata = Base.metadata`, then:

```cmd
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

</details>

<details>
<summary><strong>❌ "python" or "docker" is not recognised</strong></summary>

<br/>

The tool is not on your PATH. Reinstall it with "Add to PATH" checked, or restart
your terminal.

</details>

---

## 🗺️ Status

| Release | What it added |
|:---|:---|
| **v1.0.0** | Both modules integrated and running together |
| **v1.0.1** | Widened URLhaus coverage to domains and IPs; WHOIS listed among the sources |

- [x] **Phase 0 — Shared foundation** · JWT auth · database · app shell · API contract
- [x] **Phase 1 — Engines** · built in parallel
  - [x] Module A — `.eml` analysis engine, persistence, weighted scoring
  - [x] Module B — IOC enrichment across threat-intelligence sources, caching
- [x] **Phase 2 — Interfaces** · built in parallel
  - [x] Module A — submission form, triage queue, detail view, verdict workflow
  - [x] Module B — lookup form, sources, history, export
- [x] **Phase 3 — Integration**
  - [x] Branches merged, Alembic heads reconciled, both modules running together
  - [x] Phishing → IOC bridge wired end to end
  - [x] Automated test suite in continuous integration
- [ ] **Phase 4 — Next** · automatic enrichment of extracted indicators · ML scoring · PDF reports

The immediate continuation is to enrich extracted indicators automatically, so
the investigation loop closes without the analyst having to ask — from the
reported email through to the enriched indicator.

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

Internship at **VadaSoft**, Monastir · July–August 2026<br/>
Students at **ESPRIM** — École Supérieure Privée d'Ingénieurs de Monastir

</div>

---

## 📄 License

Released under the **MIT** License. See [`LICENSE`](LICENSE) for details.

<div align="center">
<br/>
Made with ☕ by Youssef & Iheb
</div>
