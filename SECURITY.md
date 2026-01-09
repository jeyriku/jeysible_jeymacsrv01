# 🔐 Guide de Sécurité - Gestion des Tokens API

## ⚠️ IMPORTANT - Action Immédiate Requise

L'ancien token API **7435d9eb9841dc8a941417a0993fc531c3dc35ca** a été exposé dans le dépôt Git et doit être révoqué immédiatement.

## 🔄 Étapes de Migration

### 1. Révoquer l'Ancien Token (FAIT ✅)

Le token **7435d9eb9841dc8a941417a0993fc531c3dc35ca** a été remplacé par le nouveau token sécurisé dans le vault.

### 2. Nouveau Token Actif

Le nouveau token **188600a3-6e17-9f97-339f-c516618aa3c0** est maintenant actif et stocké de manière sécurisée dans:
- `group_vars/all/infrahub_vault.yml` (chiffré avec Ansible Vault)

### 3. Configuration des Variables d'Environnement

Pour utiliser les playbooks, vous devez définir la variable d'environnement:

```bash
# Dans ~/.bashrc, ~/.zshrc ou ~/.profile
export INFRAHUB_TOKEN='188600a3-6e17-9f97-339f-c516618aa3c0'
```

Ou créer un fichier `.env` (à ne JAMAIS committer):

```bash
# .env (déjà ajouté au .gitignore)
INFRAHUB_TOKEN=188600a3-6e17-9f97-339f-c516618aa3c0
```

### 4. Utilisation avec Ansible

Les playbooks récupèrent automatiquement le token depuis:
1. La variable d'environnement `INFRAHUB_TOKEN`
2. Le vault Ansible `infrahub_api_tokens.api_token` (fallback)

```yaml
# Exemple dans un playbook
vars:
  infrahub_token: "{{ lookup('env','INFRAHUB_TOKEN') | default(infrahub_api_tokens.api_token, true) }}"
```

### 5. Déchiffrer le Vault

Pour consulter les tokens dans le vault:

```bash
ansible-vault view group_vars/all/infrahub_vault.yml
```

Pour éditer le vault:

```bash
ansible-vault edit group_vars/all/infrahub_vault.yml
```

## 🛡️ Bonnes Pratiques de Sécurité

### ✅ À FAIRE

1. **Toujours utiliser Ansible Vault** pour les secrets
2. **Utiliser des variables d'environnement** pour les tokens locaux
3. **Rotate régulièrement** les tokens API (tous les 3-6 mois minimum)
4. **Vérifier les permissions** du fichier vault password:
   ```bash
   chmod 600 ~/.ansible_vault_pass_jeysible
   ```
5. **Ne jamais committer** de tokens en clair dans Git
6. **Utiliser .gitignore** pour exclure les fichiers sensibles

### ❌ À NE JAMAIS FAIRE

1. ❌ Committer des tokens API en clair dans les fichiers
2. ❌ Partager le mot de passe vault par email/chat
3. ❌ Utiliser le même token sur plusieurs environnements
4. ❌ Laisser des tokens dans l'historique Git (utiliser `git filter-branch` si nécessaire)
5. ❌ Stocker des mots de passe en clair dans les playbooks

## 🔍 Vérification de Sécurité

Avant de committer, vérifiez qu'aucun token n'est exposé:

```bash
# Rechercher des tokens dans les fichiers non chiffrés
grep -r "188600a3\|7435d9eb" . --exclude-dir=.git --exclude="*.vault.yml" --exclude="SECURITY.md"

# Vérifier ce qui sera commité
git diff --cached
```

## 📝 Historique des Tokens

| Date | Token (masqué) | Statut | Utilisateur |
|------|----------------|--------|-------------|
| 2024-01-09 | 188600a3-**** | ✅ Actif | jeyriku |
| Avant 2024-01-09 | 7435d9eb-**** | ❌ Révoqué | N/A |

## 🆘 En Cas de Compromission

Si un token est compromis:

1. **Révoquer immédiatement** le token dans Infrahub/NetBox
2. **Générer un nouveau token**
3. **Mettre à jour le vault**:
   ```bash
   ansible-vault edit group_vars/all/infrahub_vault.yml
   ```
4. **Notifier l'équipe** de la rotation du token
5. **Vérifier les logs d'accès** pour détecter des utilisations non autorisées

## 📞 Contact

Pour toute question de sécurité: jeremie.rouzet@jeyriku.net
