#!/bin/bash

# Find the Gunicorn process by searching for the Python process running your app
PID=$(ps aux | grep 'gunicorn' | grep 'app:app' | awk '{print $2}')

# If the PID exists, kill the process
if [ -n "$PID" ]; then
  echo "Stopping Gunicorn with PID $PID..."
  kill -9 $PID
else
  echo "Gunicorn process not found."
fi