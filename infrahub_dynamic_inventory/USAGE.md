# Utilisation rapide d'Infrahub Dynamic Inventory

1. Installer la collection Infrahub (déjà fournie dans ce dépôt si vous l'avez installé) :

```bash
ansible-galaxy collection install opsmill.infrahub
```

2. Préparer la variable d'environnement contenant le token (ne pas committer en clair) :

```bash
export INFRAHUB_API_TOKEN="<votre_token>"
```

3. Tester l'inventaire :

```bash
ansible-inventory -i infrahub_dynamic_inventory/inventory_source/infrahub_inventory_example.yml --list
```

4. Générer et appliquer la configuration (exemple) :

```bash
ansible-playbook -i infrahub_dynamic_inventory/inventory_source/infrahub_inventory_example.yml playbooks/infrahub_configure.yml
```

Remarques
- Les modules `ios_config` et `junos_config` sont fournis par les collections `cisco.ios` et `junipernetworks.junos` respectivement ; installez-les si nécessaire.
- Les credentials (utilisateur/mot de passe/clé) ne doivent pas être stockés en clair dans Infrahub ; utilisez Ansible Vault ou des variables d'environnement.
