# Guide de Sauvegarde et Restauration des Données

## 🔴 URGENT : Éviter la perte de données sur Render

### Problème
À chaque build/déploiement sur Render, vous perdez :
- ❌ Tous les utilisateurs
- ❌ Tous les projets
- ❌ Toutes les données

**Cause** : SQLite (`db.sqlite3`) est stocké dans le système de fichiers éphémère.

### ✅ Solution : PostgreSQL Persistant

## Étape 1 : Sauvegarder les données actuelles

### Option A : Via le Shell Render (Recommandé)

1. Ouvrez le **Shell** de votre service Render
2. Exportez les données en JSON :

```bash
# Exporter toutes les données
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > backup_full.json

# Ou par app spécifique (recommandé pour éviter les erreurs)
python manage.py dumpdata users --natural-foreign --natural-primary --indent=2 > backup_users.json
python manage.py dumpdata projects --natural-foreign --natural-primary --indent=2 > backup_projects.json
python manage.py dumpdata core --natural-foreign --natural-primary --indent=2 > backup_core.json
python manage.py dumpdata messaging --natural-foreign --natural-primary --indent=2 > backup_messaging.json
python manage.py dumpdata notifications --natural-foreign --natural-primary --indent=2 > backup_notifications.json
```

3. Téléchargez les fichiers JSON :

```bash
# Affichez le contenu et copiez-le
cat backup_users.json
```

4. Collez le contenu dans des fichiers locaux sur votre ordinateur

### Option B : Depuis votre environnement local

Si vous avez une copie locale récente de `db.sqlite3` :

```bash
# Dans votre terminal local
cd /home/jeshurun-nasser/dev/py/django-app/investlink

# Exporter toutes les données
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --exclude=contenttypes --exclude=auth.permission > backup_full.json

# Ou par app
python manage.py dumpdata users --indent=2 > backups/backup_users.json
python manage.py dumpdata projects --indent=2 > backups/backup_projects.json
python manage.py dumpdata core --indent=2 > backups/backup_core.json
python manage.py dumpdata messaging --indent=2 > backups/backup_messaging.json
python manage.py dumpdata notifications --indent=2 > backups/backup_notifications.json
```

## Étape 2 : Créer une Base PostgreSQL sur Render

1. **Dashboard Render** → **New +** → **PostgreSQL**
2. Configurez :
   - **Name** : `investlink-db`
   - **Database** : `investlink` (ou laissez par défaut)
   - **User** : (généré automatiquement)
   - **Region** : **Frankfurt (EU Central)** (même région que votre service)
   - **Plan** : **Free** (suffisant pour débuter)

3. Cliquez **Create Database**

4. Attendez que le statut devienne **Available** (1-2 minutes)

5. Copiez l'**Internal Database URL** :
   ```
   postgresql://user:password@hostname:5432/database
   ```

## Étape 3 : Configurer votre Service Web

1. Allez dans votre **Web Service** → **Environment**

2. Ajoutez/Modifiez la variable :
   ```
   DATABASE_URL=postgresql://user:password@hostname:5432/database
   ```
   (Collez l'URL copiée à l'étape 2)

3. **IMPORTANT** : Avant de sauvegarder, vérifiez les autres variables :
   ```
   SECRET_KEY=<votre-clé-existante>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   ```

4. Cliquez **Save Changes**

## Étape 4 : Déployer avec PostgreSQL

Render va automatiquement redéployer. Attendez la fin du build.

Vérifiez les logs pour confirmer :
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying users.0001_initial... OK
  Applying projects.0001_initial... OK
  ...
```

## Étape 5 : Restaurer les Données

### Via le Shell Render :

1. Ouvrez le **Shell** de votre service

2. Créez un fichier temporaire avec vos données :

```bash
# Créer le fichier
cat > backup_users.json << 'EOF'
[
  {
    "model": "users.user",
    "pk": 1,
    ...
  }
]
EOF
```

3. Importez les données :

```bash
# Restaurer les données
python manage.py loaddata backup_users.json
python manage.py loaddata backup_projects.json
python manage.py loaddata backup_core.json
python manage.py loaddata backup_messaging.json
python manage.py loaddata backup_notifications.json
```

### Alternative : Via Script de Migration

Créez un script Python personnalisé si vous avez beaucoup de données.

## Étape 6 : Créer un Superuser

```bash
# Via le Shell Render
python manage.py create_admin --username=admin --email=admin@investlink.com

# Ou avec mot de passe personnalisé
python manage.py create_admin --username=admin --email=admin@investlink.com --password=VotreMotDePasse123!
```

## Étape 7 : Vérification

1. Connectez-vous à votre site : `https://votre-app.onrender.com/admin`
2. Vérifiez que les utilisateurs sont présents
3. Vérifiez que les projets sont présents
4. Testez la création de nouvelles données

## 🔒 Persistent Disk pour les Fichiers Media

N'oubliez pas de configurer un **Persistent Disk** pour les images :

1. **Settings** → **Disks** → **Add Disk**
2. Configurez :
   - **Name** : `media`
   - **Mount Path** : `/opt/render/project/src/media`
   - **Size** : 1GB (ou plus)
3. **Add Disk**

## 🔄 Sauvegardes Automatiques

### Script de Sauvegarde Hebdomadaire

Créez un **Cron Job** sur Render pour sauvegardes automatiques :

1. **New +** → **Cron Job**
2. Configurez :
   - **Name** : `investlink-backup`
   - **Command** : `python manage.py dumpdata --natural-foreign --indent=2 > /opt/render/backups/backup_$(date +%Y%m%d).json`
   - **Schedule** : `0 2 * * 0` (Chaque dimanche à 2h du matin)

### Sauvegarde PostgreSQL Automatique

Render Pro offre des **sauvegardes automatiques quotidiennes** pour PostgreSQL.

Pour le plan Free, exportez manuellement :

```bash
# Via le Shell de la base PostgreSQL
pg_dump $DATABASE_URL > backup.sql
```

## 📋 Checklist Avant Chaque Déploiement

- [ ] Variables d'environnement à jour
- [ ] `DATABASE_URL` pointe vers PostgreSQL (pas SQLite)
- [ ] Migrations testées localement
- [ ] Sauvegarde récente des données
- [ ] Persistent Disk configuré pour media
- [ ] `DEBUG=False` en production
- [ ] `ALLOWED_HOSTS` correct

## 🆘 En Cas de Perte de Données

Si vous avez déjà perdu des données :

1. **NE PAS PANIQUER** - Render garde des snapshots temporaires
2. Contactez le support Render pour récupération
3. Utilisez vos backups locaux
4. Restaurez avec `loaddata`

## 🎯 Bonnes Pratiques

1. **Toujours PostgreSQL en production** (jamais SQLite)
2. **Sauvegardes régulières** (hebdomadaires minimum)
3. **Persistent Disk** pour les fichiers uploadés
4. **Testez localement** avec PostgreSQL aussi
5. **Versionner** les migrations dans Git
6. **Surveiller** les logs après chaque déploiement

## 📞 Aide

- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Django Backup Docs](https://docs.djangoproject.com/en/5.2/ref/django-admin/#dumpdata)
- Support Render : support@render.com

---

**Important** : Une fois PostgreSQL configuré, vos données persisteront entre les déploiements ! 🎉
