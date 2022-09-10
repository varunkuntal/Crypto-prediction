# Crypto Prediction Application- End-to-end project with deployment
Cryptocurrency price prediction application via statistics, machine learning.

Front-end served with Flask + gunicorn.
Graphs are served with Highcharts.js library with all dependencies included.

Model registry maintained with MLFlow 1.28.0

Trading cryptocurrencies involve risks, forecasts provided are strictly for demonstration purposes.

To run the setup, follow steps below:

1. Create a virtual environment with python 3.7 & install dependencies in requirements.txt 

`pip install -r requirements.txt`


2. To run the gunicorn server, run the Flask instance in predict.py

`gunicorn --bind=0.0.0.0:9696 predict:app`

Model will be served on localhost:9696 or http://127.0.0.1:9696

Predict timestamps in future by selecting number of days to forecast & submit using the button.


3. [Optional] To train with latest data from Yahoo finance, first start Mlflow server

`mlflow server --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=file:mlruns --host 0.0.0.0 --port 5000`

Then train the time series model using:

`python model_training.py`

Latest model will be loaded & ready to predict at the ui.
