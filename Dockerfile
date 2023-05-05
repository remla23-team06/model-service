FROM python:3.10

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY model_server.py /app/

ENTRYPOINT python
CMD ["model_server.py"]

EXPOSE 8080