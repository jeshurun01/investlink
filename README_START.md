# 🚀 Guide de démarrage rapide - InvestLink

## 📝 Résumé du projet

**InvestLink** est une plateforme de mise en relation entre porteurs de projets et investisseurs.

- **Stack** : Django 5.2.7, Python, Tailwind CSS
- **Base de données** : SQLite (dev), MySQL (prod)
- **Applications** : users, projects, messaging, notifications, core

---

## 🎯 Phase 1 : TERMINÉE ✅

La configuration initiale et l'architecture du projet sont complètes :
- ✅ 5 applications Django créées
- ✅ 10 modèles de données définis
- ✅ Migrations appliquées
- ✅ Interface admin configurée
- ✅ Templates de base créés
- ✅ Tailwind CSS configuré

📄 Voir : `PHASE_1_COMPLETE.md` pour plus de détails

---

## ⚡ Démarrage rapide

### 1. Lancer le serveur Django
```bash
uv run manage.py runserver
```
➡️ Accéder à : http://127.0.0.1:8000/

### 2. Accéder à l'admin
```bash
# URL : http://127.0.0.1:8000/admin/
# Username : admin
# Password : (celui que vous avez défini)
```

### 3. Compiler Tailwind CSS
```bash
# Installation des dépendances (première fois seulement)
npm install

# Compiler le CSS
npm run build:css

# OU en mode watch pour développement
npm run watch:css
```

---

## 📂 Structure du projet

```
investlink/
├── users/          # Gestion des utilisateurs (porteur, investisseur, admin)
├── projects/       # Gestion des projets et validation
├── messaging/      # Messagerie interne
├── notifications/  # Système de notifications
├── core/           # Pages publiques (accueil, about, etc.)
├── templates/      # Templates HTML
├── static/         # CSS, JS, images
├── media/          # Fichiers uploadés
└── config/         # Configuration Django
```

---

## 🎨 Modèles de données

### Users
- **User** : Utilisateur avec 3 types (porteur, investisseur, admin)
- **ProjectOwnerProfile** : Profil détaillé des porteurs
- **InvestorProfile** : Profil détaillé des investisseurs

### Projects
- **Project** : Projet avec workflow de validation (5 statuts)
- **ProjectDocument** : Documents attachés (business plan, etc.)
- **ProjectFavorite** : Favoris des investisseurs

### Messaging
- **Conversation** : Conversations entre 2 utilisateurs
- **Message** : Messages dans une conversation

### Notifications
- **Notification** : 8 types de notifications

---

## 🔄 Workflow de validation des projets

1. **Submitted** (Soumis) : Le porteur soumet son projet
2. **Under Review** (En examen) : L'admin examine le projet
3. **Revision Requested** (Révision demandée) : L'admin demande des modifications
4. **Approved** (Validé) : Projet publié et visible par les investisseurs
5. **Rejected** (Refusé) : Projet refusé avec motif

---

## 🎯 Prochaines étapes (Phase 2)

### À développer maintenant :

1. **Formulaires d'inscription**
   - Formulaire porteur de projet
   - Formulaire investisseur
   - Validation d'email

2. **Formulaire de soumission de projet**
   - Champs complets
   - Upload de documents
   - Upload d'images/vidéos

3. **Dashboard porteur**
   - Liste de mes projets
   - Statut de validation
   - Statistiques

4. **Dashboard investisseur**
   - Projets favoris
   - Filtres avancés
   - Historique

5. **Messagerie**
   - Interface de chat
   - Notifications en temps réel
   - Marquer comme lu

6. **Système de validation admin**
   - Interface de modération
   - Vérification de documents
   - Actions groupées

---

## 📚 Fichiers utiles

- `PLAN_ACTION.md` - Plan complet avec toutes les tâches
- `PHASE_1_COMPLETE.md` - Résumé de ce qui a été fait
- `COMMANDES_UTILES.md` - Commandes Django et Git
- `Cahier des charges.md` - Spécifications du projet
- `.env` - Variables d'environnement (NE PAS COMMITTER)
- `.env.example` - Template des variables d'environnement

---

## 🐛 Debugging

### Si le serveur ne démarre pas
```bash
# Vérifier les migrations
uv run manage.py migrate

# Vérifier les erreurs
uv run manage.py check
```

### Si Tailwind CSS ne fonctionne pas
```bash
# Installer les dépendances
npm install

# Compiler le CSS
npm run build:css
```

### Si l'admin ne s'affiche pas
```bash
# Vérifier le superutilisateur
uv run manage.py createsuperuser
```

---

## 💡 Conseils

1. **Toujours tester** après chaque modification importante
2. **Committer régulièrement** avec des messages clairs
3. **Utiliser des branches** pour les nouvelles fonctionnalités
4. **Documenter** les nouvelles fonctionnalités
5. **Suivre le plan** dans `PLAN_ACTION.md`

---

## 📞 URLs principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/admin/` | Interface d'administration |
| `/users/register/` | Inscription |
| `/users/login/` | Connexion |
| `/users/dashboard/` | Dashboard utilisateur |
| `/projects/` | Liste des projets |
| `/projects/submit/` | Soumettre un projet |
| `/messages/` | Messagerie |
| `/notifications/` | Notifications |

---

## 🎨 Charte graphique

- **Bleu foncé** : `#1e3a8a` (confiance, professionnalisme)
- **Vert** : `#059669` (croissance, succès)
- **Blanc** : `#ffffff` (transparence, clarté)

---

## ✅ Checklist avant de continuer

- [ ] Le serveur Django fonctionne
- [ ] L'admin est accessible
- [ ] Tailwind CSS est compilé
- [ ] Les migrations sont appliquées
- [ ] Un superutilisateur existe
- [ ] La page d'accueil s'affiche

**Tout est ✅ ?** Vous êtes prêt pour la Phase 2 ! 🚀

---

**Bon développement ! 💪**
