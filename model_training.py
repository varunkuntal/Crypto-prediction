import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARMA', FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA', FutureWarning)

import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import pandas as pd
from datetime import date

from itertools import product
import mlflow

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
    ps = range(2, 5)
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

                mlflow.log_metric("AIC", model_fit.aic)
                mlflow.log_metric("BIC", model_fit.bic)
                mlflow.log_metric("mape", mape_val)
                mlflow.pmdarima.log_model(model_fit, artifact_path="ARIMA_ETHUSD")

            except Exception as e:
                print(e)
                print("Logging AIC, BIC, mape as inf")
                mlflow.log_metric("AIC", float('inf'))
                mlflow.log_metric("BIC", float('inf'))
                mlflow.log_metric("mape", float('inf'))

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
    print(f"Done.")
    # model, mape_val = train()
    #print(f"MAPE = {mape_val}\n\nSaving the model now...")
    #model.save('model/model.pkl')
    #print("Saved.")

    #return mape_val

if __name__ == '__main__':
    main()




