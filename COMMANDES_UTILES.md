# 🛠️ Commandes Utiles - InvestLink

## Gestion de l'environnement

```bash
# Activer l'environnement virtuel (avec uv, automatique)
uv run <command>

# Installer une nouvelle dépendance
uv add <package-name>

# Installer les dépendances
uv sync
```

## Django

### Serveur de développement
```bash
# Démarrer le serveur
uv run manage.py runserver

# Démarrer sur un port spécifique
uv run manage.py runserver 8080
```

### Base de données
```bash
# Créer les migrations
uv run manage.py makemigrations

# Appliquer les migrations
uv run manage.py migrate

# Voir les migrations SQL
uv run manage.py sqlmigrate <app_name> <migration_number>

# Réinitialiser la base de données (ATTENTION : perte de données)
rm db.sqlite3
uv run manage.py migrate
```

### Superutilisateur
```bash
# Créer un superutilisateur
uv run manage.py createsuperuser

# Changer le mot de passe d'un utilisateur
uv run manage.py changepassword <username>
```

### Shell Django
```bash
# Ouvrir le shell Django
uv run manage.py shell

# Exemples dans le shell
from users.models import User
from projects.models import Project

# Créer un utilisateur
user = User.objects.create_user(username='test', email='test@example.com', password='password123')

# Lister tous les projets
Project.objects.all()

# Filtrer les projets approuvés
Project.objects.filter(status='approved')
```

### Gestion des fichiers statiques
```bash
# Collecter les fichiers statiques
uv run manage.py collectstatic

# Vider le dossier staticfiles
rm -rf staticfiles/*
```

## Tailwind CSS

```bash
# Installer les dépendances Node.js
npm install

# Compiler le CSS (une fois)
npm run build:css

# Compiler en mode watch (automatique)
npm run watch:css
```

## Tests

```bash
# Lancer tous les tests
uv run manage.py test

# Tester une application spécifique
uv run manage.py test users
uv run manage.py test projects

# Tester avec verbose
uv run manage.py test --verbosity=2

# Tester avec coverage
uv add coverage
uv run coverage run manage.py test
uv run coverage report
uv run coverage html
```

## Utilitaires Django

```bash
# Vider la base de données d'une app
uv run manage.py flush

# Créer une nouvelle app
uv run manage.py startapp <app_name>

# Vérifier le projet
uv run manage.py check

# Afficher les URLs du projet
uv run manage.py show_urls  # (nécessite django-extensions)
```

## Git

```bash
# Status
git status

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "Message du commit"

# Push
git push origin main

# Créer une nouvelle branche
git checkout -b feature/nom-de-la-fonctionnalite

# Voir l'historique
git log --oneline
```

## Maintenance

### Sauvegardes
```bash
# Sauvegarder la base de données SQLite
cp db.sqlite3 db.sqlite3.backup-$(date +%Y%m%d)

# Exporter les données en JSON
uv run manage.py dumpdata > data.json

# Importer les données depuis JSON
uv run manage.py loaddata data.json

# Exporter une app spécifique
uv run manage.py dumpdata users > users_data.json
```

### Nettoyage
```bash
# Supprimer les fichiers Python compilés
find . -type f -name '*.pyc' -delete
find . -type d -name '__pycache__' -delete

# Supprimer les migrations (ATTENTION)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

## Production

```bash
# Variables d'environnement
cp .env.example .env
# Modifier .env avec les vraies valeurs

# Collecter les fichiers statiques
uv run manage.py collectstatic --noinput

# Vérifier la configuration de déploiement
uv run manage.py check --deploy

# Créer un superutilisateur en production
uv run manage.py createsuperuser
```

## Debugging

```bash
# Activer le mode debug dans .env
DEBUG=True

# Voir les requêtes SQL
# Dans settings.py, ajouter :
# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {'class': 'logging.StreamHandler'}
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG'
#         }
#     }
# }

# Utiliser le debugger Python
# Dans votre code :
import pdb; pdb.set_trace()
```

## Commandes personnalisées utiles

```bash
# Créer des données de test
# Créer un fichier: core/management/commands/populate_db.py
uv run manage.py populate_db

# Nettoyer les sessions expirées
uv run manage.py clearsessions

# Envoyer un email de test
uv run manage.py sendtestemail your@email.com
```

## Performance

```bash
# Installer django-debug-toolbar pour le profiling
uv add django-debug-toolbar

# Analyser les requêtes lentes
# Dans le shell
from django.db import connection
print(connection.queries)
```

## Astuces

```bash
# Ouvrir le projet dans VS Code
code .

# Rechercher dans le code
grep -r "search_term" .

# Compter les lignes de code Python
find . -name "*.py" -not -path "./.venv/*" | xargs wc -l
```
