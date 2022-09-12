import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.arima.model  import ARIMAResults
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import datetime
import requests
import pandas as pd
import json
import os
import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)
import mlflow
from mlflow.tracking import MlflowClient
import yfinance as yf
import os
import requests

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)




def download_ticker(ticker='ETH-USD'):
    
    today = datetime.date.today()
    # datetoday = today.strftime("%B %d, %Y")
    datetoday = today.strftime("%d_%m_%Y")
    if os.path.exists("data/" + ticker+"_"+datetoday+".csv"):
        return

    df = yf.download(ticker)
    df = df.reset_index()
    df['Timestamp'] = df.Date.apply(lambda x: pd.Timestamp(x).timestamp())
    df = df.drop(labels=['Date', 'Adj Close'], axis=1)
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Timestamp'] = df['Timestamp'].apply(lambda x: int(str(x)[:-2] + "000"))
    
    df.to_csv("data/" + ticker+"_"+today.strftime("%d_%m_%Y")+".csv", index=False)

    # Remove historical files
    filelist = [ f for f in os.listdir("data/") if not f.endswith(datetoday+".csv") ]
    for f in filelist:
        os.remove(os.path.join("data/", f))


def get_latest_info():
    model_name = "ARIMA-FORECASTING-MODEL"
    latest_version_info = client.get_latest_versions(model_name, stages=["staging"])
    model_version = latest_version_info[0].version
    logged_model = f'runs:/{latest_version_info[0].run_id}/model'
    return logged_model

def load_model():
    artifact_path = "ARIMA_ETHUSD"
    model_name = "ARIMA-FORECASTING-MODEL"

    print('Before fetching version')

    try:
        print("Page request initiated")
        page = requests.get('http://127.0.0.1:5000')
        print("Request completed!!!!", page.status_code)
    except Exception as e:
        print("Server Not running")
        page = None

    if page and page.status_code == 200:

        # logged_model = f'runs:/{latest_version_info[0].run_id}/model'
        # loaded_model = mlflow.statsmodels.load_model(logged_model)

        logged_model = get_latest_info()

        print(f"Logged Model: {logged_model}")

        # f"models:/{model_name}/{model_version}"

        print('After fetching version')
        loaded_model = mlflow.statsmodels.load_model(logged_model)
        print('end of model')

    else:

        loaded_model = ARIMAResults.load('model/model.pkl')

    return loaded_model

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

def prediction(timestamps = 1):
    model = load_model()
    return list(model.forecast(timestamps))

app = Flask('crypto-prediction')

@app.route('/')
def landing_page():
    download_ticker()
    return render_template('index.html', datelist="", show_results="false")

@app.route('/pipe', methods=["GET", "POST"])
def pipe():

    latest_file = newest(r"data")
    print(f"Newest file: {latest_file}")
    df = pd.read_csv(latest_file)
    df = list(map(list, df.itertuples(index=False)))
    return {"res":df}


@app.route('/predict', methods=['POST', 'GET'])
def predict_endpoint():
    
    timestamp = request.form['timestamp']   
    print(timestamp)
    pred = prediction(timestamps = int(timestamp))

    latest_file = newest(r"data")
    
    day = int(latest_file.split("_")[1])
    month = int(latest_file.split("_")[2])
    year = int(latest_file.split("_")[3].split(".")[0])

    current = datetime.datetime(year, month, day)

    datelist = []

    print(f"Predictions are: {pred}")

    for i in range(1, int(timestamp)+1):
        datelist.append([pred[i-1], (current+timedelta(days=i)).date()])

    if timestamp:
        return render_template('index.html', datelist = datelist, show_results="true")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
