# Hackaton-Ipssi-Groupe-24

## Data Lake

Le projet expose un Data Lake S3-compatible via MinIO, organisé en 3 zones:

- raw (bronze): documents bruts uploadés
- clean (silver): sortie OCR en JSON
- curated (gold): données structurées prêtes pour consommation métier

### Démarrage

```bash
docker compose up --build -d
```

### Services

- Frontend: http://localhost:5173
- Backend: http://localhost:3000
- Validation: http://localhost:8000
- MongoDB: http://localhost:27017
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
- Airflow: http://localhost:8080

Identifiants MinIO par défaut:

- user: minioadmin
- password: minioadmin

Identifiants Airflow par defaut (créer depuis le docker-compose):

- user: admin
- password: admin

Trigger par évenement au moments d'envoyer un ou plusieurs formulaires

### Contrat Data Lake backend

Les routes backend conservent le comportement existant et ajoutent les URI Data Lake:

- POST /upload
- POST /upload-to-bdd

Dans les réponses, le champ `data_lake` contient:

- raw_uri
- clean_uri
- curated_uri

Dans MongoDB (route /upload-to-bdd), ces URI sont aussi stockées dans `metadata`.
