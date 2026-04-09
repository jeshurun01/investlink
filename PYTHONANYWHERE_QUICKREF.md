# PythonAnywhere - Aide-mémoire Rapide

## 🚀 Déploiement Initial (faire une seule fois)

```bash
# 1. Cloner le projet
cd ~
git clone https://github.com/jeshurun01/investlink.git
cd investlink

# 2. Créer l'environnement virtuel
mkvirtualenv --python=/usr/bin/python3.10 investlink-env

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
nano .env
# (copier le contenu de .env.pythonanywhere.example et adapter)

# 5. Exécuter les migrations
python manage.py migrate

# 6. Créer un superutilisateur
python manage.py createsuperuser

# 7. Collecter les fichiers statiques
python manage.py collectstatic

# 8. Configurer l'interface Web PythonAnywhere (voir guide)
```

## 🔄 Mise à jour (après chaque modification)

```bash
# Méthode 1 : Script automatique
cd ~/investlink
./deploy_pythonanywhere.sh

# Méthode 2 : Manuel
cd ~/investlink
workon investlink-env
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**Puis :** Recharger l'app dans l'interface Web !

## 📁 Configuration Interface Web

### Static Files
- URL: `/static/`
- Directory: `/home/VOTRE_USERNAME/investlink/staticfiles/`

### Media Files (développement)
- URL: `/media/`
- Directory: `/home/VOTRE_USERNAME/investlink/media/`

### Virtualenv
- Path: `/home/VOTRE_USERNAME/.virtualenvs/investlink-env`

### WSGI
- Fichier: `/var/www/VOTRE_USERNAME_pythonanywhere_com_wsgi.py`
- Contenu: Utiliser `pythonanywhere_wsgi.py`

## 🛠️ Commandes Utiles

```bash
# Activer l'environnement
workon investlink-env

# Désactiver l'environnement
deactivate

# Voir les environnements disponibles
lsvirtualenv

# Migrations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Créer un superutilisateur
python manage.py createsuperuser

# Vérifier la configuration
python manage.py check --deploy

# Shell Django
python manage.py shell

# Voir les logs
tail -f /var/log/VOTRE_USERNAME.pythonanywhere.com.error.log
tail -f /var/log/VOTRE_USERNAME.pythonanywhere.com.server.log
```

## 🔐 Variables d'Environnement Essentielles

```bash
DEBUG=False
SECRET_KEY=votre-clé-générée
ALLOWED_HOSTS=VOTRE_USERNAME.pythonanywhere.com
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

## 🆘 Dépannage Express

| Problème | Solution |
|----------|----------|
| Erreur 502 | Vérifier logs d'erreur + fichier WSGI |
| Fichiers statiques manquants | `collectstatic` + config interface Web |
| DisallowedHost | Vérifier `ALLOWED_HOSTS` dans `.env` |
| Module non trouvé | `pip install -r requirements.txt` |
| Base de données | `python manage.py migrate` |

## 📍 URLs Importantes

- Site: `https://VOTRE_USERNAME.pythonanywhere.com`
- Admin: `https://VOTRE_USERNAME.pythonanywhere.com/admin/`
- Dashboard: `https://www.pythonanywhere.com/user/VOTRE_USERNAME/`
- Logs: Onglet "Web" → Error log / Server log

## 💡 Astuces

- Toujours recharger l'app après modification du code
- Vérifier les logs en cas d'erreur
- Tester en local avant de déployer
- Faire des commits réguliers sur GitHub
- Garder le `.env` secret (ne jamais commit)

## 🔗 Liens Utiles

- [Documentation PythonAnywhere](https://help.pythonanywhere.com/)
- [Guide Django](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Forum Support](https://www.pythonanywhere.com/forums/)

---
💡 **Conseil :** Gardez ce fichier ouvert pendant que vous déployez !
