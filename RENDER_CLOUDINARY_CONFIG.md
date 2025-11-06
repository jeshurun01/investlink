# Configuration Render - URGENT

## Problème actuel
Les images ne s'affichent pas sur Render car Cloudinary n'est pas activé.

## Variables d'environnement REQUISES sur Render

Allez sur **Render Dashboard → Votre service → Environment** et ajoutez:

### 1. Mode Production
```
DEBUG = False
```
⚠️ **CRITIQUE** - Sans cela, Cloudinary ne sera jamais activé!

### 2. Credentials Cloudinary

Créez d'abord un compte sur: https://cloudinary.com/users/register_free

Puis récupérez vos credentials dans le Dashboard Cloudinary et ajoutez:

```
CLOUDINARY_CLOUD_NAME = votre_cloud_name
CLOUDINARY_API_KEY = votre_api_key
CLOUDINARY_API_SECRET = votre_api_secret
```

### 3. Variables existantes (à garder)
```
SECRET_KEY = [votre clé secrète]
DATABASE_URL = [votre URL PostgreSQL]
ALLOWED_HOSTS = localhost,127.0.0.1,.onrender.com
```

## Configuration complète Render

Voici TOUTES les variables à avoir sur Render:

| Variable | Valeur | Obligatoire |
|----------|--------|-------------|
| `DEBUG` | `False` | ✅ OUI |
| `SECRET_KEY` | Votre clé secrète Django | ✅ OUI |
| `DATABASE_URL` | URL PostgreSQL (auto par Render) | ✅ OUI |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.onrender.com` | ✅ OUI |
| `CLOUDINARY_CLOUD_NAME` | De votre dashboard Cloudinary | ✅ OUI |
| `CLOUDINARY_API_KEY` | De votre dashboard Cloudinary | ✅ OUI |
| `CLOUDINARY_API_SECRET` | De votre dashboard Cloudinary | ✅ OUI |

## Étapes détaillées

### Étape 1: Créer compte Cloudinary (5 min)

1. Allez sur: https://cloudinary.com/users/register_free
2. Inscrivez-vous (gratuit, 25GB)
3. Validez votre email

### Étape 2: Récupérer les credentials (1 min)

1. Connectez-vous à Cloudinary
2. Dashboard → En haut de la page, vous verrez:
   ```
   Account Details
   Cloud name: votre_cloud_name
   API Key: 123456789012345
   API Secret: [Click to reveal] abcdefghijklmnopqrstuvwxyz
   ```
3. Copiez ces 3 valeurs

### Étape 3: Configurer Render (3 min)

1. Allez sur: https://dashboard.render.com/
2. Sélectionnez votre service InvestLink
3. Cliquez sur **"Environment"** dans le menu gauche
4. Cliquez sur **"Add Environment Variable"**
5. Ajoutez les variables une par une:

   **Variable 1:**
   ```
   Key: DEBUG
   Value: False
   ```
   
   **Variable 2:**
   ```
   Key: CLOUDINARY_CLOUD_NAME
   Value: [coller votre cloud_name]
   ```
   
   **Variable 3:**
   ```
   Key: CLOUDINARY_API_KEY
   Value: [coller votre api_key]
   ```
   
   **Variable 4:**
   ```
   Key: CLOUDINARY_API_SECRET
   Value: [coller votre api_secret]
   ```

6. Cliquez sur **"Save Changes"**
7. Render va automatiquement redéployer votre application

### Étape 4: Vérification (5 min)

Attendez que le déploiement se termine (2-3 min), puis:

1. Allez sur votre site Render
2. Connectez-vous à l'admin Django
3. Allez dans Blog Posts ou Projects
4. **Uploadez une NOUVELLE image** (les anciennes ne seront pas migrées automatiquement)
5. Sauvegardez
6. Retournez voir la liste
7. ✅ L'image devrait s'afficher!

### Étape 5: Vérifier dans Cloudinary

1. Allez sur Cloudinary Dashboard
2. Cliquez sur **"Media Library"** (menu gauche)
3. Vous devriez voir votre image uploadée
4. L'URL sera du type: `https://res.cloudinary.com/votre_cloud_name/image/upload/...`

## Que faire avec les anciennes images?

Les images uploadées AVANT la configuration Cloudinary sont perdues (système de fichiers éphémère de Render).

**Solutions:**

1. **Re-uploader manuellement** (recommandé pour < 10 images)
   - Allez dans l'admin Django
   - Éditez chaque article/projet
   - Re-uploadez l'image
   - Sauvegardez

2. **Script de migration** (si vous avez beaucoup d'images)
   - Sauvegardez vos images en local d'abord
   - Utilisez un script Python pour les uploader vers Cloudinary
   - Contactez-moi si vous avez besoin d'aide

## Troubleshooting

### ❌ "Les images ne s'affichent toujours pas"

**Vérifiez:**
1. Sur Render → Environment → `DEBUG = False` (pas "false", pas "0")
2. Les 3 variables Cloudinary sont présentes
3. Pas d'espaces avant/après les valeurs
4. Le déploiement est terminé (regardez les logs)
5. Vous avez uploadé une NOUVELLE image après la config

**Testez:**
```bash
# Dans les logs Render, cherchez:
"CLOUDINARY_CLOUD_NAME"
"DEFAULT_FILE_STORAGE"
```

### ❌ "Cloudinary dit 'No files'"

**Normal!** Cloudinary est vide au début. Les anciennes images sont perdues.

**Solution:** Uploadez de nouvelles images via l'admin Django.

### ❌ "Erreur 401 Unauthorized de Cloudinary"

**Cause:** Credentials incorrects

**Solution:**
1. Vérifiez que vous avez copié les bonnes valeurs
2. Pas d'espaces avant/après
3. API Secret complètement copié (cliquez "Reveal" dans Cloudinary)

### ❌ "Le build échoue sur Render"

**Regardez les logs:**
- Si erreur `ModuleNotFoundError`: requirements.txt a bien cloudinary
- Si erreur database: DATABASE_URL est configuré
- Si erreur settings: DEBUG et autres variables présentes

## Commandes de diagnostic

Pour tester en local (avec DEBUG=False temporairement):

```bash
# Ajouter à .env en local:
DEBUG=False
CLOUDINARY_CLOUD_NAME=votre_value
CLOUDINARY_API_KEY=votre_value
CLOUDINARY_API_SECRET=votre_value

# Puis tester:
python check_cloudinary.py
```

Vous devriez voir tous les ✅ verts.

## Après la configuration

Une fois que tout fonctionne:

✅ Les nouvelles images uploadées vont automatiquement sur Cloudinary  
✅ Les images persistent même après redéploiement  
✅ CDN global = chargement rapide partout  
✅ Optimisation automatique (WebP, compression)  
✅ 25GB gratuit (largement suffisant)  

## Besoin d'aide?

Si après avoir suivi ces étapes les images ne s'affichent toujours pas:

1. Copiez les logs Render (dernier déploiement)
2. Capturez screenshot de Render → Environment (masquez les secrets!)
3. Partagez le message d'erreur exact

---

**Temps total estimé: 15 minutes**

🎯 **Objectif:** DEBUG=False + 3 variables Cloudinary sur Render = Images qui fonctionnent!
