# Full pipeline

## Prérequis
- python 3.11
  - poetry (`pip install poetry`)

## Mise en place
> Create env
> > On Windows / Linux / OSX
> > ```bash
> > poetry env use 3.11
> > ```

> Install dependencies
> > On Windows / Linux / OSX
> > ```bash
> > poetry install
> > ```

## Éxecution
1. Set your `OPENAPI_KEY` environment variable if used with ChatGPT 
2. Launch the action server:
```bash
poetry run flask --app action_server run
```
3. Launch the main script:
```bash
poetry run python main.py
```