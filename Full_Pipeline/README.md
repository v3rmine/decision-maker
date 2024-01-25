# Full pipeline

## Prérequis
- python 3.11
  - poetry (`pip install poetry`)

## Mise en place
**Creation de l'env**
```bash
poetry env use 3.11
```

**Installation des dépendances**
```bash
poetry install
```

## Éxecution
1. Assigner la variable d'env `OPENAPI_KEY` à une clef API OpenAI 
2. Lancer le serveur d'action (simulateur du robot)
```bash
poetry run flask --app action_server run
```
3. Lancer le script principal
```bash
# Entrée de la phrase par le clavier (texte)
poetry run python3 main.py
# Entrée de la phrase via le micro
poetry run python3 main.py --record
```