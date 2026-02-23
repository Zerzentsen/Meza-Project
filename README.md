# Meza-Project

Espace de travail pour les automatisations et scripts Python du groupe GIM.

## Structure du projet

```
Meza-Project/
├── scripts/          # Scripts d'automatisation Python
├── libs/             # Modules partagés et utilitaires communs
├── config/           # Fichiers de configuration (templates uniquement, pas de secrets)
├── docs/             # Documentation complémentaire
├── requirements.txt  # Dépendances Python du projet
└── CONTRIBUTING.md   # Guide de contribution
```

## Prérequis

- Python 3.9+
- pip

## Installation

```bash
# Cloner le repo
git clone <url-du-repo>
cd Meza-Project

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

Chaque script dans `scripts/` est documenté avec un en-tête décrivant son objectif, ses paramètres et un exemple d'utilisation. Consulter `docs/TEMPLATE_SCRIPT.md` pour le format attendu.

## Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les conventions et le processus de contribution.
