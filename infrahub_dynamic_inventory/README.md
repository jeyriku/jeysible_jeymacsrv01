# infrahub_dynamic_inventory

Arborescence dédiée à l'intégration d'une instance Infrahub (serveur `jeysrv10`) comme source d'inventaire dynamique pour Ansible.

Structure
- `inventory_source/` : modèles et sources d'inventaire (fichiers YAML à adapter).
- `inventory_output/` : emplacement prévu pour les sorties/rapports générés par les scripts (ex: JSON/YAML).
- `inventory_report/` : rapports consolidés (ex: playbooks qui écrivent des rapports ici).

Utilisation
- Copiez/adaptez les fichiers de `inventory_source/` pour appeler votre API Infrahub ou un script local qui exporte l'inventaire au format attendu par Ansible.
- Les fichiers fournis sont des templates avec des placeholders : remplacez `INFRAHUB_API_URL` et `INFRAHUB_TOKEN` par vos valeurs ou implémentez un script d'extraction.

Sécurité
- Ne vérifiez jamais en clair les tokens API dans le dépôt public. Utilisez des variables d'environnement, Ansible Vault, ou un fichier non versionné pour stocker les secrets.
