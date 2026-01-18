# Guide d'utilisation rapide - Audit Infrahub

## 🚀 Démarrage rapide

### 1. Configuration

Créer le fichier `.env` avec vos paramètres :
```bash
cp .env.example .env
nano .env
```

Renseigner :
```
INFRAHUB_API_URL=http://jeysrv10:8080
INFRAHUB_API_TOKEN=votre_token_ici
```

### 2. Installation des dépendances

```bash
pip3 install -r requirements.txt
```

### 3. Exécution

#### Option A : Tous les audits en une fois
```bash
./run_audits.sh
```

#### Option B : Audits individuels

**Audit des devices :**
```bash
python3 check_devices.py
```

**Audit des interfaces :**
```bash
python3 check_interfaces.py
```

**Audit des sites :**
```bash
python3 check_sites.py
```

**Audit des plateformes :**
```bash
python3 check_platforms.py
```

**Rapport complet :**
```bash
python3 audit_report.py
```

### 4. Consulter les résultats

Les rapports JSON sont générés dans `reports/` :
```bash
ls -lh reports/
cat reports/audit_full_*.json | jq .summary
```

## 📊 Ce qui est vérifié

### Devices (InfraDevice)
- ✅ Champs critiques : `name`, `primary_address`
- ⚠️ Champs importants : `site`, `platform`, `role`
- ℹ️ Champs optionnels : `type`, `interfaces`, `description`

### Interfaces (InfraInterface)
- ✅ Champs critiques : `name`, `device`
- ⚠️ Champs importants : `status`, `enabled`
- 🔍 Vérifications : interfaces orphelines, devices sans interfaces

### Sites (InfraSite)
- ✅ Champs critiques : `name`
- ⚠️ Champs importants : `location`
- 🔍 Vérifications : sites référencés mais non définis, devices sans site

### Plateformes (InfraPlatform)
- ✅ Champs critiques : `name`, `ansible_network_os`
- ⚠️ Champs importants : `manufacturer`
- 🔍 Vérifications : cohérence ansible_network_os, devices sans plateforme

## 🎯 Exemple de workflow

```bash
# 1. Exécuter un audit complet
./run_audits.sh

# 2. Vérifier le résumé
python3 audit_report.py | grep -A 20 "RAPPORT D'AUDIT"

# 3. Identifier les problèmes critiques
jq '.devices.critical_issues[] | {device: .object_name, issues: .issues}' reports/audit_full_*.json

# 4. Lister les devices sans plateforme
jq '.platforms.devices_without_platform[]' reports/audit_full_*.json

# 5. Corriger dans Infrahub puis relancer
./run_audits.sh
```

## 🔧 Options avancées

### Mode verbeux
```bash
python3 check_devices.py -v
```

### Sortie personnalisée
```bash
python3 audit_report.py -o /tmp/mon_audit.json
```

### Intégration CI/CD
```bash
# Retourne code 0 si OK, 1 si problèmes, 2 si erreur
python3 audit_report.py
if [ $? -eq 0 ]; then
    echo "✅ Audit OK"
else
    echo "❌ Problèmes détectés"
    exit 1
fi
```

## 📝 Interprétation des résultats

### Sévérités
- **critical** : Bloquant pour l'automation Ansible
- **warning** : À corriger mais non bloquant
- **info** : Information (ex: plateforme sans devices)

### Codes de sortie
- `0` : Aucun problème
- `1` : Problèmes détectés
- `2` : Erreur d'exécution

## 🆘 Dépannage

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "Connection refused"
```bash
# Vérifier que Infrahub est accessible
curl http://jeysrv10:8080/graphql

# Vérifier les variables d'environnement
echo $INFRAHUB_API_URL
```

### "Unauthorized"
```bash
# Vérifier le token dans .env ou :
export INFRAHUB_API_TOKEN="votre_token"
```

## 📚 Plus d'informations

Voir [README.md](README.md) pour la documentation complète.
