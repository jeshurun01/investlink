# Guide d'Administration du Blog InvestLink

## Accès à l'Interface d'Administration

Votre application Django dispose déjà d'un système de blog complet et professionnel !

### 1. Connexion à l'Admin Django
- URL: `http://127.0.0.1:8000/admin/`
- **Username:** `admin`
- **Password:** `admin123`

### 2. Gestion des Articles de Blog

#### Via l'Admin Django (Recommandé)
Une fois connecté, vous verrez dans le panneau d'administration :

**Section "CORE"** :
- **Articles de blog** : Créer, modifier, publier vos articles
- **Catégories** : Gérer les catégories d'articles

#### Fonctionnalités Améliorées

L'interface admin a été améliorée avec :

✅ **Aperçu des images** : Voir les images directement dans la liste et le formulaire  
✅ **Édition rapide du statut** : Changer le statut (brouillon/publié) directement depuis la liste  
✅ **Actions groupées** :
   - Publier plusieurs articles en même temps
   - Mettre en brouillon plusieurs articles
✅ **Publication automatique** : La date de publication est définie automatiquement lors de la publication  
✅ **Compteur de vues** : Suivez le nombre de vues de chaque article  
✅ **Organisation SEO** : Champs méta-description pour le référencement  

### 3. Créer un Nouvel Article

1. Cliquez sur **"Articles de blog"** dans l'admin
2. Cliquez sur **"AJOUTER ARTICLE DE BLOG"** en haut à droite
3. Remplissez les champs :
   - **Titre** : Le titre de votre article
   - **Slug** : Généré automatiquement depuis le titre
   - **Catégorie** : Sélectionnez ou créez une catégorie
   - **Image à la une** : Téléchargez une image
   - **Extrait** : Un résumé court (affiché dans la liste)
   - **Contenu** : Le texte complet de l'article
   - **Tags** : Mots-clés séparés par des virgules
   - **Statut** : 
     - `Brouillon` : L'article n'est pas visible publiquement
     - `Publié` : L'article est visible sur le site
   - **Meta description** : Pour le SEO (optionnel)

4. Cliquez sur **"ENREGISTRER"** ou **"ENREGISTRER ET CONTINUER À MODIFIER"**

### 4. Gérer les Catégories

1. Dans l'admin, cliquez sur **"Catégories"**
2. Créez de nouvelles catégories pour organiser vos articles :
   - Investissement
   - Actualités
   - Conseils
   - Analyses de marché
   - Etc.

### 5. URLs du Blog Public

Les articles sont accessibles publiquement à :
- **Liste des articles** : `http://127.0.0.1:8000/blog/`
- **Article individuel** : `http://127.0.0.1:8000/blog/mon-article/`

### 6. Fonctionnalités du Blog Public

Le blog dispose de :
- ✅ Filtrage par catégories
- ✅ Recherche d'articles
- ✅ Pagination
- ✅ Compteur de vues
- ✅ Articles en vedette
- ✅ Design responsive (mobile, tablette, desktop)

### 7. Actions Rapides dans l'Admin

#### Depuis la liste des articles :
- **Modifier le statut** : Changez directement brouillon ↔ publié
- **Actions groupées** : Sélectionnez plusieurs articles et :
  - Choisissez "Publier les articles sélectionnés"
  - Ou "Mettre en brouillon les articles sélectionnés"
  - Puis cliquez sur "Exécuter"

#### Tri et filtres :
- Filtrez par statut, catégorie, date de création ou publication
- Recherchez dans les titres, contenus et tags
- Naviguez par date avec la hiérarchie temporelle

### 8. Astuces pour de Meilleurs Articles

1. **Images** : Utilisez des images de haute qualité (recommandé : 1200x630px)
2. **Extrait** : Rédigez un extrait accrocheur (max 300 caractères)
3. **Tags** : Ajoutez des tags pertinents séparés par des virgules
4. **SEO** : Remplissez la meta description (160 caractères max)
5. **Brouillon d'abord** : Créez en brouillon, relisez, puis publiez

### 9. Workflow Recommandé

```
1. Créer un brouillon
   ↓
2. Ajouter le contenu et les images
   ↓
3. Prévisualiser (sauvegarder en brouillon)
   ↓
4. Vérifier l'affichage sur le blog public
   ↓
5. Changer le statut en "Publié"
   ↓
6. Article visible instantanément !
```

## Support Technique

Si vous rencontrez des problèmes :
1. Vérifiez que le serveur est démarré : `uv run python manage.py runserver`
2. Consultez les logs dans le terminal
3. Assurez-vous d'être connecté avec le compte admin

## Prochaines Étapes

Vous pouvez maintenant :
- ✅ Créer vos premiers articles de blog
- ✅ Organiser par catégories
- ✅ Publier et gérer le contenu
- ✅ Suivre les statistiques de vues

**Bon blogging ! 📝✨**
