# jeysible

Ce dépôt est une collection d'outils et de composants pour l'automatisation d'infrastructures réseau avec Ansible, des scripts Python utilitaires et plusieurs ressources annexes (inventaires, templates, packaging et utilitaires de développement).

**Résumé rapide**
- **But**: Fournir un environnement et des playbooks pour gérer des équipements réseau (Cisco, Juniper, etc.) et intégrer un inventaire dynamique depuis NetBox.
- **Contenu principal**: playbooks Ansible, inventaires statiques et dynamiques (NetBox), rôles, scripts Python, et un sous-projet `pylibssh`.

**Structure importante**
- **Configuration Ansible**: [ansible.cfg](ansible.cfg) — paramètres par défaut, chemin des rôles et interpréteur Python.
- **Inventaires**: [hosts](hosts) (statique) et le répertoire [netbox_dynamic_inventory/](netbox_dynamic_inventory/) pour les sources d'inventaire dynamiques basées sur NetBox.
- **Playbooks**: [playbooks/](playbooks/) (inclut `Dynamic_inventory/`, `Static_inventory/`, et exemples de playbooks par rôle/site/type).
- **Rôles**: [roles/](roles/) (ex. `ansible-pyats` référencé dans `requirements.yml`).
- **Dépendances Ansible Galaxy**: [requirements.yml](requirements.yml) — installer avec `ansible-galaxy install -r requirements.yml`.
- **Scripts et utilitaires Python**: `Python/`, `pylibssh/`, `lib/`, `scripts` et exemples divers.
- **Virtualenv / Binaires**: `bin/` contient un environnement Python local et des exécutables (ex. `activate`).
- **Archives & templates**: `archives/`, `templates/`, `vars/`, `group_vars/`, `host_vars/` pour générer et stocker configurations.

**Usage rapide**
- Activer l'environnement Python fourni (si utilisé) :

```bash
source bin/activate
```

- Installer les rôles requis :

```bash
ansible-galaxy install -r requirements.yml
```

- Lancer des playbooks (exemples listés dans [launch_playbook.txt](launch_playbook.txt)) :

```bash
ansible-playbook -i netbox_dynamic_inventory/inventory_source/netbox_inventory_source_byrole.yml playbooks/playbook_byrole.yml
ansible-playbook -i hosts playbooks/Dynamic_inventory/pb_create_report_v2.yml
```

**Notes techniques**
- `ansible.cfg` référence un interpréteur Python local (`/Users/jeremierouzet/jeysible/bin/python`) et désactive la vérification des clés d'hôte.
- Le projet contient des expérimentations pour l'intégration NetBox (génération d'inventaires dynamiques) et plusieurs playbooks ciblant Cisco et Juniper (pyez, netconf, RESTCONF).
- Un sous-dossier `pylibssh/` contient une bibliothèque liée à `libssh` (bindings / packaging) et des scripts associés.

**Contribuer**
- Ouvrir une issue pour discuter d'un changement majeur.
- Soumettre des Merge Requests propres, documentées et testées.

**Prochaines étapes proposées**
- Committer ce `README.md` localement.
- Convertir et fusionner éventuellement `pylibssh/README.rst` en Markdown si souhaité.
- Ajouter des exemples d'usage concrets (playbook minimal, snippet Python) et des instructions d'installation de NetBox si vous voulez une doc plus complète.

---
Fichier généré automatiquement après analyse rapide de l'arborescence du dépôt. Dites-moi si vous voulez que je crée le commit Git localement ou que j'enrichisse cette documentation avec des exemples précis.
