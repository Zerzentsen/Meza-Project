# Guide de contribution

## Ajouter un nouveau script

1. Créer le fichier dans `scripts/` avec un nom descriptif en snake_case (ex: `export_users.py`)
2. Inclure le docstring d'en-tête tel que décrit dans `docs/TEMPLATE_SCRIPT.md`
3. Ajouter les dépendances éventuelles dans `requirements.txt`
4. Tester le script localement avant de committer

## Structure du code

- **`scripts/`** — Scripts autonomes exécutables directement
- **`libs/`** — Modules partagés importables par les scripts
- **`config/`** — Fichiers de configuration (templates uniquement)
- **`docs/`** — Documentation complémentaire

## Conventions

### Nommage
- Fichiers : `snake_case.py`
- Fonctions et variables : `snake_case`
- Classes : `PascalCase`
- Constantes : `UPPER_SNAKE_CASE`

### Code
- Suivre PEP 8
- Utiliser `argparse` pour les paramètres en ligne de commande
- Gérer les erreurs avec des messages explicites
- Ne jamais hardcoder de secrets ou chemins absolus spécifiques à une machine

### Git
- Messages de commit clairs et en français ou anglais (rester cohérent)
- Une fonctionnalité ou correction par commit
- Créer une branche pour les changements importants

## Secrets et configuration

- Ne jamais committer de fichiers `.env`, clés API, ou credentials
- Utiliser des variables d'environnement ou des fichiers `.env` (listés dans `.gitignore`)
- Placer des templates de configuration dans `config/` (ex: `config/example.env`)
