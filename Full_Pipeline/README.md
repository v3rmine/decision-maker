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
> Set your `OPENAPI_KEY` environment variable if used with ChatGPT 

Launch the main script:

```bash
poetry run python main.py
```

Launch the action server:
```bash
poetry run flask --app action_server run
```
