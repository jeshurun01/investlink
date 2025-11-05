# 🚀 Guide Rapide : Migration vers PostgreSQL sur Render

## ⚡ Actions Urgentes (À faire MAINTENANT)

### 1️⃣ Sauvegarder vos données actuelles

**AVANT de faire quoi que ce soit d'autre !**

```bash
# Sur votre ordinateur local
cd /home/jeshurun-nasser/dev/py/django-app/investlink

# Sauvegarde complète
python backup_data.py

# OU sauvegarder toutes les apps séparément (recommandé)
python backup_data.py --all
```

Les fichiers seront créés dans le dossier `backups/`.

### 2️⃣ Créer PostgreSQL sur Render

1. Allez sur [Render Dashboard](https://dashboard.render.com/)
2. Cliquez **New +** → **PostgreSQL**
3. Configurez :
   ```
   Name: investlink-db
   Database: investlink
   User: (auto-généré)
   Region: Frankfurt (EU Central)
   PostgreSQL Version: 16
   Plan: Free
   ```
4. Cliquez **Create Database**
5. Attendez que le statut devienne **Available** (1-2 minutes)

### 3️⃣ Configurer la connexion

1. Dans la page de votre base PostgreSQL, copiez l'**Internal Database URL** :
   ```
   postgresql://username:password@hostname/database
   ```

2. Allez dans votre **Web Service** → **Environment**

3. Ajoutez/Modifiez la variable :
   ```
   DATABASE_URL=postgresql://username:password@hostname/database
   ```
   (Collez l'URL complète que vous avez copiée)

4. **Sauvegardez** (Save Changes)

### 4️⃣ Déploiement automatique

Render va redéployer automatiquement. Attendez la fin du build (2-5 minutes).

Surveillez les logs pour voir :
```
Running migrations:
  Applying users.0001_initial... OK
  Applying projects.0001_initial... OK
  ...
```

### 5️⃣ Restaurer vos données

Une fois le déploiement terminé :

1. Ouvrez le **Shell** de votre service web
2. Restaurez les données :

```bash
# Si vous avez sauvegardé avec --all
python manage.py loaddata backup_users_*.json
python manage.py loaddata backup_projects_*.json
python manage.py loaddata backup_core_*.json
python manage.py loaddata backup_messaging_*.json
python manage.py loaddata backup_notifications_*.json

# OU si vous avez une sauvegarde complète
python manage.py loaddata backup_full_*.json
```

**Astuce** : Vous devrez copier-coller le contenu des fichiers JSON dans le shell si vous ne pouvez pas les uploader directement.

### 6️⃣ Créer un superuser

```bash
python manage.py create_admin --username=admin --email=admin@investlink.com
```

### 7️⃣ Vérification

1. Visitez : `https://votre-app.onrender.com/admin`
2. Connectez-vous
3. Vérifiez que les données sont présentes
4. Testez la création de nouveaux objets

## ✅ Résultat

Maintenant, à chaque déploiement :
- ✅ Vos utilisateurs persistent
- ✅ Vos projets persistent
- ✅ Toutes vos données persistent
- ✅ Seul le code est mis à jour

## 📊 Comparaison

| Avant (SQLite) | Après (PostgreSQL) |
|----------------|-------------------|
| ❌ Données perdues à chaque build | ✅ Données persistantes |
| ❌ Pas pour la production | ✅ Production-ready |
| ❌ Performances limitées | ✅ Hautes performances |
| ❌ Pas de sauvegardes automatiques | ✅ Snapshots automatiques (Pro) |
| ❌ Fichier dans le système éphémère | ✅ Service externe persistant |

## 🔄 Workflow de Déploiement (Après Migration)

```bash
# 1. Développement local
git add .
git commit -m "feat: nouvelle fonctionnalité"

# 2. Push vers GitHub
git push origin main

# 3. Render détecte le push et redéploie automatiquement
# ✅ Vos données sont préservées !

# 4. Vérification (si nécessaire)
# Ouvrir le Shell Render et vérifier
python manage.py shell
>>> from users.models import User
>>> User.objects.count()
```

## 🆘 En cas de problème

### Erreur de connexion PostgreSQL

Vérifiez que `DATABASE_URL` :
- Est correctement définie dans Environment
- Contient l'**Internal URL** (pas l'External)
- Est au format : `postgresql://user:pass@host:5432/db`

### Erreur de migration

```bash
# Shell Render
python manage.py migrate --fake-initial
```

### Données toujours perdues

Vérifiez que vous utilisez bien PostgreSQL :

```bash
# Shell Render
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default']['ENGINE'])
# Doit afficher : django.db.backends.postgresql
```

## 💡 Conseils

1. **Sauvegardez toujours avant un déploiement majeur**
2. **Testez localement avec PostgreSQL** aussi (docker-compose)
3. **Surveillez les logs** après chaque déploiement
4. **Configurez des alertes** Render pour être notifié des problèmes

## 📞 Support

- Guide complet : `backup_restore_guide.md`
- Documentation Render : [render.com/docs/databases](https://render.com/docs/databases)
- Support Render : support@render.com

---

**Temps estimé** : 15-30 minutes
**Difficulté** : Facile
**Impact** : 🔥 CRITIQUE - Résout le problème de perte de données
