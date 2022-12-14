import numpy as np
import yfinance as yf
import pandas as pd
from datetime import date
import requests

from itertools import product
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import train_test_split
import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
EXPERIMENT_NAME = f"arima-ethusdt"

# Check if MLFlow server running on localhost:5000 
try:
    page = requests.get('http://127.0.0.1:5000')
    print("MLFlow server response: ", page.status_code)
except Exception as e:
    print("MLFlow Not running")
    page = None

if page and page.status_code == 200:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    mlflow.statsmodels.autolog(log_models=True)


def read_data(ticker='ETH-USD'):
    # Download cryptocurrency data (2017 - 2022)

    today = date.today()
    datetoday = today.strftime("%B %d, %Y")
    print(f"\nDownloading the dataset for {ticker} on {datetoday} ...\n\n")
    df = yf.download(ticker)
    #Process dataframe for Highcharts graph to display properly
    df = df.reset_index()
    df['Timestamp'] = df.Date.apply(lambda x: pd.Timestamp(x).timestamp())
    df = df.drop(labels=['Date', 'Adj Close'], axis=1)
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Timestamp'] = df['Timestamp'].apply(lambda x: int(str(x)[:-2] + "000"))
    
    df.to_csv("data/" + ticker+"_"+today.strftime("%d_%m_%Y")+".csv", index=False)

    # Train-Test Split
    training_data, testing_data = train_test_split(df, test_size=0.1, shuffle=False)
    training_data, testing_data = list(training_data['Close']), list(testing_data['Close'])
    return df, training_data, testing_data


def mape(model_predictions, testing_data):
    # Mean Absolute Percentage Error for time series
    return np.mean(np.abs(np.array(model_predictions) - np.array(testing_data)) / np.abs(testing_data))


def train_model_search():
    df, training_data, testing_data = read_data()
    
    # Using GRID Search for (p,d,q) instead of Randomized Hyperopt as number of prameters are lesser
    ps = range(2, 4)
    qs = range(0, 1)
    d=1
    parameters = product(ps, qs)
    parameters_list = list(parameters)

    for param in parameters_list:
        model_predictions = []
        with mlflow.start_run(run_name='arima_param'):
            mlflow.set_tag("model", "ARIMA")
            print(f"p & q values are: {param[0]}, {param[1]}")
            mlflow.log_param('param-ps', param[0])
            mlflow.log_param('param-qs', param[1])
            n_test_obs = len(testing_data)

            try:
                for i in range(n_test_obs):
                    model = ARIMA(endog=training_data, order = (param[0], d, param[1]))
                    model_fit = model.fit()
                    output = model_fit.forecast()
                    yhat = output[0]
                    model_predictions.append(yhat)
                    actual_test_value = testing_data[i]
                    # Rolling prediction one day ahead and appending result to training + reiterate
                    training_data.append(actual_test_value)

                print(f"Model Predictions, Testing Data = {len(model_predictions)}, {len(testing_data)}")
                mape_val = mape(model_predictions, testing_data)

                model_fit.save('model/model.pkl')

                mlflow.log_metric("mape", mape_val)
                
            except Exception as e:
                print(f"Error: {e}")
                mlflow.log_metric("AIC", float('inf'))
                mlflow.log_metric("BIC", float('inf'))
                mlflow.log_metric("mape", float('inf'))

    return 


def register_model():
    # Regsiter best model and promote to Staging via MLFlow API

    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.mape ASC"]
    )

    if runs:
        for run in runs:
            print(f"run id: {run.info.run_id}, mape: {run.data.metrics['mape']:.4f}")

            artifact_path = "ARIMA_ETHUSD"
            model_name = "ARIMA-FORECASTING-MODEL"

            model_uri = f'runs:/{run.info.run_id}/{artifact_path}'

            model_details = mlflow.register_model(model_uri=model_uri, name=model_name)

            client.transition_model_version_stage(
            name=model_details.name,
            version=model_details.version,
            stage='staging',
            )

            model_version_details = client.get_model_version(
            name=model_details.name,
            version=model_details.version,
            )

            latest_version_info = client.get_latest_versions(model_name, stages=["staging"])
            latest_production_version = latest_version_info[0].version
            print("The latest production version of the model '%s' is '%s'." % (model_name, latest_production_version))

    else:
        print(f"No runs found in the experiment {EXPERIMENT_NAME}")
        
    return
    

def train():
    model_predictions = []
    
    df, training_data, testing_data = read_data()
    n_test_obs = len(testing_data)

    print("\nModel tracking not running! Training the model & saving in ./model...\n")
    for i in range(n_test_obs):
        model = ARIMA(training_data, order = (4,1,0))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        model_predictions.append(yhat)
        actual_test_value = testing_data[i]
        # Rolling Training by predicting one day ahead and appending to 
        training_data.append(actual_test_value)

    mape_val = mape(model_predictions, testing_data)

    return model_fit, mape_val

def main():
    if page and page.status_code == 200:
        print("Training & registering best model to staging...")
        train_model_search()
        register_model()
        print("Done")
    else:
        model, mape_val = train()
        print(f"MAPE = {mape_val}\nSaving the model now...")
        model.save('model/model.pkl')
        print("Done.")
        return mape_val

if __name__ == '__main__':
    main()





