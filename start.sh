#!/bin/bash

nohup bash -c 'source env/bin/activate && python run.py' > output.log 2>&1 &