# Crypto Prediction Application- End-to-end project 
Cryptocurrency price prediction application via statistics, machine learning with deployment, experiment tracking & model registry.

Index
- [Problem Description](#problem-description)
- [Instruction to Run Code](#instructions-to-run-the-code)
    1. [Running via script](#running-on-the-cloud-or-locally)
    2. [Running as a containerized service](#running-as-a-containerized-service)
- Some points on development

## Problem Description

- To predict cryptocurrency daily ***closing*** prices using statistical time series models (ARIMA at present). 
- ARIMA Model deployed as a **Web Service** with front end served with Flask & gunicorn.
- UI to have an thorough & inteactive crypto historic chart, option to select number of days to predict with submit button that displayes result in bootstrap table.
- Experiment to be tracked & models with lowest MAPE value to be registered automatically to **Staging** in MLFlow server.
- Containerize the entire flow with docker & serve MLFlow server with Flask gunicorn server from same container.
- Model Training & Serving must be independent of MLFlow server & should be able to train & predict without it running.

## Instructions to run the code
### Running on the cloud or locally

1. Clone the repository in a provisioned VM Instance or locally:

    `git clone https://github.com/varunkuntal/Crypto-prediction.git`
    
2. Create a virtual environment (using Anaconda) with python 3.7 & install dependencies in requirements.txt, run commnd in terminal:

    `pip install -r requirements.txt`

3. To run the Flask gunicorn server, run commnd in terminal:

    `gunicorn --bind=0.0.0.0:9696 predict:app`

    Model will be served on `http://localhost:9696` or `http://127.0.0.1:9696`.

4a. To train, track & resgiter models using MLFlow server, run commnd in terminal:

    mlflow server --host=0.0.0.0 --port=5000 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=file:mlruns
    
    MLFlow server is served at 
    
    http://127.0.0.1:5000
    
    Now we can train the ARIMA model using following command in terminal:
    
    python model_training.py
    

4b. Alternatively, train the model without tracking server by directly running:

    `python model_training.py`
    
    
### Running as a containerized service

1. Build the image using docker, run command in terminal from root folder of project:

    `docker build -t crypto-prediction-app:v1 .`
  
2. Run the container image with 2 services using:

    `docker run -it -p 5000:5000 -p 9696:9696  crypto-prediction-app:v1`


**Model with UI** is served at `http://127.0.0.1:9696` & the **tracking & registry server** is served at `http://127.0.0.1:5000`.


### Some points on the development:

- Final project for #mlopszoomcamp by [DataTalks club](https://datatalks.club)
- Currently default Ethereum ticker is used for forecasting.
- Graphs are served with Highcharts.js library with all dependencies included.
- Model registry maintained with MLFlow 1.28.0
- Trading cryptocurrencies involve high risks, forecasts provided are strictly for demonstration purposes.
