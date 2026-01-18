# Audit Infrahub

Ce répertoire contient des scripts Python pour auditer l'instance Infrahub (jeysrv10:8080) et identifier les objets manquants ou incomplets.

## Structure

- `check_devices.py` : Vérifie les devices manquants et leurs attributs requis
- `check_interfaces.py` : Vérifie les interfaces manquantes sur les devices
- `check_sites.py` : Vérifie les sites et leur cohérence
- `check_platforms.py` : Vérifie les plateformes et les attributs Ansible
- `audit_report.py` : Génère un rapport d'audit complet
- `config.py` : Configuration centralisée pour les scripts
- `utils.py` : Fonctions utilitaires partagées
- `reports/` : Répertoire pour les rapports générés

## Utilisation

### Configuration

Définir les variables d'environnement :
```bash
export INFRAHUB_API_URL="http://jeysrv10:8080"
export INFRAHUB_API_TOKEN="votre_token"
```

Ou créer un fichier `.env` :
```
INFRAHUB_API_URL=http://jeysrv10:8080
INFRAHUB_API_TOKEN=votre_token
```

### Exécution des audits

```bash
# Audit des devices
python check_devices.py

# Audit des interfaces
python check_interfaces.py

# Audit des sites
python check_sites.py

# Audit des plateformes
python check_platforms.py

# Rapport complet
python audit_report.py --output reports/audit_$(date +%Y%m%d_%H%M%S).json
```

## Attributs vérifiés

### InfraDevice
- `name` : Nom du device (requis)
- `primary_address.address` : Adresse IP primaire (requis)
- `site.name` : Site d'appartenance (requis)
- `role` : Rôle du device (recommandé)
- `type` : Type de device (recommandé)
- `platform.ansible_network_os` : OS réseau Ansible (requis pour automation)
- `interfaces` : Liste des interfaces (recommandé)

### InfraInterface
- `name` : Nom de l'interface (requis)
- `device` : Device parent (requis)
- `status` : Statut de l'interface (recommandé)
- `enabled` : Interface activée ou non (recommandé)
- `ip_addresses` : Adresses IP assignées (optionnel)

### InfraSite
- `name` : Nom du site (requis)
- `location` : Localisation (recommandé)
- `devices` : Liste des devices du site (pour cohérence)

### InfraPlatform
- `name` : Nom de la plateforme (requis)
- `ansible_network_os` : OS pour Ansible (requis)
- `manufacturer` : Fabricant (recommandé)

## Formats de sortie

Les scripts génèrent des rapports en JSON avec la structure suivante :
```json
{
  "timestamp": "2026-01-18T10:30:00",
  "audit_type": "devices",
  "summary": {
    "total": 100,
    "complete": 85,
    "incomplete": 15,
    "missing_critical": 5
  },
  "issues": [
    {
      "object_type": "InfraDevice",
      "object_name": "device-01",
      "severity": "critical",
      "missing_fields": ["primary_address", "platform"],
      "message": "Device sans adresse IP et plateforme"
    }
  ]
}
```

## Dépendances

```bash
pip install requests python-dotenv
```
