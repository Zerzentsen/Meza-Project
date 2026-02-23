# Template de documentation pour les scripts

Chaque script Python dans `scripts/` doit inclure un docstring en en-tête suivant ce format :

```python
"""
Nom du script : nom_du_script.py
Description   : Brève description de ce que fait le script.
Auteur        : Prénom Nom
Date          : YYYY-MM-DD

Dépendances :
    - module_externe (pip install module_externe)

Usage :
    python scripts/nom_du_script.py [--option valeur]

Paramètres :
    --option    Description du paramètre (défaut : valeur_par_defaut)

Exemple :
    python scripts/nom_du_script.py --input data.csv --output result.json
"""
```

## Conventions

- Un script = une responsabilité claire
- Utiliser `argparse` pour les arguments en ligne de commande
- Les fonctions réutilisables doivent être placées dans `libs/`
- Les configurations (URLs, chemins, seuils) vont dans `config/`
- Ne jamais committer de secrets ou credentials
