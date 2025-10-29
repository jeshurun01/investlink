---
tags:
summary: InvestLink
---
**1. Présentation générale du projet**

**1.1 Contexte**

Le projet **InvestLink** vise à créer une plateforme web innovante qui facilite la **rencontre entre porteurs de projets** en recherche de financement et **investisseurs** souhaitant placer leur capital dans des initiatives prometteuses.

La plateforme servira d’intermédiaire fiable, garantissant la **transparence**, la **sécurité** et la **qualité des projets publiés**.

**1.2 Objectifs**

- Offrir une vitrine de qualité aux projets à fort potentiel.
- Permettre aux investisseurs d’accéder à des opportunités filtrées et crédibles.
- Favoriser les échanges directs entre porteurs et investisseurs.
- Créer une communauté dynamique autour de l’investissement participatif.
- **Assurer un contrôle rigoureux des projets avant leur publication** afin de maintenir la fiabilité du site.

**1.3 Public cible**

- **Porteurs de projet** : entrepreneurs, startups, chercheurs, inventeurs.
- **Investisseurs** : particuliers, business angels, fonds d’investissement, entreprises.

**2. Identité visuelle et design**

**2.1 Charte graphique**

- Couleurs : **bleu foncé** (confiance), **vert** (croissance), **blanc** (transparence).
- Typographie : moderne et lisible (ex. Lato, Open Sans).
- Style : professionnel, minimaliste, sérieux.

**2.2 Univers visuel**

- Logo symbolisant la **connexion** et la **croissance** (ex. deux flèches entrelacées).
- Illustrations inspirant la **collaboration** et le **succès partagé**.

**3. Arborescence du site**

1. **Accueil** — Présentation du concept et appel à l’action.
2. **Découvrir les projets** — Liste filtrable des projets **validés** par la plateforme.
3. **Soumettre un projet** — Formulaire d’inscription pour les porteurs de projet.
4. **Espace investisseurs** — Informations, inscription et tableau de bord.
5. **À propos** — Vision, mission et équipe fondatrice.
6. **Actualités / Blog** — Articles et conseils en investissement.
7. **Contact / FAQ** — Formulaire, assistance et mentions légales.
8. **Espace membre** — Gestion du profil, messagerie, suivi des interactions.

**4. Fonctionnalités principales**

**4.1 Pour les porteurs de projet**

- Création d’un **profil détaillé** avec description, budget recherché, objectifs, réalisations, vidéos, documents de présentation, etc.
- Possibilité de **soumettre un projet** via un formulaire complet.
- Tableau de bord personnel pour suivre le statut du projet :
    - _Soumis → En cours d’examen → Validé / Refusé / En révision._
- Notifications automatiques à chaque étape du processus.

**4.2 Pour les investisseurs**

- Création d'un **profil investisseur** précisant les préférences (secteur, montant, type de risque, localisation).
- Accès uniquement aux projets **approuvés et publiés** par la plateforme.
- Outils de recherche et filtres avancés (secteur, rendement estimé, statut du projet, etc.).
- Messagerie interne sécurisée pour contacter les porteurs de projets.
- Tableau de bord pour suivre les projets suivis ou contactés.
- **Espace "États financiers mensuels"** présentant :
    - Les performances et rendements des entreprises dans lesquelles l'investisseur a placé son argent.
    - Des graphiques d'évolution du portefeuille.
    - Distribution des investissements par secteur.

**4.3 Pour l’administrateur (propriétaire de la plateforme)**

- Espace d’administration complet :
    - Gestion des comptes utilisateurs (investisseurs / porteurs).
    - **Validation manuelle et obligatoire des projets avant publication.**
    - Vérification des documents justificatifs (business plan, statuts, pièces d’identité, etc.).
    - Outils de modération et d’édition des contenus.
    - Tableau de bord des activités et statistiques globales.

**4.4 Fonctionnalités générales**

- Inscription et connexion sécurisées (email, authentification à deux facteurs).
- Système de messagerie interne.
- Notifications (email + tableau de bord).
- Interface responsive (ordinateurs, tablettes, smartphones).
- Gestion du RGPD et consentement des utilisateurs.

**4.5 Améliorations fonctionnelles - Page "Découvrir les projets"**

- **Statistiques globales de la plateforme** :
    - Nombre total de projets soumis sur la plateforme.
    - Nombre de projets validés et publiés.
    - Pourcentage de projets financés via la plateforme.
    - Montant total des financements réalisés.

- **Classement par secteur d'activité** (agriculture, technologie, énergie, santé, immobilier, etc.) :
    - Nombre de projets par secteur.
    - Présentation des équipes porteuses (photos, vidéos, réalisations).
    - Indicateur estimatif du **retour sur investissement (ROI)** potentiel.
    - Bouton **"Aller plus loin"** pour accéder aux détails complets du projet.

- **Restriction d'accès** :
    - ⚠️ L'accès complet aux détails des projets nécessite d'être **connecté en tant qu'investisseur**.
    - Les utilisateurs non connectés ou non investisseurs voient une version limitée avec incitation à s'inscrire.

**5. Contraintes techniques**

- **Langages / frameworks** : Django, Python (back-end) ; Html, javascript tailwind css (front-end).
- **Base de données** : sqlite3(Dev), MySQL(production)
- **Hébergement** : serveur cloud (OVH, AWS, ou équivalent).
- **Nom de domaine** : à définir.
- **Sécurité** :
    - Certificat SSL (HTTPS) obligatoire.
    - Système de validation et de modération.
    - Sauvegardes automatiques et cryptage des données.
    - Accès administrateur protégé.
- **SEO** : structure optimisée, métadonnées, compatibilité mobile.
    

**6. Processus de validation des projets (détail ajouté)**

1. **Soumission du projet** par le porteur via son espace membre.
2. **Vérification automatique** des informations de base (champs obligatoires, format, pièces jointes).
3. **Analyse manuelle** par l’équipe administrative (documents, faisabilité, conformité).
4. **Décision** :
    - ✅ _Projet validé_ → publication sur la plateforme.
    - ❌ _Projet refusé_ → notification au porteur avec motif.
    - 🔁 _Projet en révision_ → retour au porteur pour ajustement.
5. **Publication finale** uniquement après validation officielle par la plateforme propriétaire.

💡 **Objectif :** garantir la qualité, la transparence et la fiabilité des projets publiés afin de renforcer la confiance des investisseurs.

**7. Planning prévisionnel**
  
|**Étape**|**Description**|**Durée estimée**|
|---|---|---|
|1|Rédaction du cahier des charges final|1 semaine|
|2|Maquettes et charte graphique|2 semaines|
|3|Développement MVP (prototype fonctionnel)|5 à 6 semaines|
|4|Phase de test et validation interne|2 semaines|
|5|Mise en ligne officielle|1 semaine|
|**Total estimé**|≈ **11 à 12 semaines**||

**8. Budget prévisionnel**

|**Poste**|**Estimation (€)**|
|---|---|
|Design et identité visuelle|1 000 – 2 000|
|Développement plateforme|5 000 – 9 000|
|Hébergement & maintenance (1 an)|300 – 800|
|Communication & marketing de lancement|500 – 1 000|
|**Total estimé**|≈ **6 800 à 12 800 €**|

**9. Critères de réussite**

- Taux d’approbation et de publication de projets.
- Nombre d’investisseurs actifs.
- Volume d’échanges entre utilisateurs.
- Qualité perçue (retours positifs des utilisateurs).
- Sécurité et stabilité technique du site.

**10. Évolutions futures**

- Application mobile (iOS / Android).
- Système de notation des projets et investisseurs.
- Automatisation partielle du contrôle documentaire.
- Intégration de solutions de paiement sécurisées.
- Outils de reporting et de statistiques d’investissement.