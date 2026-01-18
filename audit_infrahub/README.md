# Audit Infrahub

Ce répertoire contient un script Python unifié pour auditer l'instance Infrahub (jeysrv10:8000) et identifier les objets manquants ou incomplets.

## Structure

- `audit.py` : Script unifié d'audit Infrahub (devices, rôles, plateformes)
- `config.py` : Configuration centralisée
- `utils.py` : Fonctions utilitaires partagées
- `reports/` : Répertoire pour les rapports JSON générés
- `.env` : Configuration de l'API Infrahub

## Utilisation

### Configuration

Créer un fichier `.env` à partir du modèle :
```bash
cp .env.example .env
nano .env
```

Renseigner :
```
INFRAHUB_API_URL=http://jeysrv10:8000
INFRAHUB_API_TOKEN=votre_token
```

### Installation des dépendances

```bash
pip3 install -r requirements.txt
```

### Exécution des audits

```bash
# Audit complet (devices, rôles, plateformes, résumé)
python3 audit.py

# Audits spécifiques
python3 audit.py --devices      # Uniquement les devices
python3 audit.py --roles        # Uniquement les rôles
python3 audit.py --platforms    # Uniquement les plateformes
python3 audit.py --summary      # Tableau résumé

# Export personnalisé
python3 audit.py -o mon_audit.json
```

## Résultats de l'audit

Le script génère automatiquement :
- **Affichage console** : Résumé formaté avec statistiques et problèmes détectés
- **Rapport JSON** : Fichier détaillé sauvegardé dans `reports/audit_YYYYMMDD_HHMMSS.json`

### Informations auditées

**Devices :**
- Nom, adresse IP management, statut
- Rôle et plateforme
- Nombre d'interfaces
- Problèmes : devices sans IP, rôle, plateforme ou status offline

**Rôles :**
- Liste des rôles existants
- Distribution des devices par rôle

**Plateformes :**
- Liste des plateformes existantes (iOS, JunOS, etc.)
- Distribution des devices par plateforme
- Devices sans plateforme définie

### Exemple de sortie

```
📱 AUDIT DES DEVICES
✅ 46 devices trouvés
📊 Statistiques:
  Total: 46
  Sans IP management: 0
  Sans plateforme: 35
  Status non-actif: 7
⚠️ 36 devices avec problèmes
```

## Format du rapport JSON

```json
{
  "timestamp": "2026-01-18T18:14:14",
  "devices": {...},
  "roles": {...},
  "platforms": {...},
  "summary": {...}
}
```

## Dépendances

```bash
pip install requests python-dotenv
```
