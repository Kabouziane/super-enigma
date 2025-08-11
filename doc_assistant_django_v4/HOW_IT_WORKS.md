
# How It Works -  Document Assistant

---

## Introduction

Cette page explique clairement le fonctionnement interne de l'application ** Document Assistant**. Elle décrit le cheminement des documents et des requêtes, ainsi que les interactions entre les différents composants techniques.

---

## Workflow global

```plaintext
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

---

## Étapes détaillées

### 1. Upload du document

- L'utilisateur envoie un fichier PDF via l'endpoint sécurisé `/api/upload/`.
- Django valide le fichier (taille, type, intégrité).
- Une tâche asynchrone Celery est déclenchée pour traiter ce document.

### 2. Indexation & création d’embeddings

- Le worker Celery récupère le document, le découpe en chunks de texte.
- Chaque chunk est envoyé à l’API OpenAI pour générer un embedding vectoriel.
- Ces vecteurs sont stockés dans l’index local FAISS ou dans Pinecone (si configuré).

### 3. Recherche et réponse

- L’utilisateur pose une question via `/api/query/`.
- Django appelle Celery pour effectuer une recherche vectorielle dans l’index.
- Les chunks les plus pertinents sont retournés avec un score de similarité.
- Une réponse synthétique est générée (optionnel, selon implémentation) et renvoyée à l’utilisateur.

---

## Composants clés

| Composant     | Description                                                                                  |
|---------------|----------------------------------------------------------------------------------------------|
| **Django**    | API backend exposant les endpoints, gérant l’authentification, les validations et la logique |
| **Celery**    | Gestion des tâches asynchrones et périodiques (indexation, réindexation)                    |
| **Redis**     | Broker pour Celery, stockage temporaire des tâches                                          |
| **FAISS**     | Base de données vectorielle locale pour la recherche rapide                                |
| **Pinecone**  | Option cloud pour la recherche vectorielle scalable                                        |
| **OpenAI**    | Fournisseur des embeddings d’intelligence artificielle                                     |

---

## Schéma d’architecture

```plaintext
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

---

## Conclusion

Grâce à cette architecture modulaire et performante,  Document Assistant permet une gestion efficace et sécurisée de la recherche intelligente dans des documents PDF, avec une scalabilité possible vers le cloud.

---

Merci d’avoir lu cette explication détaillée !
