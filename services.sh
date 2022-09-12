#!/bin/bash

# Start the first process
./gunicorn.sh &
  
# Start the second process
./mlflow.sh &
  
# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?