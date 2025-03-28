#!/bin/bash

# Define your command (or part of it) used with nohup
PROCESS_NAME="python run.py"

# Find the PID of the process
PID=$(pgrep -f "$PROCESS_NAME")

# Check if the process is running
if [ -n "$PID" ]; then
    echo "Stopping process $PROCESS_NAME (PID: $PID)..."
    kill "$PID"
    sleep 2  # Wait for process to terminate
    if ps -p "$PID" > /dev/null; then
        echo "Process did not terminate, forcing kill..."
        kill -9 "$PID"
    fi
else
    echo "No process found for $PROCESS_NAME."
fi
