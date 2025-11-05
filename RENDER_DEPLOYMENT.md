# 🚀 Guide de Déploiement sur Render

## Configuration des Fichiers

✅ Fichiers créés/modifiés pour Render :
- `requirements.txt` - Dépendances Python optimisées
- `build.sh` - Script de build avec UV (gestionnaire de packages ultra-rapide)
- `Procfile` - Commande de démarrage
- `runtime.txt` - Version Python
- `config/settings.py` - Sécurité et base de données
- `.env.example` - Template variables d'environnement

**Note:** Le script utilise `uv` au lieu de `pip` pour une installation 10-100x plus rapide !

## 📋 Étapes de Déploiement

### 1. Créer un nouveau Web Service sur Render

1. Connectez-vous à [Render](https://render.com)
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repo GitHub : `https://github.com/jeshurun01/investlink`
4. Configurez les paramètres :

### 2. Paramètres du Service

**Informations de base :**
- **Name:** `investlink` (ou votre choix)
- **Region:** `Frankfurt (EU Central)` (ou proche de vous)
- **Branch:** `main`
- **Root Directory:** (laissez vide)
- **Runtime:** `Python 3`

**Build & Deploy :**
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn config.wsgi:application`

**Plan :**
- Choisissez **Free** pour commencer (ou un plan payant selon vos besoins)

### 3. Variables d'Environnement

Dans l'onglet **"Environment"**, ajoutez ces variables :

#### Variables Essentielles :

```bash
# Django Core
SECRET_KEY=<générer-une-clé-secrète-forte>
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Database (Render PostgreSQL - voir étape 4)
DATABASE_URL=<sera-fournie-par-render-postgresql>

# Email (Console pour test, SMTP pour production)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@investlink.com

# Python Runtime
PYTHON_VERSION=3.12.9
```

#### Générer une SECRET_KEY sécurisée :

```python
# Dans un terminal Python local :
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Base de Données PostgreSQL

1. Dans Render, créez une **nouvelle base PostgreSQL** :
   - **New +** → **PostgreSQL**
   - **Name:** `investlink-db`
   - **Region:** Même région que votre web service
   - **Plan:** Free (suffisant pour démarrer)

2. Une fois créée, copiez l'**Internal Database URL**

3. Ajoutez la à vos variables d'environnement :
   ```
   DATABASE_URL=<coller-l-url-interne-postgresql>
   ```

### 5. Déploiement Initial

1. Cliquez sur **"Create Web Service"**
2. Render va :
   - Cloner votre repo
   - Installer les dépendances
   - Exécuter `build.sh` (collectstatic + migrations)
   - Démarrer avec Gunicorn

3. Surveillez les logs pour vérifier le déploiement

### 6. Configuration Post-Déploiement

#### Créer un superutilisateur :

Utilisez le **Shell** de Render :

```bash
python manage.py createsuperuser
```

#### Vérifier les migrations :

```bash
python manage.py showmigrations
```

## 🔧 Configuration Avancée

### Gestion des Fichiers Media (IMAGES UPLOADÉES)

⚠️ **PROBLÈME CONNU** : Les images uploadées (blog, projets) ne s'affichent pas en production sur Render.

**Cause** : Le système de fichiers de Render est éphémère. Les fichiers uploadés sont supprimés à chaque redéploiement.

#### ✅ Solution 1 : Persistent Disk (Recommandé pour Render)

1. Dans votre service Render → **Settings** → **Disks**
2. Cliquez **Add Disk**
3. Configurez :
   - **Name** : `media`
   - **Mount Path** : `/opt/render/project/src/media`
   - **Size** : 1GB (ou plus selon vos besoins)
4. Cliquez **Add Disk**
5. Redéployez votre service

Le persistent disk garantit que vos fichiers media persistent entre les déploiements.

#### ✅ Solution 2 : Cloudinary (Recommandé pour la production à grande échelle)

**Avantages** :
- ✅ CDN mondial pour chargements ultra-rapides
- ✅ Optimisation automatique des images
- ✅ Transformation d'images à la volée (resize, crop, webp)
- ✅ Pas de problèmes de persistence
- ✅ Plan gratuit : 25 crédits/mois

**Installation** :

```bash
pip install cloudinary django-cloudinary-storage
```

Ajoutez à `requirements.txt` :
```
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

**Configuration dans settings.py** :

```python
INSTALLED_APPS = [
    # ... autres apps
    'cloudinary_storage',
    'cloudinary',
    # ... reste des apps
]

# Cloudinary Configuration
import cloudinary

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

**Variables d'environnement Cloudinary** (sur Render) :

```bash
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
```

Pour obtenir vos identifiants :
1. Créez un compte sur [Cloudinary](https://cloudinary.com/)
2. Dashboard → **API Keys**
3. Copiez Cloud Name, API Key, API Secret

#### ✅ Solution 3 : AWS S3 (Pour les grandes entreprises)

Pour la production, configurez un stockage externe (AWS S3) :

1. Installez `django-storages` :
   ```bash
   pip install django-storages boto3
   ```

2. Ajoutez à `requirements.txt`

3. Configurez dans `settings.py` :
   ```python
   INSTALLED_APPS = [
       # ...
       'storages',
   ]
   
   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
   AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
   AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
   AWS_S3_REGION_NAME = 'eu-central-1'
   
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

### Vérification des fichiers media

Après configuration, testez :

1. Uploadez une image via l'admin Django
2. Vérifiez qu'elle s'affiche : `/media/projects/...` ou URL Cloudinary
3. Redéployez votre service
4. Vérifiez que l'image est toujours accessible

### Variables d'environnement additionnelles (Production)

```bash
# Email SMTP (Gmail exemple)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=mot-de-passe-application

# Domaine personnalisé
ALLOWED_HOSTS=.onrender.com,votre-domaine.com
```

### Domaine Personnalisé

1. Dans Render Dashboard → **Settings** → **Custom Domain**
2. Ajoutez votre domaine
3. Configurez les DNS selon les instructions Render
4. Mettez à jour `ALLOWED_HOSTS`

## 🐛 Dépannage

### Erreur de build

```bash
# Vérifier les logs de build
# Assurer que build.sh est exécutable
chmod +x build.sh
git add build.sh
git commit -m "fix: make build.sh executable"
git push
```

### Erreur d'installation UV

Si UV ne s'installe pas, revenez à pip classique dans `build.sh` :

```bash
# Remplacer dans build.sh :
pip install -r requirements.txt
```

### Avantages de UV

- ⚡ **10-100x plus rapide** que pip
- 📦 Résolution de dépendances optimisée
- 🔒 Lockfile automatique pour reproductibilité
- 💾 Cache intelligent

### Erreur de static files

```bash
# Dans le Shell Render :
python manage.py collectstatic --no-input
```

### Erreur de base de données

```bash
# Vérifier DATABASE_URL
echo $DATABASE_URL

# Re-exécuter les migrations
python manage.py migrate --run-syncdb
```

### Debug en production

**Temporairement**, activez DEBUG pour voir les erreurs :

```bash
DEBUG=True
```

⚠️ **N'oubliez pas de le remettre à False après !**

## 📊 Monitoring

### Logs en temps réel

Dans le Dashboard Render :
- **Logs** → Voir tous les logs de l'application
- Filtrer par niveau (Info, Error, etc.)

### Métriques

- CPU usage
- Memory usage
- Requests per minute

### Alertes

Configurez des alertes pour :
- Service down
- High memory usage
- Error rate élevé

## 🔐 Sécurité Production

Checklist avant la mise en production :

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` unique et sécurisée
- [ ] `ALLOWED_HOSTS` correctement configuré
- [ ] Base PostgreSQL (pas SQLite)
- [ ] HTTPS activé (automatique sur Render)
- [ ] Variables sensibles dans Environment Variables
- [ ] Fichier `.env` dans `.gitignore`
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Superutilisateur créé

## 🚀 Redéploiement

Pour mettre à jour votre application :

```bash
git add .
git commit -m "votre message"
git push origin main
```

Render détectera automatiquement le push et redéploiera.

## 📞 Support

- [Documentation Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Community Render](https://community.render.com/)

---

**Version:** 1.0  
**Dernière mise à jour:** 29 octobre 2025
