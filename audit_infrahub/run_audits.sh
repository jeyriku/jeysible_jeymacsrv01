#!/bin/bash
# Script d'exemple pour exécuter les audits Infrahub

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}    Audit Infrahub - Exemple d'utilisation     ${NC}"
echo -e "${GREEN}================================================${NC}\n"

# Vérifier que les dépendances sont installées
if ! python3 -c "import requests, dotenv" 2>/dev/null; then
    echo -e "${YELLOW}Installation des dépendances...${NC}"
    pip3 install -r requirements.txt
    echo ""
fi

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    echo -e "Copier .env.example vers .env et configurer vos paramètres:"
    echo -e "  cp .env.example .env"
    echo -e "  vim .env"
    echo ""
    echo -e "Ou exporter les variables d'environnement:"
    echo -e "  export INFRAHUB_API_URL=\"http://jeysrv10:8080\""
    echo -e "  export INFRAHUB_API_TOKEN=\"votre_token\""
    echo ""
fi

# Timestamp pour les rapports
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}1. Audit des devices...${NC}"
python3 check_devices.py -o reports/audit_devices_${TIMESTAMP}.json
echo ""

echo -e "${GREEN}2. Audit des interfaces...${NC}"
python3 check_interfaces.py -o reports/audit_interfaces_${TIMESTAMP}.json
echo ""

echo -e "${GREEN}3. Audit des sites...${NC}"
python3 check_sites.py -o reports/audit_sites_${TIMESTAMP}.json
echo ""

echo -e "${GREEN}4. Audit des plateformes...${NC}"
python3 check_platforms.py -o reports/audit_platforms_${TIMESTAMP}.json
echo ""

echo -e "${GREEN}5. Génération du rapport complet...${NC}"
python3 audit_report.py -o reports/audit_full_${TIMESTAMP}.json
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Audits terminés! Rapports disponibles dans:${NC}"
echo -e "${GREEN}  $(pwd)/reports/${NC}"
echo -e "${GREEN}================================================${NC}"
