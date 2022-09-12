#!/bin/sh
mlflow server --host=0.0.0.0 --port=5000 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=file:mlruns 