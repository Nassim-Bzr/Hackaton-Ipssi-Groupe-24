FROM python:3.11-slim

# Répertoire de travail de l'application
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY . .

# Port exposé par le service FastAPI
EXPOSE 8000

# Commande de démarrage du serveur FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

