# model-service

## Install requirements
```bash
python3 -m pip install -r requirements.txt
```

## Run the model server
```bash
python3 model_server.py
```

## Test the model server with data
```bash
python3 -c "import requests; r = requests.post('http://localhost:8080/predict', {'data': 'I was disgusted because I was pretty sure that was human hair.'}); print(r.text)"
```