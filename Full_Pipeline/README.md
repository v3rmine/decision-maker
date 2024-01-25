
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


> Set your `OPENAPI_KEY` environment variable if used with ChatGPT 

Launch the main script:

```bash
poetry run python main.py
```

Launch the action server:
```bash
poetry run flask --app action_server run
```
