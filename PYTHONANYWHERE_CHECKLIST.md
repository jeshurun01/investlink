# PythonAnywhere - Checklist de Déploiement

Cochez chaque étape au fur et à mesure ✅

## Phase 1 : Préparation (Local)

- [ ] Code testé et fonctionnel en local
- [ ] Tous les commits poussés sur GitHub
- [ ] Compte PythonAnywhere créé et email confirmé
- [ ] Credentials Cloudinary obtenus (cloud_name, api_key, api_secret)
- [ ] SECRET_KEY générée (ne pas utiliser celle de développement)

## Phase 2 : Configuration PythonAnywhere

### Console Bash

- [ ] Console Bash ouverte
- [ ] Repository cloné : `git clone https://github.com/jeshurun01/investlink.git`
- [ ] Dossier investlink accessible : `cd ~/investlink`
- [ ] Environnement virtuel créé : `mkvirtualenv --python=/usr/bin/python3.10 investlink-env`
- [ ] Dépendances installées : `pip install -r requirements.txt`

### Fichier .env

- [ ] Fichier créé : `nano ~/investlink/.env`
- [ ] `DEBUG=False` ajouté
- [ ] `SECRET_KEY` générée et ajoutée
- [ ] `ALLOWED_HOSTS` configuré avec votre username PythonAnywhere
- [ ] Credentials Cloudinary ajoutés (CLOUDINARY_CLOUD_NAME, API_KEY, API_SECRET)
- [ ] Fichier sauvegardé (Ctrl+X, Y, Enter)

### Base de données

- [ ] Migrations exécutées : `python manage.py migrate`
- [ ] Superutilisateur créé : `python manage.py createsuperuser`
- [ ] Login admin noté (username et password)

### Fichiers statiques

- [ ] Fichiers collectés : `python manage.py collectstatic`
- [ ] Dossier `staticfiles/` créé et rempli

## Phase 3 : Interface Web PythonAnywhere

### Création de l'application

- [ ] Onglet "Web" ouvert
- [ ] "Add a new web app" cliqué
- [ ] "Manual configuration" sélectionné
- [ ] Python 3.10 choisi
- [ ] Application créée

### Configuration Static Files

- [ ] Section "Static files" trouvée
- [ ] Entrée ajoutée :
  - URL : `/static/`
  - Directory : `/home/VOTRE_USERNAME/investlink/staticfiles/`
- [ ] **Username remplacé par votre vrai username**

### Configuration Media Files (optionnel développement)

- [ ] Entrée ajoutée :
  - URL : `/media/`
  - Directory : `/home/VOTRE_USERNAME/investlink/media/`
- [ ] **Username remplacé par votre vrai username**

### Configuration du Virtualenv

- [ ] Section "Virtualenv" trouvée
- [ ] Chemin entré : `/home/VOTRE_USERNAME/.virtualenvs/investlink-env`
- [ ] **Username remplacé par votre vrai username**
- [ ] Checkmark bleu cliqué pour sauvegarder

### Configuration WSGI

- [ ] Lien du fichier WSGI cliqué
- [ ] Fichier local `pythonanywhere_wsgi.py` ouvert
- [ ] Contenu copié dans le fichier WSGI PythonAnywhere
- [ ] **VOTRE_USERNAME remplacé dans le fichier (ligne du path)**
- [ ] Fichier sauvegardé

## Phase 4 : Lancement

### Premier démarrage

- [ ] Bouton vert "Reload" cliqué
- [ ] Site visité : `https://VOTRE_USERNAME.pythonanywhere.com`
- [ ] Page d'accueil s'affiche correctement
- [ ] Admin accessible : `https://VOTRE_USERNAME.pythonanywhere.com/admin/`
- [ ] Connexion admin réussie

### Tests fonctionnels

- [ ] Navigation entre les pages fonctionne
- [ ] Fichiers statiques chargés (CSS, JS, images)
- [ ] Formulaires fonctionnent
- [ ] Upload d'images fonctionne (via Cloudinary)
- [ ] Messages d'erreur affichés correctement (tester une connexion invalide)

## Phase 5 : Vérifications finales

### Logs

- [ ] Error log consulté (aucune erreur critique)
- [ ] Server log consulté (requêtes s'affichent normalement)

### Sécurité

- [ ] `DEBUG=False` confirmé dans .env
- [ ] Fichier .env non accessible publiquement
- [ ] SECRET_KEY différente de celle de développement
- [ ] ALLOWED_HOSTS correctement configuré

### Configuration Django

- [ ] Check de déploiement exécuté : `python manage.py check --deploy`
- [ ] Avertissements de sécurité résolus (si présents)

## Phase 6 : Documentation

- [ ] Credentials admin sauvegardés dans un endroit sûr
- [ ] URL du site notée
- [ ] Procédure de mise à jour documentée pour l'équipe

## Mise à jour future (Checklist rapide)

Chaque fois que vous modifiez le code :

- [ ] Code commité et poussé sur GitHub
- [ ] Console Bash ouverte sur PythonAnywhere
- [ ] `cd ~/investlink`
- [ ] `workon investlink-env`
- [ ] `git pull`
- [ ] `pip install -r requirements.txt` (si requirements changé)
- [ ] `python manage.py migrate` (si modèles changés)
- [ ] `python manage.py collectstatic --noinput` (si static changés)
- [ ] Bouton "Reload" cliqué dans l'interface Web
- [ ] Site testé

## En cas de problème

### Erreur 502 Bad Gateway
- [ ] Error log consulté
- [ ] Fichier WSGI vérifié (syntaxe et chemins)
- [ ] Virtualenv vérifié
- [ ] Reload effectué

### Static files manquants
- [ ] `collectstatic` réexécuté
- [ ] Configuration "Static files" vérifiée
- [ ] Chemin vers `staticfiles/` (pas `static/`)

### DisallowedHost
- [ ] ALLOWED_HOSTS dans .env vérifié
- [ ] Exact match avec l'URL visitée
- [ ] Reload effectué après modification

### Erreurs de base de données
- [ ] Migrations exécutées : `python manage.py migrate`
- [ ] Permissions fichier SQLite vérifiées
- [ ] DATABASE_URL dans .env vérifié (si PostgreSQL)

## Ressources

- [ ] Guide complet lu : `PYTHONANYWHERE_DEPLOYMENT.md`
- [ ] Quick reference bookmarked : `PYTHONANYWHERE_QUICKREF.md`
- [ ] Documentation PythonAnywhere consultée si besoin

---

## 🎉 Félicitations !

Si toutes les cases sont cochées, votre application est déployée avec succès !

**URL de votre site :** `https://VOTRE_USERNAME.pythonanywhere.com`

**Prochaines étapes suggérées :**
- Configurer un domaine personnalisé (compte payant)
- Mettre en place une stratégie de backup
- Configurer le monitoring
- Optimiser les performances

---

**Date de déploiement :** _______________
**Version déployée :** _______________
**Notes :** 
_________________________________________
_________________________________________
_________________________________________
