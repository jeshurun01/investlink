# Déploiement sur PythonAnywhere

Ce guide vous accompagne étape par étape pour déployer votre application Django InvestLink sur PythonAnywhere.

## Table des matières
1. [Prérequis](#prérequis)
2. [Configuration initiale](#configuration-initiale)
3. [Clonage du projet](#clonage-du-projet)
4. [Configuration de la base de données](#configuration-de-la-base-de-données)
5. [Configuration des fichiers statiques](#configuration-des-fichiers-statiques)
6. [Configuration WSGI](#configuration-wsgi)
7. [Variables d'environnement](#variables-denvironnement)
8. [Migrations et superutilisateur](#migrations-et-superutilisateur)
9. [Dépannage](#dépannage)

## Prérequis

- Un compte PythonAnywhere (gratuit ou payant)
- Votre code sur GitHub
- Les credentials Cloudinary (pour les fichiers media en production)

## Configuration initiale

### 1. Créer un compte PythonAnywhere

1. Allez sur [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Inscrivez-vous pour un compte gratuit ou payant
3. Confirmez votre adresse email

### 2. Comprendre les limitations du compte gratuit

**Compte gratuit :**
- 1 application web
- 512 MB d'espace disque
- SQLite uniquement (pas de PostgreSQL/MySQL)
- Sous-domaine `username.pythonanywhere.com`
- Pas d'accès HTTPS personnalisé

**Compte payant (Hacker/Web Dev) :**
- PostgreSQL/MySQL disponible
- Domaine personnalisé
- Plus d'espace et de ressources

## Clonage du projet

### 1. Ouvrir une console Bash

1. Connectez-vous à PythonAnywhere
2. Cliquez sur l'onglet **"Consoles"**
3. Cliquez sur **"Bash"** pour ouvrir une nouvelle console

### 2. Cloner votre repository

```bash
# Se positionner dans le dossier home
cd ~

# Cloner le repository (remplacez par votre URL)
git clone https://github.com/jeshurun01/investlink.git

# Entrer dans le dossier
cd investlink
```

### 3. Créer un environnement virtuel

```bash
# Créer un environnement virtuel Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 investlink-env

# L'environnement sera automatiquement activé
# Vous verrez (investlink-env) dans votre prompt
```

### 4. Installer les dépendances

```bash
# S'assurer que l'environnement est activé
workon investlink-env

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration de la base de données

### Option A : SQLite (Compte gratuit)

SQLite est automatiquement configuré dans votre `settings.py`. Aucune configuration supplémentaire n'est nécessaire.

### Option B : PostgreSQL (Compte payant)

1. Allez dans l'onglet **"Databases"** sur PythonAnywhere
2. Créez une nouvelle base de données PostgreSQL
3. Notez les informations de connexion
4. Ajoutez la variable d'environnement `DATABASE_URL` (voir section Variables d'environnement)

Format de `DATABASE_URL` :
```
postgresql://username:password@hostname:port/database_name
```

## Configuration des fichiers statiques

### 1. Collecter les fichiers statiques

```bash
# Dans la console Bash, avec l'environnement activé
cd ~/investlink
python manage.py collectstatic --noinput
```

### 2. Configurer dans l'interface Web

1. Allez dans l'onglet **"Web"**
2. Cliquez sur **"Add a new web app"**
3. Choisissez **"Manual configuration"** (pas "Django")
4. Sélectionnez **Python 3.10**
5. Cliquez sur **"Next"**

Après la création de l'app :

1. Dans la section **"Static files"**, ajoutez :
   - **URL:** `/static/`
   - **Directory:** `/home/VOTRE_USERNAME/investlink/staticfiles/`

2. Ajoutez également pour les fichiers media (développement uniquement) :
   - **URL:** `/media/`
   - **Directory:** `/home/VOTRE_USERNAME/investlink/media/`

⚠️ **Important :** Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur PythonAnywhere réel.

## Configuration WSGI

### 1. Localiser le fichier WSGI

Dans l'onglet **"Web"**, vous verrez un lien vers votre fichier WSGI :
```
/var/www/VOTRE_USERNAME_pythonanywhere_com_wsgi.py
```

### 2. Modifier le fichier WSGI

Cliquez sur le lien pour éditer le fichier et remplacez tout son contenu par :

```python
import os
import sys

# Ajouter le chemin de votre projet
path = '/home/VOTRE_USERNAME/investlink'
if path not in sys.path:
    sys.path.insert(0, path)

# Définir le module de settings Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Charger les variables d'environnement depuis .env
from pathlib import Path
import environ

env = environ.Env()
env_file = Path(path) / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Initialiser Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

⚠️ **Important :** Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur PythonAnywhere réel.

### 3. Configurer le virtualenv

Dans la section **"Virtualenv"** de l'onglet Web :
1. Entrez le chemin : `/home/VOTRE_USERNAME/.virtualenvs/investlink-env`
2. Cliquez sur le checkmark bleu pour sauvegarder

## Variables d'environnement

### 1. Créer le fichier .env

Dans une console Bash :

```bash
cd ~/investlink
nano .env
```

### 2. Ajouter les variables

Copiez et modifiez selon vos besoins :

```bash
# Django Core
DEBUG=False
SECRET_KEY=votre-clé-secrète-super-longue-et-aléatoire-ici
ALLOWED_HOSTS=VOTRE_USERNAME.pythonanywhere.com

# Pour compte payant avec domaine personnalisé :
# ALLOWED_HOSTS=VOTRE_USERNAME.pythonanywhere.com,votredomaine.com,www.votredomaine.com

# Base de données (pour PostgreSQL - compte payant)
# DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Cloudinary (pour les fichiers media en production)
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@investlink.com
```

### 3. Sauvegarder le fichier

- Appuyez sur `Ctrl + X`
- Appuyez sur `Y` pour confirmer
- Appuyez sur `Enter` pour sauvegarder

### 4. Générer une SECRET_KEY sécurisée

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiez la clé générée et utilisez-la dans votre fichier `.env`.

## Migrations et superutilisateur

### 1. Exécuter les migrations

```bash
cd ~/investlink
workon investlink-env
python manage.py migrate
```

### 2. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte admin.

### 3. Tester la configuration

```bash
python manage.py check --deploy
```

Cette commande vérifie que tout est correctement configuré pour la production.

## Finalisation

### 1. Recharger l'application

Dans l'onglet **"Web"**, cliquez sur le gros bouton vert **"Reload"**.

### 2. Vérifier que tout fonctionne

Visitez votre site : `https://VOTRE_USERNAME.pythonanywhere.com`

### 3. Accéder à l'admin Django

Visitez : `https://VOTRE_USERNAME.pythonanywhere.com/admin/`

## Mises à jour du code

Chaque fois que vous modifiez votre code sur GitHub :

```bash
# Dans une console Bash
cd ~/investlink
workon investlink-env

# Récupérer les dernières modifications
git pull

# Installer les nouvelles dépendances (si requirements.txt a changé)
pip install -r requirements.txt

# Exécuter les nouvelles migrations (si des modèles ont changé)
python manage.py migrate

# Collecter les nouveaux fichiers statiques
python manage.py collectstatic --noinput
```

Puis dans l'onglet **"Web"**, cliquez sur **"Reload"**.

## Dépannage

### Erreur 502 Bad Gateway

**Causes possibles :**
- Erreur de syntaxe dans le fichier WSGI
- Chemin du virtualenv incorrect
- Module Django non trouvé

**Solution :**
1. Vérifiez les logs d'erreur (onglet "Web" → liens "Error log" et "Server log")
2. Vérifiez les chemins dans le fichier WSGI
3. Assurez-vous que le virtualenv est correctement configuré

### Les fichiers statiques ne se chargent pas

**Solution :**
1. Vérifiez la configuration dans "Static files"
2. Assurez-vous d'avoir exécuté `collectstatic`
3. Vérifiez que le chemin pointe vers `staticfiles/` et non `static/`

### Erreur avec la base de données

**SQLite :**
```bash
# Vérifier que le fichier db.sqlite3 existe et a les bonnes permissions
cd ~/investlink
ls -la db.sqlite3
chmod 644 db.sqlite3
```

**PostgreSQL :**
- Vérifiez la variable `DATABASE_URL` dans `.env`
- Vérifiez que la base de données existe dans l'onglet "Databases"

### Les images/fichiers uploadés ne s'affichent pas

**En développement (SQLite) :**
- Configurez la section "Media files" dans l'onglet Web
- Chemin : `/home/VOTRE_USERNAME/investlink/media/`

**En production (avec Cloudinary) :**
- Vérifiez vos credentials Cloudinary dans `.env`
- Testez la connexion avec `python check_cloudinary.py`

### Erreur "DisallowedHost"

**Solution :**
Vérifiez `ALLOWED_HOSTS` dans votre fichier `.env` :
```bash
ALLOWED_HOSTS=VOTRE_USERNAME.pythonanywhere.com
```

### Voir les logs

Dans l'onglet **"Web"** :
- **Error log** : Erreurs Python/Django
- **Server log** : Erreurs du serveur web
- **Access log** : Requêtes HTTP

## Script de déploiement automatique

Pour faciliter les mises à jour, créez un script `deploy.sh` :

```bash
#!/bin/bash
cd ~/investlink
source ~/.virtualenvs/investlink-env/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
echo "Déploiement terminé ! N'oubliez pas de recharger l'app dans l'interface Web."
```

Rendez-le exécutable :
```bash
chmod +x deploy.sh
```

Utilisez-le :
```bash
./deploy.sh
```

## Ressources utiles

- [Documentation PythonAnywhere](https://help.pythonanywhere.com/)
- [Guide Django sur PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Forum PythonAnywhere](https://www.pythonanywhere.com/forums/)

## Support

En cas de problème :
1. Consultez les logs (Error log et Server log)
2. Vérifiez que toutes les étapes ont été suivies
3. Consultez le forum PythonAnywhere
4. Contactez le support PythonAnywhere (pour comptes payants)

---

**Bon déploiement ! 🚀**
