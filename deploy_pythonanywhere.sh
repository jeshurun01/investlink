#!/bin/bash

# ======================================
# Script de déploiement PythonAnywhere
# ======================================
# Ce script automatise les tâches de mise à jour après un push sur GitHub
# 
# Utilisation :
# 1. Rendez-le exécutable : chmod +x deploy_pythonanywhere.sh
# 2. Exécutez-le : ./deploy_pythonanywhere.sh
# 3. Rechargez l'app dans l'interface Web PythonAnywhere

set -e  # Arrêter en cas d'erreur

echo "========================================"
echo "Déploiement InvestLink sur PythonAnywhere"
echo "========================================"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ======================================
# 1. Vérifier qu'on est dans le bon dossier
# ======================================
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Erreur: manage.py non trouvé. Êtes-vous dans le bon dossier ?${NC}"
    exit 1
fi

# ======================================
# 2. Activer l'environnement virtuel
# ======================================
echo -e "${BLUE}Activation de l'environnement virtuel...${NC}"
if [ -d "$HOME/.virtualenvs/investlink-env" ]; then
    source "$HOME/.virtualenvs/investlink-env/bin/activate"
    echo -e "${GREEN}✓ Environnement activé${NC}"
else
    echo -e "${RED}Erreur: Environnement virtuel non trouvé${NC}"
    echo "Créez-le avec: mkvirtualenv --python=/usr/bin/python3.10 investlink-env"
    exit 1
fi

# ======================================
# 3. Récupérer les dernières modifications
# ======================================
echo -e "\n${BLUE}Récupération des modifications depuis GitHub...${NC}"
git pull
echo -e "${GREEN}✓ Code mis à jour${NC}"

# ======================================
# 4. Installer/Mettre à jour les dépendances
# ======================================
echo -e "\n${BLUE}Installation des dépendances...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dépendances installées${NC}"

# ======================================
# 5. Exécuter les migrations
# ======================================
echo -e "\n${BLUE}Exécution des migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations appliquées${NC}"

# ======================================
# 6. Collecter les fichiers statiques
# ======================================
echo -e "\n${BLUE}Collection des fichiers statiques...${NC}"
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}✓ Fichiers statiques collectés${NC}"

# ======================================
# 7. Vérifier la configuration
# ======================================
echo -e "\n${BLUE}Vérification de la configuration...${NC}"
python manage.py check --deploy --quiet
echo -e "${GREEN}✓ Configuration OK${NC}"

# ======================================
# 8. Afficher un résumé
# ======================================
echo -e "\n========================================"
echo -e "${GREEN}Déploiement terminé avec succès ! ✓${NC}"
echo "========================================"
echo -e "\n${BLUE}Prochaines étapes :${NC}"
echo "1. Allez sur https://www.pythonanywhere.com"
echo "2. Cliquez sur l'onglet 'Web'"
echo "3. Cliquez sur le bouton vert 'Reload' pour redémarrer votre application"
echo ""
echo "Votre site sera ensuite mis à jour !"
echo "========================================"
