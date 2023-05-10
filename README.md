# model-service

## Install Poetry (for Python package management)
See this [link](https://python-poetry.org/docs/#installation) for how to install poetry for your platform.

## Install requirements
```bash
# in the root directory of the repo
poetry update
```

## Run the model server
```bash
poetry run flask --port 8000 --host 0.0.0.0
```

## Test the model server with data
```bash
poetry run python -c \
 "import requests;  r = requests.post('http://localhost:8080/predict', {'data': 'I was disgusted because I was pretty sure that was human hair.'}); print(r.text)"
```