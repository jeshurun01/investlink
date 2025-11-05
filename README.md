# 🚀 InvestLink - Plateforme d'Investissement

Plateforme Django de mise en relation entre porteurs de projets et investisseurs.

## 🔥 ATTENTION : Perte de Données sur Render ?

**Si vous perdez vos données à chaque déploiement**, consultez immédiatement :
- **📕 URGENCE_PERTE_DONNEES.md** - Guide visuel avec solution en 30 minutes
- **📘 POSTGRESQL_MIGRATION.md** - Guide rapide de migration
- **📗 backup_restore_guide.md** - Guide complet de sauvegarde/restauration

**Solution** : Migrer de SQLite vers PostgreSQL (gratuit sur Render).

---

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Déploiement](#-déploiement)
- [Documentation](#-documentation)
- [Technologies](#-technologies)

---

## ✨ Fonctionnalités

### Pour les Porteurs de Projets
- ✅ Soumission de projets avec documents multiples
- ✅ Suivi du statut de validation
- ✅ Dashboard avec statistiques
- ✅ Visualisation des investisseurs
- ✅ Messagerie intégrée

### Pour les Investisseurs
- ✅ Découverte de projets validés
- ✅ Filtres et recherche avancée
- ✅ Système de favoris
- ✅ Déclaration d'investissement
- ✅ États financiers avec graphiques
- ✅ Calcul automatique du ROI

### Pour les Administrateurs
- ✅ Validation des projets
- ✅ Validation des investissements
- ✅ Gestion des utilisateurs
- ✅ Système de blog/actualités
- ✅ Messages de contact
- ✅ Logs d'activité

### Fonctionnalités Générales
- ✅ Authentification sécurisée
- ✅ Système de notifications
- ✅ Messagerie interne
- ✅ Design responsive (desktop + mobile)
- ✅ Menu mobile moderne
- ✅ Toast notifications
- ✅ Profils utilisateurs personnalisés

---

## 🛠️ Installation

### Prérequis

- Python 3.12+
- PostgreSQL (recommandé) ou SQLite (dev uniquement)
- UV (gestionnaire de packages ultra-rapide)

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/jeshurun01/investlink.git
cd investlink

# Installer UV (si pas déjà installé)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Créer l'environnement virtuel et installer les dépendances
uv venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env

# Générer une SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Coller la clé dans .env

# Exécuter les migrations
python manage.py migrate

# Créer un superuser
python manage.py create_admin

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Lancer le serveur
python manage.py runserver
```

Visitez : http://localhost:8000

---

## 🚀 Déploiement

### Render (Recommandé)

Consultez le guide complet : **RENDER_DEPLOYMENT.md**

#### Configuration Rapide

1. **Créer PostgreSQL** sur Render (gratuit)
2. **Configurer les variables d'environnement** :
   ```
   SECRET_KEY=<générer-une-clé>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=<url-postgresql>
   ```
3. **Build Command** : `./build.sh`
4. **Start Command** : `gunicorn config.wsgi:application`
5. **Ajouter un Persistent Disk** pour les fichiers media :
   - Mount Path : `/opt/render/project/src/media`
   - Size : 1GB

#### Important : Éviter la Perte de Données

⚠️ **Ne JAMAIS utiliser SQLite en production sur Render !**

Les données SQLite sont supprimées à chaque déploiement. Utilisez PostgreSQL.

Guides disponibles :
- **URGENCE_PERTE_DONNEES.md** - Solution en 30 minutes
- **POSTGRESQL_MIGRATION.md** - Migration rapide
- **backup_restore_guide.md** - Sauvegarde/restauration

---

## 📚 Documentation

### Guides de Déploiement
- **RENDER_DEPLOYMENT.md** - Déploiement complet sur Render
- **POSTGRESQL_MIGRATION.md** - Migration SQLite → PostgreSQL
- **URGENCE_PERTE_DONNEES.md** - Solution urgente perte de données

### Guides Techniques
- **backup_restore_guide.md** - Sauvegarde et restauration
- **PLAN_ACTION.md** - Plan de développement détaillé

### Scripts Utiles

```bash
# Sauvegarder les données
python backup_data.py              # Sauvegarde complète
python backup_data.py --app users  # Sauvegarde d'une app
python backup_data.py --all        # Toutes les apps séparément

# Restaurer les données
python restore_data.py backups/backup_full_20251105.json

# Créer un admin (local ou Render)
python manage.py create_admin --username=admin --email=admin@example.com
```

---

## 🏗️ Technologies

### Backend
- **Django 5.2.7** - Framework web Python
- **PostgreSQL** - Base de données (production)
- **SQLite** - Base de données (développement)
- **Gunicorn** - Serveur WSGI
- **WhiteNoise** - Gestion des fichiers statiques

### Frontend
- **Tailwind CSS 3.x** - Framework CSS
- **Alpine.js** - Framework JavaScript léger
- **Chart.js** - Graphiques interactifs
- **Font Awesome** - Icônes

### Infrastructure
- **Render** - Hébergement
- **UV** - Gestionnaire de packages Python (10-100x plus rapide que pip)
- **Git/GitHub** - Contrôle de version

---

## 📁 Structure du Projet

```
investlink/
├── config/              # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/               # Gestion des utilisateurs
├── projects/            # Gestion des projets
├── messaging/           # Messagerie interne
├── notifications/       # Système de notifications
├── core/                # Fonctionnalités communes (blog, contact)
├── templates/           # Templates HTML
│   ├── base.html
│   ├── users/
│   ├── projects/
│   ├── messaging/
│   ├── notifications/
│   └── core/
├── static/              # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
├── media/               # Fichiers uploadés (non versionné)
├── backups/             # Sauvegardes (non versionné)
├── backup_data.py       # Script de sauvegarde
├── restore_data.py      # Script de restauration
├── build.sh             # Script de build Render
├── Procfile             # Configuration Render
└── requirements.txt     # Dépendances Python
```

---

## 🔐 Sécurité

- ✅ HTTPS forcé en production
- ✅ CSRF protection
- ✅ XSS protection
- ✅ SQL Injection protection (ORM Django)
- ✅ Mots de passe hashés (PBKDF2)
- ✅ Sessions sécurisées
- ✅ Validation côté serveur
- ✅ Limitation des uploads

---

## 🐛 Dépannage

### Perte de données sur Render

**Problème** : Données supprimées à chaque build
**Solution** : Migrer vers PostgreSQL (voir URGENCE_PERTE_DONNEES.md)

### Images non visibles en production

**Problème** : Fichiers media non servis
**Solutions** :
1. Configurer un Persistent Disk sur Render
2. Utiliser Cloudinary (recommandé)
3. Voir RENDER_DEPLOYMENT.md

### Erreur de migration

```bash
python manage.py migrate --fake-initial
```

### Static files non chargés

```bash
python manage.py collectstatic --no-input
```

---

## 📊 Statistiques

- **5 apps Django** - Architecture modulaire
- **50+ templates** - Design cohérent
- **30+ vues** - Fonctionnalités complètes
- **15+ modèles** - Base de données structurée
- **100% responsive** - Mobile et desktop

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

**Jeshurun Nasser**
- GitHub: [@jeshurun01](https://github.com/jeshurun01)
- Email: contact@investlink.com

---

## 🙏 Remerciements

- Django Community
- Tailwind CSS Team
- Render Platform
- Font Awesome
- Chart.js

---

## 📞 Support

- **Documentation** : Voir les guides dans le dossier racine
- **Issues** : [GitHub Issues](https://github.com/jeshurun01/investlink/issues)
- **Email** : support@investlink.com

---

**Version** : 1.0.0  
**Dernière mise à jour** : 5 novembre 2025

---

## 🎯 Roadmap

- [ ] Authentification à deux facteurs (2FA)
- [ ] Validation d'email
- [ ] Workflow d'activation de compte motivée
- [ ] Export PDF/Excel des états financiers
- [ ] Notifications email SMTP
- [ ] Application mobile (React Native)
- [ ] API REST pour intégrations
- [ ] Tests automatisés complets
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring avancé (Sentry)

---

**🎉 Prêt à révolutionner l'investissement en RDC !**
