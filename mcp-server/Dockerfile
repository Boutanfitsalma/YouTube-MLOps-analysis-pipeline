FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crée un dossier pour les modèles pré-téléchargés
RUN mkdir -p models

# Expose le port pour l'API
EXPOSE 8000

# Commande pour démarrer le serveur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]