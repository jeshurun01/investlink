"""
Configuration WSGI pour PythonAnywhere - InvestLink

Ce fichier doit être copié dans votre fichier WSGI PythonAnywhere :
/var/www/VOTRE_USERNAME_pythonanywhere_com_wsgi.py

Instructions:
1. Sur PythonAnywhere, allez dans l'onglet "Web"
2. Cliquez sur le lien du fichier WSGI
3. Remplacez tout le contenu par ce fichier
4. Remplacez VOTRE_USERNAME par votre nom d'utilisateur PythonAnywhere
5. Sauvegardez et rechargez votre application web
"""

import os
import sys

# ======================================
# CONFIGURATION DES CHEMINS
# ======================================
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur PythonAnywhere
# Par exemple : /home/jeshurun01/investlink
path = '/home/VOTRE_USERNAME/investlink'

if path not in sys.path:
    sys.path.insert(0, path)

# ======================================
# DJANGO SETTINGS MODULE
# ======================================
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# ======================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ======================================
from pathlib import Path
import environ

env = environ.Env()
env_file = Path(path) / '.env'

if env_file.exists():
    environ.Env.read_env(str(env_file))
else:
    print(f"ATTENTION: Fichier .env non trouvé à {env_file}")
    print("Créez un fichier .env avec vos variables d'environnement")

# ======================================
# INITIALISATION DJANGO
# ======================================
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
