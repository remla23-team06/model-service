# model-service

## Run the model server
```bash
python3 model_server.py
```

## Test the model server with data
```bash
python3 -c "import requests; r = requests.post('http://localhost:8080/predict', {'data': 42}); print(r.text)"
```