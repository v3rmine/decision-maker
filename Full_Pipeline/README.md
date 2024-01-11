
> **For both:** activate venv
> > On Windows
> > ```bash
> > .\venv\Scripts\Activate
> > ```
> 
> > On Linux
> > ```bash
> > source venv/bin/activate
> > ```

> Set your `OPENAPI_KEY` environment variable if used with ChatGPT 

Launch the main script:

```bash
python main.py
```

Launch the action server:
```bash
flask --app action_server run
```