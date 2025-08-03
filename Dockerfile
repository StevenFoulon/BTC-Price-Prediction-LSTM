# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/
COPY start_backend.py .

# Créer le dossier models s'il n'existe pas
RUN mkdir -p app/models

# Exposer le port 5001
EXPOSE 5001

# Variables d'environnement
ENV PYTHONPATH=/app
ENV FLASK_APP=app.backend.api
ENV FLASK_ENV=production

# Commande par défaut
CMD ["python", "start_backend.py"] 