# Configuration Cloudinary pour InvestLink

## Problème résolu
Sur Render, les fichiers uploadés (images, documents) disparaissent à chaque redéploiement car le système de fichiers est **éphémère**. Cloudinary résout ce problème en stockant les médias dans le cloud.

## Avantages de Cloudinary

✅ **Stockage persistant** - Les fichiers ne disparaissent jamais  
✅ **CDN global** - Images livrées rapidement partout dans le monde  
✅ **Optimisation automatique** - Compression et formats modernes (WebP, AVIF)  
✅ **Transformations à la volée** - Redimensionnement, recadrage, filtres  
✅ **Free tier généreux** - 25GB stockage + 25GB bande passante/mois  

## Étapes d'installation (déjà effectué dans le code)

### 1. Packages installés
```bash
pip install cloudinary==1.41.0 django-cloudinary-storage==0.3.0
```

### 2. INSTALLED_APPS mis à jour
```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',  # AVANT django.contrib.staticfiles
    'cloudinary',
    # ...
]
```

### 3. Configuration automatique
Le code détecte automatiquement l'environnement:
- **Production** (DEBUG=False): Utilise Cloudinary
- **Développement** (DEBUG=True): Utilise stockage local

## Configuration Cloudinary (À FAIRE)

### 1. Créer un compte gratuit
🔗 **Inscription**: https://cloudinary.com/users/register_free

### 2. Récupérer les credentials
Après inscription, allez sur le Dashboard et copiez:
```
Cloud Name: votre_cloud_name
API Key: votre_api_key
API Secret: votre_api_secret
```

### 3. Configuration locale (développement)
Créez un fichier `.env` à la racine du projet:
```bash
# Copiez .env.example vers .env
cp .env.example .env
```

Éditez `.env` et ajoutez vos credentials:
```env
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
```

### 4. Configuration Render (production)

#### Via le Dashboard Render:
1. Allez sur votre service → **Environment**
2. Ajoutez ces variables:
   ```
   CLOUDINARY_CLOUD_NAME = votre_cloud_name
   CLOUDINARY_API_KEY = votre_api_key
   CLOUDINARY_API_SECRET = votre_api_secret
   ```
3. Cliquez sur **Save Changes**
4. Le service redémarrera automatiquement

#### Via render.yaml (alternatif):
```yaml
services:
  - type: web
    name: investlink
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: CLOUDINARY_CLOUD_NAME
        value: votre_cloud_name
      - key: CLOUDINARY_API_KEY
        value: votre_api_key
      - key: CLOUDINARY_API_SECRET
        sync: false  # Secret, à configurer manuellement
```

## Vérification de la configuration

### Test local
```bash
python manage.py shell
```

```python
from django.conf import settings
import cloudinary

# Vérifier que Cloudinary est configuré
print(cloudinary.config().cloud_name)
# Devrait afficher votre cloud_name

# Tester un upload
from cloudinary.uploader import upload
result = upload("/path/to/test-image.jpg")
print(result['secure_url'])
```

### Test en production
1. Connectez-vous à l'admin Django sur Render
2. Créez un article de blog avec une image
3. Vérifiez que l'image s'affiche
4. Redéployez l'application
5. ✅ L'image devrait toujours être visible

## Migration des fichiers existants

Si vous avez déjà des images uploadées localement:

### Option 1: Via l'interface admin
1. Re-uploadez manuellement chaque image
2. Les nouvelles uploads iront automatiquement sur Cloudinary

### Option 2: Via script (bulk upload)
```python
# manage.py migrate_to_cloudinary
import cloudinary.uploader
from core.models import BlogPost
from projects.models import Project

for post in BlogPost.objects.all():
    if post.image and post.image.path:
        result = cloudinary.uploader.upload(post.image.path)
        post.image = result['secure_url']
        post.save()
```

## URLs des médias

### Avant (local - ne fonctionne pas sur Render)
```
http://localhost:8000/media/blog/image.jpg
```

### Après (Cloudinary - CDN global)
```
https://res.cloudinary.com/votre_cloud_name/image/upload/v1234567890/media/blog/image.jpg
```

## Transformations d'images

Cloudinary permet des transformations à la volée:

```python
# Dans vos templates
{{ post.image.url }}?w=300&h=200&c=fill

# Avec django-cloudinary-storage
from cloudinary.templatetags.cloudinary import cloudinary_url
cloudinary_url(post.image.name, width=300, height=200, crop="fill")
```

## Formats d'URL supportés

- `/upload/` - Images normales
- `/upload/w_300,h_200,c_fill/` - Redimensionnées 300x200
- `/upload/f_auto,q_auto/` - Format et qualité automatiques
- `/upload/e_grayscale/` - Effets (noir et blanc, etc.)

## Limites du free tier

| Ressource | Limite mensuelle |
|-----------|------------------|
| Stockage | 25 GB |
| Bande passante | 25 GB |
| Transformations | 25,000 |
| Uploads | Illimité |

Pour un projet comme InvestLink, le free tier est largement suffisant au début.

## Alternative: Render Persistent Disk

Si vous préférez ne pas utiliser de service externe:

1. Créez un Persistent Disk sur Render (500 MB gratuit)
2. Montez-le sur `/opt/render/project/src/media`
3. Modifiez settings.py:
```python
if not DEBUG:
    MEDIA_ROOT = '/opt/render/project/src/media'
```

⚠️ **Inconvénients**:
- Pas de CDN (images plus lentes)
- Pas d'optimisation automatique
- Limité à 500 MB en free tier
- Backups manuels nécessaires

**Cloudinary est recommandé** pour de meilleures performances et fonctionnalités.

## Ressources

- 📚 Documentation Cloudinary: https://cloudinary.com/documentation/django_integration
- 📦 django-cloudinary-storage: https://github.com/klis87/django-cloudinary-storage
- 🎥 Tutorial vidéo: https://cloudinary.com/documentation/django_video_tutorial
- 💬 Support communautaire: https://community.cloudinary.com/

## Prochaines étapes

1. ✅ Code configuré pour Cloudinary
2. ⏳ Créer compte Cloudinary
3. ⏳ Ajouter credentials à .env (local)
4. ⏳ Ajouter credentials à Render (production)
5. ⏳ Tester upload d'image
6. ⏳ Redéployer et vérifier persistance
