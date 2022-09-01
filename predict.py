import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.arima_model import ARIMAResults
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



# import plotly.graph_objects as go
# import pandas as pd

# fig = go.Figure(data = )

def load_model():
    model = ARIMAResults.load('model/model.pkl')
    return model

def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

def prediction(timestamps = 1):
    model = load_model()
    return list(model.forecast(timestamps)[0])

app = Flask('crypto-prediction')

@app.route('/')
def landing_page():
    return render_template('index.html', datelist="", show_results="false")

@app.route('/pipe', methods=["GET", "POST"])
def pipe():

    latest_file = newest(r"data")
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

    for i in range(1, int(timestamp)+1):
        datelist.append([pred[i-1], (current+timedelta(days=i)).date()])


    if timestamp:
        return render_template('index.html', datelist = datelist, show_results="true")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
