FROM python:3.7-slim

RUN pip install -U pip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ./services.sh
