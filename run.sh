#!/bin/bash

nohup bash -c 'source env/bin/activate && gunicorn -w 2 -b 0.0.0.0:8000 app:app --timeout 300' > output.log 2>&1 &
