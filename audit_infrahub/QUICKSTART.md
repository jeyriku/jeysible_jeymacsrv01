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
INFRAHUB_API_URL=http://jeysrv10:8000
INFRAHUB_API_TOKEN=votre_token_ici
```

### 2. Installation des dépendances

```bash
pip3 install -r requirements.txt
```

### 3. Exécution

#### Audit complet (recommandé)
```bash
python3 audit.py
```

Cela exécute tous les audits en une seule commande :
- ✅ Audit des devices
- ✅ Audit des rôles
- ✅ Audit des plateformes  
- ✅ Tableau résumé

#### Audits spécifiques

**Audit des devices uniquement :**
```bash
python3 audit.py --devices
```

**Audit des rôles uniquement :**
```bash
python3 audit.py --roles
```

**Audit des plateformes uniquement :**
```bash
python3 audit.py --platforms
```

**Tableau résumé uniquement :**
```bash
python3 audit.py --summary
```

**Export avec nom personnalisé :**
```bash
python3 audit.py -o mon_audit_custom.json
```


### 4. Consulter les résultats

Les rapports JSON sont automatiquement sauvegardés dans `reports/` :
```bash
ls -lh reports/
cat reports/audit_*.json | jq .
```

## 📊 Ce qui est vérifié

### Devices (JeylanDevice)
- ✅ Champs vérifiés : `name`, `mgmt_ip`, `status`
- ⚠️ Champs importants : `platform`, `role`
- ℹ️ Compteur d'interfaces

### Rôles (JeylanDeviceRole)
- Liste de tous les rôles
- Distribution des devices par rôle
- Statistiques d'utilisation

### Plateformes (JeylanPlatform)
- Liste des plateformes (iOS, JunOS, etc.)
- Distribution des devices par plateforme
- Devices sans plateforme définie

## 🎯 Exemple de workflow

```bash
# 1. Exécuter un audit complet
python3 audit.py

# 2. Consulter un rapport spécifique
cat reports/audit_*.json | jq '.summary'

# 3. Identifier les devices sans plateforme
python3 audit.py --platforms | grep "sans plateforme"

# 4. Corriger dans Infrahub puis relancer
python3 audit.py
```

## 🔧 Options du script

```bash
python3 audit.py [OPTIONS]

Options:
  --devices     Audit des devices uniquement
  --roles       Audit des rôles uniquement
  --platforms   Audit des plateformes uniquement
  --summary     Tableau résumé uniquement
  -o FILE       Nom du fichier de sortie JSON
```

Sans option, le script exécute tous les audits.

## 📝 Interprétation des résultats

### Statistiques affichées
- **Total** : Nombre total de devices
- **Sans IP management** : Devices sans adresse IP
- **Sans rôle** : Devices sans rôle défini
- **Sans plateforme** : Devices sans plateforme
- **Status non-actif** : Devices offline/disabled

### Format de sortie console
```
📱 AUDIT DES DEVICES
✅ 46 devices trouvés
📊 Statistiques...
⚠️ X devices avec problèmes
```

## 🆘 Dépannage

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "Connection refused"
```bash
# Vérifier que Infrahub est accessible
curl http://jeysrv10:8000/graphql

# Vérifier les variables d'environnement
cat .env
```
echo $INFRAHUB_API_URL


### "Unauthorized" ou "403"
```bash
# Vérifier le token dans .env
cat .env | grep TOKEN

# Ou définir directement :
export INFRAHUB_API_TOKEN="votre_token"
```

### Port incorrect
Le port par défaut est **8000** (pas 8080). Vérifier `.env` :
```
INFRAHUB_API_URL=http://jeysrv10:8000
```

## 📚 Plus d'informations

Voir [README.md](README.md) pour la documentation complète.
