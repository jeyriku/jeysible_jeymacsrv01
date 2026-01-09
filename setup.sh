#!/usr/bin/env bash
# setup.sh - Configuration initiale de l'environnement jeysible
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
PYTHON_VERSION="python3"

echo "🚀 Configuration de l'environnement jeysible..."
echo "📁 Répertoire du projet: ${PROJECT_ROOT}"

# Vérifier la présence de Python
if ! command -v ${PYTHON_VERSION} &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "${VENV_DIR}" ]; then
    echo "📦 Création de l'environnement virtuel..."
    ${PYTHON_VERSION} -m venv "${VENV_DIR}"
else
    echo "✅ Environnement virtuel déjà existant"
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source "${VENV_DIR}/bin/activate"

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip setuptools wheel

# Installer les dépendances
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo "📦 Installation des dépendances Python..."
    pip install -r "${PROJECT_ROOT}/requirements.txt"
else
    echo "⚠️  Aucun fichier requirements.txt trouvé"
fi

# Installer les rôles Ansible
if [ -f "${PROJECT_ROOT}/requirements.yml" ]; then
    echo "📦 Installation des rôles Ansible..."
    ansible-galaxy install -r "${PROJECT_ROOT}/requirements.yml"
else
    echo "⚠️  Aucun fichier requirements.yml trouvé"
fi

# Vérifier les variables d'environnement nécessaires
echo ""
echo "🔐 Vérification des variables d'environnement..."
MISSING_VARS=()

if [ -z "${INFRAHUB_TOKEN:-}" ]; then
    MISSING_VARS+=("INFRAHUB_TOKEN")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Variables d'environnement manquantes:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - ${var}"
    done
    echo ""
    echo "💡 Ajoutez ces variables à votre ~/.bashrc, ~/.zshrc ou ~/.profile:"
    echo "   export INFRAHUB_TOKEN='votre-token-ici'"
fi

# Vérifier le fichier vault password
VAULT_PASS_FILE="${HOME}/.ansible_vault_pass_jeysible"
if [ ! -f "${VAULT_PASS_FILE}" ]; then
    echo ""
    echo "⚠️  Fichier vault password non trouvé: ${VAULT_PASS_FILE}"
    echo "💡 Créez ce fichier avec votre mot de passe vault:"
    echo "   echo 'votre-mot-de-passe' > ${VAULT_PASS_FILE}"
    echo "   chmod 600 ${VAULT_PASS_FILE}"
fi

# Rendre les scripts exécutables
echo ""
echo "🔧 Configuration des permissions des scripts..."
chmod +x "${PROJECT_ROOT}/scripts/"*.{expect,exp,sh} 2>/dev/null || true

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Configurez vos variables d'environnement (INFRAHUB_TOKEN)"
echo "   2. Configurez votre mot de passe vault si nécessaire"
echo "   3. Activez l'environnement: source venv/bin/activate"
echo "   4. Testez avec: ansible-playbook --version"
echo ""
