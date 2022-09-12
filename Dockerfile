FROM python:3.7-slim

RUN pip install -U pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]

CMD ["mlflow server", "--host=0.0.0.0", "--port=5000", "--backend-store-uri=sqlite:///mlflow.db", "--default-artifact-root=file:mlruns"]