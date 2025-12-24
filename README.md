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

**Infrahub Ansible Modules**
- **Docs officielles**: références des plugins Ansible fournis par Infrahub — utile pour créer playbooks ciblant une instance Infrahub:
	- artifact_fetch_module: https://docs.infrahub.app/ansible/references/plugins/artifact_fetch_module
	- query_graphql_module: https://docs.infrahub.app/ansible/references/plugins/query_graphql_module
	- branch_module: https://docs.infrahub.app/ansible/references/plugins/branch_module
	- node_module: https://docs.infrahub.app/ansible/references/plugins/node_module
	- inventory_inventory: https://docs.infrahub.app/ansible/references/plugins/inventory_inventory
	- lookup_lookup: https://docs.infrahub.app/ansible/references/plugins/lookup_lookup
	- roles/install: https://docs.infrahub.app/ansible/references/roles/install

- **Résumé & bonnes pratiques**:
	- Utilisez `infrahub.query_graphql` pour interroger directement l'API GraphQL d'Infrahub et récupérer des nœuds, inventaires ou effectuer des mutations quand l'API REST n'existe pas.
	- Préférez l'envoi de payloads JSON via fichiers (`--data-binary` dans les tests curl) pour éviter les problèmes de quoting lors de génération dynamique.
	- Ajoutez des timeouts et des retries (dans vos tâches Ansible ou scripts appelés) lorsque vous effectuez des opérations en masse (création/upsert de profiles, attachments, etc.).

- **Exemples rapides**:

	- Requête GraphQL simple avec le module `query_graphql` (extrait):

```yaml
- name: Interroger Infrahub - devices
	hosts: localhost
	tasks:
		- name: Query GraphQL devices
			infrahub.query_graphql:
				url: "http://jeysrv10:8000/graphql"
				headers:
					X-INFRAHUB-KEY: "{{ lookup('env','INFRAHUB_TOKEN') }}"
					Authorization: "Bearer {{ lookup('env','INFRAHUB_TOKEN') }}"
				query: |
					query ($limit:Int){
						devices(limit:$limit){
							id
							name
						}
					}
				variables:
					limit: 50
			register: ghql

		- debug: var=ghql
```

	- Récupération d'un artefact et extraction via `artifact_fetch` (extrait):

```yaml
- name: Télécharger un artefact depuis Infrahub
	hosts: localhost
	tasks:
		- name: Fetch artifact
			infrahub.artifact_fetch:
				url: "http://jeysrv10:8000"
				artifact: "configs/device-template.tar.gz"
				dest: "/tmp/device-template.tar.gz"
			register: af

		- name: Debug artifact result
			debug: var=af
```

Pour des usages plus avancés (branch/node management, inventaires dynamiques, lookup personnalisé), consultez les pages liées ci-dessus et adaptez les exemples selon votre endpoint et le token d'authentification.


**Entrées présentes sur `origin/main`**
Après vérification du remote `origin/main`, les entrées de premier niveau présentes sont :

- .gitignore
- Icon
- ansible.cfg
- archives/
- config/
- Dojo/
- host_vars/
- hosts
- Json/
- launch_inventory.txt
- launch_playbook.txt
- netbox_dynamic_inventory/
- playbooks/
- Python/
- pyvenv.cfg
- README.md
- requirements.yml
- roles/
- templates/
- vars/

Si vous souhaitez que j'ajoute la liste complète (récursive) pour un dossier précis, dites lequel.
