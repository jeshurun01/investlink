# ✅ Configuration PostgreSQL - Checklist

## 🔍 Vérification de la Configuration Actuelle

### 1. Requirements.txt ✅

**Status** : ✅ DÉJÀ CONFIGURÉ

```txt
psycopg2-binary==2.9.10  # ✅ Présent
django-environ==0.11.2   # ✅ Présent
```

Aucune modification nécessaire.

---

### 2. Settings.py ✅

**Status** : ✅ DÉJÀ CONFIGURÉ

Le fichier `config/settings.py` utilise déjà `django-environ` qui détecte automatiquement PostgreSQL :

```python
# Ligne 112-116
DATABASES = {
    "default": env.db_url(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}
```

**Comment ça marche** :
- Si `DATABASE_URL` n'existe pas → SQLite (dev local)
- Si `DATABASE_URL=postgresql://...` → PostgreSQL automatiquement détecté
- Aucun code à modifier !

**Optimisations PostgreSQL ajoutées** (lignes 119-125) :
```python
if not DEBUG and 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Connection pooling
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'  # 30 seconds timeout
    }
```

---

### 3. Variables d'Environnement Render

**Status** : ⏳ À CONFIGURER SUR RENDER

Dans **Render Dashboard** → **Web Service** → **Environment**, ajoutez :

```bash
# ====== OBLIGATOIRES ======

# Base de données PostgreSQL (à copier depuis votre base PostgreSQL Render)
DATABASE_URL=postgresql://user:password@hostname:5432/database

# Sécurité
SECRET_KEY=<générer-une-clé-secrète-forte>
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# ====== OPTIONNELLES ======

# Email (console par défaut, SMTP pour production)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com  # Si vous utilisez Gmail
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@investlink.com

# Performance PostgreSQL (optionnel)
CONN_MAX_AGE=600  # Durée de vie des connexions (10 minutes)

# Python
PYTHON_VERSION=3.12.9
```

### Comment générer une SECRET_KEY sécurisée :

```bash
# Dans un terminal Python local
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🎯 Ce Qui Change Automatiquement

### Détection Automatique de la Base

```python
# SQLite (dev local - pas de DATABASE_URL)
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# PostgreSQL (production - DATABASE_URL défini)
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
```

### Format DATABASE_URL PostgreSQL

```
postgresql://username:password@hostname:port/database

Exemple :
postgresql://investlink_user:abc123@dpg-abc123.frankfurt-postgres.render.com:5432/investlink_db
```

**Décomposition** :
- `postgresql://` - Type de base de données
- `investlink_user` - Nom d'utilisateur
- `abc123` - Mot de passe
- `dpg-abc123.frankfurt-postgres.render.com` - Hostname
- `5432` - Port (défaut PostgreSQL)
- `investlink_db` - Nom de la base

---

## 🔄 Workflow de Migration

### Étape 1 : Créer PostgreSQL sur Render ✓
- New + → PostgreSQL
- Plan Free
- Copier l'Internal Database URL

### Étape 2 : Configurer DATABASE_URL ✓
- Web Service → Environment
- Coller l'URL PostgreSQL
- Save Changes

### Étape 3 : Render redéploie automatiquement ✓
- Détecte le changement de variable
- Réinstalle les dépendances (psycopg2-binary)
- Exécute les migrations
- Démarre avec PostgreSQL

### Étape 4 : Les migrations s'exécutent ✓
```bash
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, messaging, notifications, projects, sessions, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying users.0001_initial... OK
  Applying projects.0001_initial... OK
  ...
```

### Étape 5 : Restaurer les données ✓
```bash
python manage.py loaddata backup_full_*.json
```

---

## ✅ Vérification Post-Migration

### 1. Vérifier la base utilisée

```bash
# Shell Render
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default']['ENGINE'])
# Doit afficher : django.db.backends.postgresql

>>> print(settings.DATABASES['default']['NAME'])
# Doit afficher : investlink_db (ou le nom de votre base)
```

### 2. Vérifier les connexions

```bash
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT version();")
>>> print(cursor.fetchone())
# Doit afficher : ('PostgreSQL 16.x ...',)
```

### 3. Vérifier les données

```bash
>>> from users.models import User
>>> User.objects.count()
# Doit afficher : le nombre d'utilisateurs restaurés

>>> from projects.models import Project
>>> Project.objects.count()
# Doit afficher : le nombre de projets restaurés
```

---

## 🐛 Résolution de Problèmes

### Erreur : "No module named 'psycopg2'"

**Cause** : `psycopg2-binary` pas installé
**Solution** : Déjà dans `requirements.txt`, rebuild le service

### Erreur : "could not connect to server"

**Cause** : `DATABASE_URL` incorrect
**Solution** : Vérifier que vous avez copié l'**Internal URL** (pas l'External)

### Erreur : "FATAL: password authentication failed"

**Cause** : Mauvais mot de passe dans `DATABASE_URL`
**Solution** : Re-copier l'URL complète depuis Render PostgreSQL

### Erreur : "relation 'users_user' does not exist"

**Cause** : Migrations pas exécutées
**Solution** : 
```bash
python manage.py migrate
# ou
python manage.py migrate --run-syncdb
```

### Les données ne persistent toujours pas

**Cause** : Toujours sur SQLite
**Solution** : Vérifier avec le shell que l'ENGINE est bien `postgresql`

---

## 📊 Comparaison Détaillée

| Aspect | SQLite (Avant) | PostgreSQL (Après) |
|--------|----------------|-------------------|
| **Type de stockage** | Fichier local | Service externe |
| **Persistence Render** | ❌ Éphémère | ✅ Permanent |
| **Concurrent writes** | ❌ 1 seul | ✅ Milliers |
| **Performances** | ⚠️ Limitées | ✅ Excellentes |
| **Transactions** | ✅ Basiques | ✅ Complètes (ACID) |
| **JSON/JSONB** | ❌ Non | ✅ Oui |
| **Full-text search** | ⚠️ Limitée | ✅ Avancée |
| **Réplication** | ❌ Non | ✅ Oui |
| **Backups auto** | ❌ Non | ✅ Oui (Pro) |
| **Coût Render** | Gratuit | Gratuit |
| **Recommandation** | Dev uniquement | Production ✅ |

---

## 💡 Bonnes Pratiques

### 1. Utiliser PostgreSQL localement aussi

Pour éviter les surprises, utilisez PostgreSQL en développement :

```bash
# Installer PostgreSQL
sudo apt install postgresql  # Ubuntu/Debian
brew install postgresql      # macOS

# Créer une base locale
createdb investlink_dev

# Dans .env
DATABASE_URL=postgresql://localhost/investlink_dev
```

### 2. Sauvegardes régulières

```bash
# Hebdomadaire minimum
python backup_data.py --all

# Avant chaque déploiement majeur
python backup_data.py
```

### 3. Surveiller les performances

```bash
# Activer le logging des requêtes lentes (settings.py)
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### 4. Utiliser les indexes

```python
# Dans vos modèles
class Project(models.Model):
    title = models.CharField(max_length=200, db_index=True)  # Index
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),  # Index composé
        ]
```

---

## 📞 Support

- **Configuration settings** : `config/settings.py` (lignes 107-125)
- **Requirements** : `requirements.txt` (ligne 18)
- **Guide migration** : `POSTGRESQL_MIGRATION.md`
- **Documentation Render** : https://render.com/docs/databases

---

## ✅ Résumé

1. ✅ **Code déjà prêt** - `settings.py` et `requirements.txt` configurés
2. ⏳ **Action requise** - Créer PostgreSQL sur Render et configurer `DATABASE_URL`
3. ✅ **Migration automatique** - Render redéploie et exécute les migrations
4. ⏳ **Restauration** - Charger vos données sauvegardées
5. ✅ **Résultat** - Plus jamais de perte de données !

**Aucune modification de code nécessaire** - Tout est déjà configuré ! 🎉
