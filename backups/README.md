# Dossier de sauvegardes

Ce dossier contient les sauvegardes des données de la base de données.

## 📋 Instructions

### Créer une sauvegarde

```bash
# Sauvegarde complète
python backup_data.py

# Sauvegarde d'une app spécifique
python backup_data.py --app users

# Sauvegarder toutes les apps séparément
python backup_data.py --all
```

### Restaurer une sauvegarde

```bash
python restore_data.py backups/backup_full_20251105_143000.json
```

## ⚠️ Important

- Les fichiers de sauvegarde ne doivent **PAS** être versionnés dans Git (ajoutés au .gitignore)
- Conservez les sauvegardes dans un lieu sûr (cloud, disque externe)
- Testez régulièrement vos sauvegardes en les restaurant sur un environnement de test

## 📅 Fréquence Recommandée

- **Quotidien** : En production active
- **Hebdomadaire** : En développement
- **Avant chaque déploiement** : Toujours !

## 🔒 Sécurité

Les fichiers de sauvegarde peuvent contenir des données sensibles :
- Mots de passe hashés
- Emails d'utilisateurs
- Données personnelles

Protégez-les en conséquence !
