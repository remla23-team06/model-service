# model-service

After cloning the repository, please follow the instructions below to run the `model-service`:

## Running locally
### Install Poetry (for Python package management)
See this [link](https://python-poetry.org/docs/#installation) for how to install poetry for your platform.

### Install requirements
```bash
# in the root directory of the repo
poetry lock
poetry update
```

### Run the model-service server
In Bash:
```sh
poetry run flask --app model_service --port 8000 --host 0.0.0.0
```

In Powershell:
```powershell
poetry run flask --app model_service --port 8000 --host 0.0.0.0
```

## Running in Docker
Firstly, build the Docker image locally.
```docker
docker build . -t model-service-local
```
Secondly, run the docker image
```docker
docker run --rm model-service-local
```
