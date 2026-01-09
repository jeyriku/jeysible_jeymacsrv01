Résumé des extraits Infrahub

Fichiers inclus :
- artifact_fetch_module.txt — https://docs.infrahub.app/ansible/references/plugins/artifact_fetch_module
- query_graphql_module.txt — https://docs.infrahub.app/ansible/references/plugins/query_graphql_module
- branch_module.txt — https://docs.infrahub.app/ansible/references/plugins/branch_module
- node_module.txt — https://docs.infrahub.app/ansible/references/plugins/node_module
- inventory_inventory.txt — https://docs.infrahub.app/ansible/references/plugins/inventory_inventory
- lookup_lookup.txt — https://docs.infrahub.app/ansible/references/plugins/lookup_lookup

Usage rapide :
- Ces fichiers contiennent les paramètres, exemples et valeurs de retour des modules Infrahub Ansible.
- Pour exécuter des mutations GraphQL depuis un playbook, utilisez `opsmill.infrahub.query_graphql` (champ `query`).
- Pour créer des nœuds schema (ex. dropdown), essayez `opsmill.infrahub.node` avec `kind: SchemaDropdown` et `data` approprié.

Prochaine étape : j'extrais maintenant les exemples de mutations et je prépare des payloads (dry-run). Si OK, je les génèrerai en YAML Ansible prêt à exécuter.
