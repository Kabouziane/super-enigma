
#  Document Assistant (Django + AI + Vector Search)

---

## Table des matières

- [Présentation](#présentation)  
- [Fonctionnalités principales](#fonctionnalités-principales)  
- [Architecture technique](#architecture-technique)  
- [Installation & configuration](#installation--configuration)  
- [Lancement en local](#lancement-en-local)  
- [Utilisation de l’API](#utilisation-de-lapi)  
- [Authentification & sécurité](#authentification--sécurité)  
- [Ré-indexation & tâches périodiques](#ré-indexation--tâches-périodiques)  
- [Monitoring & logs](#monitoring--logs)  
- [Déploiement en production](#déploiement-en-production)  
- [Page How It Works](#page-how-it-works)  
- [Contribuer](#contribuer)  
- [Licence](#licence)

---

## Présentation

 Document Assistant est une plateforme backend avancée permettant d’indexer et d’interroger facilement des documents PDF via une interface API sécurisée. Grâce à l’intelligence artificielle et aux modèles de langage, le système génère des embeddings vectoriels pour chaque document, stocke ces données dans une base vectorielle locale (FAISS) ou cloud (Pinecone), et répond aux questions en langage naturel en citant les sources précises.

Ce projet a été développé avec Django 5.2 LTS pour garantir stabilité et performance, Celery pour le traitement asynchrone, et un système d’authentification JWT pour sécuriser l’accès.

---

## Fonctionnalités principales

- Upload sécurisé de PDF avec contrôle d’intégrité  
- Extraction automatique d’index vectoriel par embeddings OpenAI  
- Recherche vectorielle ultra-rapide via FAISS ou Pinecone  
- API RESTful sécurisée avec authentification par tokens JWT  
- Tâches asynchrones & périodiques (réindexation automatique quotidienne)  
- Limitation de taux d’usage pour protéger les endpoints  
- Monitoring avec Sentry pour suivre erreurs et performances  
- Tests automatisés pour garantir la stabilité du code  
- Extensible pour intégrer d’autres fournisseurs vectoriels ou modèles AI

---

## Architecture technique

```
+-------------+      +------------+      +------------+      +--------------+
| Frontend /  | ---> |  Django    | ---> | Celery /   | ---> | Vector Store |
| Clients API |      |  REST API  |      | Redis      |      | (FAISS /     |
+-------------+      +------------+      +------------+      | Pinecone)    |
       |                   |                   |             +--------------+
       |                   |                   |
       |                   |                   |
       |                   |                   +----------------+
       |                   |                                    |
       |                   +------------> PostgreSQL (Django DB) |
       |                                                        |
       +--------------------------------------------------------+
                             (auth, tokens, metadata, logs)
```

- Django REST Framework sert de backbone à l’API.  
- Celery gère les tâches lourdes d’indexation en arrière-plan via Redis.  
- django-celery-beat orchestre les tâches périodiques (ex: réindexation journalière).  
- FAISS (local) ou Pinecone (cloud) sont les stores vectoriels utilisés pour les recherches.  
- JWT via `djangorestframework-simplejwt` sécurise les endpoints.  
- Sentry surveille erreurs et exceptions.

---

## Installation & configuration

1. Clone le repo :  
```bash
git clone <URL_DU_REPO>
cd -document-assistant
```

2. Crée un environnement virtuel et active-le :  
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Installe les dépendances :  
```bash
pip install -r requirements.txt
```

4. Configure tes variables d’environnement dans un fichier `.env` à la racine :  
```env
DEBUG=True
SECRET_KEY=ta_clef_secrète
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI
OPENAI_API_KEY=ton_api_key_openai

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=5  # en minutes

# Pinecone (optionnel)
VECTORSTORE=faiss
# VECTORSTORE=pinecone
PINECONE_API_KEY=ton_api_key_pinecone
PINECONE_ENV=us-west1-gcp
PINECONE_INDEX_NAME=-index

# Sentry (optionnel)
SENTRY_DSN=https://ton_dsn_sentry@o0.ingest.sentry.io/0

# Limites uploads
MAX_UPLOAD_SIZE=10485760  # 10 MB
```

5. Applique les migrations :  
```bash
python manage.py migrate
python manage.py migrate django_celery_beat
```

6. Lance Redis localement ou via Docker :  
```bash
docker run -d -p 6379:6379 redis
```

---

## Lancement en local

Démarre les services en 3 consoles ou via Docker Compose :

- Django :  
```bash
python manage.py runserver
```

- Celery worker :  
```bash
celery -A config worker -l info
```

- Celery beat (scheduler) :  
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## Utilisation de l’API

### Authentification

Obtiens un token JWT :  
```bash
curl -X POST http://localhost:8000/api/token/ -d '{"username":"ton_utilisateur","password":"ton_mot_de_passe"}' -H "Content-Type: application/json"
```

Réponse :  
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

Utilise ce token pour accéder aux endpoints protégés :  
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..." http://localhost:8000/api/upload/
```

---

### Endpoints clés

- `POST /api/upload/` : upload un PDF (multipart/form-data)  
- `POST /api/query/` : interroge la base en langage naturel, payload JSON avec `question`  
- `GET /api/documents/` : liste des documents uploadés  

---

## Authentification & sécurité

- Auth via JWT simple avec DRF SimpleJWT  
- Limitation de taux configurable pour éviter abus  
- Validation stricte des fichiers uploadés (taille, type, header PDF)  
- Logs et erreurs remontés dans Sentry (si configuré)  

---

## Ré-indexation & tâches périodiques

- Les documents sont indexés en tâche asynchrone Celery.  
- Une tâche périodique programmée via django-celery-beat relance une ré-indexation complète chaque nuit à 2h.  
- Tu peux configurer la périodicité et la planification dans l’admin Django.  

---

## Monitoring & logs

- Sentry pour tracking des exceptions et alertes.  
- Logs formatés dans la console (niveau INFO par défaut).  

---

## Déploiement en production

- Préférer Postgres à SQLite pour la base principale.  
- Utiliser Redis en production pour Celery (celui-ci doit être persistant).  
- Configurer un reverse proxy (Nginx) et HTTPS.  
- Mettre en place une gestion des secrets (Vault, GitHub Secrets).  
- Surveiller régulièrement via Sentry et les métriques Celery.  
- Éventuellement scaler avec Pinecone pour la base vectorielle.

---

## Page How It Works

Voici un schéma simplifié du workflow :

```
Utilisateur              API Django               Celery Worker               Vector Store
   |                        |                          |                            |
   |--- Upload PDF --------->|                          |                            |
   |                        |--- Tâche indexation ---->|                            |
   |                        |                          |-- Extraction embeddings -->|
   |                        |                          |                            |-- Stockage vecteurs
   |                        |                          |                            |
   |--- Question ------------>|                          |                            |
   |                        |--- Recherche embeddings -->|                            |
   |                        |                          |<-- Résultats / sources ----|
   |<-----------------------|                          |                            |
```

Le document est uploadé, découpé en chunks, converti en vecteurs denses, puis stocké dans un index de recherche. Lorsqu’une question arrive, on interroge l’index et on retourne les résultats avec extraits de texte pour la source.

---

## Contribuer

Contributions bienvenues !  
Forkez, créez une branche, faites vos modifications puis un pull request.

---

## Licence

MIT License © 2025 

---

Merci d’utiliser  Document Assistant !
