# 🚀 Guide d'installation rapide

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- ✅ **Docker** (version 20.10+)
- ✅ **Docker Compose** (version 1.29+)
- ✅ **Compte Twilio** avec sandbox WhatsApp
- ✅ **Clé API YouTube Data v3**
- ✅ **Compte Gmail** avec app password
- ✅ **ngrok** (pour l'exposition du webhook)

## Installation en 5 minutes ⏱️

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/youtube-mlops-n8n.git
cd youtube-mlops-n8n
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
nano .env  # ou utilisez votre éditeur préféré
```

**Minimum requis à configurer :**
- `YOUTUBE_API_KEY` : Votre clé YouTube API
- `GMAIL_EMAIL` : Votre adresse Gmail
- `GMAIL_APP_PASSWORD` : Votre app password Gmail
- `N8N_ENCRYPTION_KEY` : Une chaîne aléatoire (min 10 caractères)

### 3. Démarrer les services

```bash
docker-compose up -d
```

Vérifier que tous les services sont démarrés :
```bash
docker-compose ps
```

### 4. Configurer ngrok

Dans un nouveau terminal :
```bash
ngrok http 5678
```

Copiez l'URL HTTPS générée (ex: `https://abcd1234.ngrok-free.app`)

### 5. Configurer n8n

1. Ouvrez votre navigateur : `http://localhost:5678`
2. Créez un compte administrateur
3. Importez ou créez le workflow d'analyse

### 6. Configurer Twilio

1. Connectez-vous à [Twilio Console](https://console.twilio.com/)
2. Allez dans **Messaging** > **Try it out** > **Send a WhatsApp message**
3. Configurez le webhook avec votre URL ngrok :
   ```
   https://votre-url.ngrok-free.app/webhook/votre-workflow-id
   ```

### 7. Tester l'installation ✅

1. Envoyez `join <sandbox-code>` au numéro Twilio depuis WhatsApp
2. Envoyez `GoDeploy`
3. Attendez 2-5 minutes
4. Vérifiez votre email pour le rapport !

## Vérification de l'installation

### Vérifier les logs

```bash
# Logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f n8n
docker-compose logs -f mcp-server
```

### Tester les endpoints

```bash
# Vérifier n8n
curl http://localhost:5678

# Vérifier MCP server
curl http://localhost:8000

# Vérifier Streamlit
curl http://localhost:8501
```

## Troubleshooting rapide 🔧

### Les conteneurs ne démarrent pas
```bash
docker-compose down
docker-compose up -d --build
```

### Erreur de connexion PostgreSQL
```bash
docker-compose restart postgres
docker-compose restart n8n
```

### Le webhook ne répond pas
1. Vérifiez que ngrok est actif
2. Vérifiez l'URL configurée dans Twilio
3. Regardez les logs n8n : `docker-compose logs -f n8n`

### Erreur API YouTube/Hugging Face
- Vérifiez que vos clés API sont correctement configurées dans `.env`
- Vérifiez les quotas de vos APIs

## Accès aux services

Une fois installé, accédez aux services :

| Service | URL | Description |
|---------|-----|-------------|
| n8n | http://localhost:5678 | Interface de workflow |
| MCP API | http://localhost:8000 | API de sentiment |
| Dashboard | http://localhost:8501 | Visualisation des résultats |
| PostgreSQL | localhost:5432 | Base de données |

## Prochaines étapes

1. ✅ Installation terminée
2. 📚 Lisez le [README.md](README.md) complet
3. 🎨 Personnalisez le workflow selon vos besoins


