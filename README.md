

Readme · MD
<div align="center"> <img src="https://img.shields.io/badge/-BaitWay-1f3864?style=for-the-badge&labelColor=1f3864&color=2f8f88" alt="BaitWay" height="40"/>
🎣 BaitWay
Plateforme d'analyse SOC — Portail Phishing & Recherche d'IOC
Deux tâches clés d'un SOC, réunies dans une seule interface : l'analyse automatisée d'e-mails de phishing et la recherche d'indicateurs de compromission.

<br> <img src="https://img.shields.io/badge/status-en%20d%C3%A9veloppement-orange?style=flat-square" alt="status"/> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/> <img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React"/> <img src="https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/> <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/> <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/> <br> <br>
Phishing Analysis  •  IOC Lookup  •  Threat Intelligence  •  Blue Team

</div> <br>
<div align="center">
Aperçu · Fonctionnalités · Architecture · Installation · Lancement · API · Équipe

</div>
📖 Aperçu
Les équipes de sécurité opérationnelle (SOC) passent une part importante de leur temps sur deux tâches répétitives : analyser des e-mails suspects et vérifier des indicateurs de compromission (IP, domaines, URLs, empreintes de fichiers). Ces opérations sont souvent réalisées manuellement, en jonglant entre plusieurs outils et services en ligne.

BaitWay centralise ces deux fonctions dans une interface web unique. Un analyste soumet un e-mail suspect ou un indicateur, et obtient un score de risque et un verdict instantanés, enrichis à partir de plusieurs sources de threat intelligence.

[!NOTE] Projet développé dans le cadre d'un stage à l'ESPRIM (École Supérieure Privée d'Ingénieurs de Monastir), avec une architecture modulaire conçue pour un développement en binôme.

<br>
✨ Fonctionnalités
<table> <tr> <td width="50%" valign="top">
🎣 Module A — Portail Phishing
📥 Soumission d'e-mails .eml (copier-coller ou upload)
📨 Analyse des en-têtes — SPF, DKIM, DMARC, From/Reply-To, IP d'origine
🔗 Analyse des URLs — défang, raccourcisseurs, domaines sosies, réputation
📎 Analyse des pièces jointes — MD5/SHA256, extensions dangereuses
🎯 Score de risque 0–100 + verdict
📋 File de triage triée par risque
</td> <td width="50%" valign="top">
🔍 Module B — Recherche d'IOC
🧩 Détection automatique du type (IP / domaine / URL / hash)
🌐 Enrichissement multi-sources — VirusTotal, AbuseIPDB, URLhaus, MalwareBazaar, WHOIS
⚖️ Agrégation en un verdict unique
⚡ Mise en cache (respect des quotas d'API)
🕓 Historique de recherche
📤 Export CSV / liste noire
</td> </tr> </table>
🛡️ Socle commun
Authentification JWT  ·  Rôles analyste/admin  ·  Tableau de bord unifié  ·  Documentation OpenAPI

<br>
🏗️ Architecture
<br>
🧰 Stack technique
Technologie	Rôle
Backend	Python 3.11+ · FastAPI	API REST, moteurs d'analyse
Frontend	React 18 · Vite	Interfaces & app shell
Base de données	PostgreSQL 16	Persistance des données
ORM / Migrations	SQLAlchemy · Alembic	Modélisation & versionnement du schéma
Auth	JWT (python-jose) · bcrypt	Sessions & rôles
Conteneurisation	Docker Compose	Base de données isolée
Client HTTP / Routing	Axios · React Router	Communication API & navigation
<br>
⚙️ Prérequis
Outil	Version min.	Vérification
Show Image	3.11	python --version
Show Image	18	node --version
Show Image	récent	docker --version
Show Image	récent	git --version
[!IMPORTANT] Sous Windows, Docker Desktop nécessite WSL2 activé. Les commandes de ce README sont données pour cmd.exe.

<br>
🚀 Installation
1️⃣ Cloner le dépôt
cmd
git clone https://github.com/Givemeboga/Baitway.git
cd Baitway
2️⃣ Lancer la base de données
Docker Desktop doit être démarré.

cmd
docker compose up -d db
docker compose ps
[!WARNING] La base est exposée sur le port 5433 (et non 5432) pour éviter les conflits avec un PostgreSQL local. Si 5433 est déjà pris, modifie le port dans docker-compose.yml et dans .env.

3️⃣ Configurer le backend
cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
4️⃣ Configurer le frontend
cmd
cd ..\frontend
npm install
<br>
🔧 Configuration
Le backend se configure via backend/.env (ignoré par Git — ne jamais le committer).

env
DATABASE_URL=postgresql://baitway_admin:baitway_password@localhost:5433/baitway
JWT_SECRET=remplace_par_une_cle_secrete
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
[!TIP] Génère une clé secrète solide :

cmd
python -c "import secrets; print(secrets.token_urlsafe(32))"
<br>
▶️ Lancement
Trois terminaux, en parallèle :

<table> <tr> <td><strong>🐘 Base de données</strong></td> <td>
cmd
docker compose up -d db
</td> </tr> <tr> <td><strong>⚡ Backend</strong></td> <td>
cmd
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
→ http://localhost:8000 · docs : /docs

</td> </tr> <tr> <td><strong>⚛️ Frontend</strong></td> <td>
cmd
cd frontend
npm run dev
→ http://localhost:5173

</td> </tr> </table> <br>
🎮 Utilisation
Créer un compte (pas encore d'UI d'inscription) :

Ouvre http://localhost:8000/docs
POST /auth/register → Try it out → renseigne email + password → Execute
Réponse attendue : {"message": "Utilisateur cree"}
Se connecter :

Ouvre http://localhost:5173
Connecte-toi → tu arrives sur le tableau de bord avec les deux modules
<br>
📂 Structure du projet
baitway/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 core/          → config · database · security · deps
│   │   ├── 📁 models/        → user.py
│   │   ├── 📁 routers/       → auth · phishing (Youssef) · ioc (Iheb)
│   │   ├── 📁 schemas/       → schémas Pydantic
│   │   └── 📄 main.py        → point d'entrée FastAPI
│   ├── 📁 migrations/        → migrations Alembic
│   ├── 📄 .env.example
│   └── 📄 requirements.txt
│
├── 📁 frontend/
│   └── 📁 src/
│       ├── 📁 context/       → AuthContext.jsx
│       ├── 📁 api/           → client.js (Axios + JWT)
│       ├── 📁 components/    → Sidebar · ProtectedRoute
│       ├── 📁 pages/         → Login · Dashboard · phishing/ · ioc/
│       ├── 📄 App.jsx        → routing
│       └── 📄 main.jsx       → AuthProvider
│
├── 📁 docs/
│   └── 📄 api-contract.md    → contrat d'API partagé
├── 📄 docker-compose.yml
└── 📄 README.md
<br>
🔌 API
Documentation interactive complète : http://localhost:8000/docs Contrat détaillé : docs/api-contract.md

Méthode	Endpoint	Description	🔒
GET	/health	État du serveur	—
POST	/auth/register	Créer un compte	—
POST	/auth/login	Se connecter (JWT)	—
POST	/phishing/analyze	Analyser un e-mail	✅
GET	/phishing/submissions	File de triage	✅
GET	/phishing/submissions/{id}	Détail d'une soumission	✅
PATCH	/phishing/submissions/{id}	Mettre à jour un verdict	✅
POST	/ioc/lookup	Enrichir un indicateur	✅
GET	/ioc/history	Historique des recherches	✅
GET	/ioc/lookups/{id}	Détail d'une recherche	✅
GET	/ioc/export	Exporter les indicateurs	✅
<br>
👥 Organisation & Workflow Git
Périmètre	Responsable	Branche
🛡️ Socle commun	Youssef & Iheb	main / develop
🎣 Module A — Phishing	Youssef Ben Chaouacha	feature/phishing-module
🔍 Module B — IOC	Iheb Ben Massaoud	feature/ioc-module
🔗 Intégration	Youssef & Iheb	develop → main
Règles : main = stable uniquement · develop = intégration · chaque feature via Pull Request relue par l'autre · jamais de commit direct sur main/develop.

Commits (Conventional Commits) : feat: · fix: · docs: · chore: · refactor:

cmd
git checkout develop && git pull
git checkout -b feature/phishing-module
<br>
🩺 Dépannage
<details> <summary><strong>❌ « password authentication failed for user "baitway_admin" »</strong></summary> <br>
Un autre PostgreSQL écoute sur le port. Vérifie :

cmd
netstat -ano | findstr :5433
Si plusieurs processus apparaissent, change le port dans docker-compose.yml (ex. 5434:5432), mets à jour DATABASE_URL, puis :

cmd
docker compose down -v
docker compose up -d db
alembic upgrade head
</details> <details> <summary><strong>❌ Erreur 500 à l'inscription (bcrypt)</strong></summary> <br>
Incompatibilité passlib / bcrypt récent. Fixe la version :

cmd
pip install "bcrypt==4.0.1"
pip freeze > requirements.txt
</details> <details> <summary><strong>❌ « blocked by CORS policy »</strong></summary> <br>
Vérifie que app/main.py contient le middleware CORS avec allow_origins=["http://localhost:5173"], puis redémarre uvicorn.

</details> <details> <summary><strong>❌ La migration Alembic ne crée aucune table</strong></summary> <br>
Le modèle n'est pas importé dans migrations/env.py. Ajoute from app.models.user import User et target_metadata = Base.metadata, puis :

cmd
alembic revision --autogenerate -m "creation table users"
alembic upgrade head
</details> <details> <summary><strong>❌ « python » ou « docker » non reconnu</strong></summary> <br>
L'outil n'est pas dans le PATH. Réinstalle-le en cochant « Add to PATH » ou redémarre le terminal.

</details> <br>
🗺️ Feuille de route
 Phase 0 — Socle commun · auth JWT · base de données · app shell · contrat d'API
 Phase 1 — Moteurs · développement parallèle (données mockées)
 Phase 2 — Interfaces · développement parallèle des UI
 Phase 3 — Intégration · dashboard unifié · lien inter-modules · tests
 Phase 4 — Bonus · scoring ML · export avancé · rapports PDF
<br>
👨‍💻 Équipe
<table> <tr> <td align="center" width="50%"> <strong>Youssef Ben Chaouacha</strong><br> 🎣 Module A — Portail Phishing </td> <td align="center" width="50%"> <strong>Iheb Ben Massaoud</strong><br> 🔍 Module B — Recherche d'IOC </td> </tr> </table> <div align="center">
Projet de stage · ESPRIM — École Supérieure Privée d'Ingénieurs de Monastir

</div> <br>
📄 Licence
Distribué sous licence MIT. Voir LICENSE pour plus de détails.

<div align="center"> <br>
Made with ☕ by Youssef & Iheb

</div>





