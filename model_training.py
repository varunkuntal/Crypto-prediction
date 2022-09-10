import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima.model', FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima.model', FutureWarning)

import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import pandas as pd
from datetime import date

from itertools import product
import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
import mlflow.pyfunc

from google.cloud import storage

MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
EXPERIMENT_NAME = f"arima-ethusdt_{date.today().strftime('%d_%m_%Y')}"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

mlflow.statsmodels.autolog(log_models=True)

# def upload_blob(bucket_name="zc-bucket", source_file_name="model.pkl", destination_blob_name="mlruns"):
#     """Uploads a file to the bucket."""
#     # The ID of your GCS bucket
#     # bucket_name = "your-bucket-name"
#     # The path to your file to upload
#     # source_file_name = "local/path/to/file"
#     # The ID of your GCS object
#     # destination_blob_name = "storage-object-name"

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)

#     blob.upload_from_filename(source_file_name)

#     print(
#         f"File {source_file_name} uploaded to {destination_blob_name}."
#     )


# Download cryptocurrency data (2017 - 2022)
def read_data(ticker='ETH-USD'):
    today = date.today()
    datetoday = today.strftime("%B %d, %Y")
    print(f"\nDownloading the dataset for {ticker} on {datetoday} ...\n\n")
    df = yf.download(ticker)
    df = df.reset_index()
    df['Timestamp'] = df.Date.apply(lambda x: pd.Timestamp(x).timestamp())
    df = df.drop(labels=['Date', 'Adj Close'], axis=1)
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Timestamp'] = df['Timestamp'].apply(lambda x: int(str(x)[:-2] + "000"))
    
    df.to_csv("data/" + ticker+"_"+today.strftime("%d_%m_%Y")+".csv", index=False)

    # 10% data to test
    training_data, testing_data = train_test_split(df, test_size=0.1, shuffle=False)
    training_data, testing_data = list(training_data['Close']), list(testing_data['Close'])
    return df, training_data, testing_data

def mape(model_predictions, testing_data):
    return np.mean(np.abs(np.array(model_predictions) - np.array(testing_data)) / np.abs(testing_data))

def train_model_search():
    df, training_data, testing_data = read_data()
    

    # Using GRID Search instead of Randomized Hyperopt as number of prameters are lesser
    ps = range(2, 3)
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

            #try:
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

            model_fit.save('model.pkl')

            mlflow.log_metric("AIC", model_fit.aic)
            mlflow.log_metric("BIC", model_fit.bic)
            mlflow.log_metric("mape", mape_val)
                
                # mlflow.pmdarima.log_model(model_fit, artifact_path="ARIMA_ETHUSD")

            # except Exception as e:
            #     print(e)
            #     print("Logging AIC, BIC, mape as inf")
            #     mlflow.log_metric("AIC", float('inf'))
            #     mlflow.log_metric("BIC", float('inf'))
            #     mlflow.log_metric("mape", float('inf'))

    return 

def register_model():

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

    print("\nTraining the model...\n")
    for i in range(n_test_obs):
        model = ARIMA(training_data, order = (4,1,0))
        model_fit = model.fit(disp=0)
        output = model_fit.forecast()
        yhat = list(output[0])[0]
        model_predictions.append(yhat)
        actual_test_value = testing_data[i]
        # Rolling Training by predicting one day ahead and appending to 
        training_data.append(actual_test_value)

    mape_val = mape(model_predictions, testing_data)

    return model_fit, mape_val

def main():
    # df, training_data, testing_data = read_data()
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("arima-ethusdt")
    print(f"Searching Best Model ...")
    train_model_search()
    print(f"Registering Model.")
    register_model()
    print("Done.")
    # model, mape_val = train()
    #print(f"MAPE = {mape_val}\n\nSaving the model now...")
    #model.save('model/model.pkl')
    #print("Saved.")

    #return mape_val

if __name__ == '__main__':
    main()





