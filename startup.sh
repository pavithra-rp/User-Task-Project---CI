#!/bin/bash

pip install --upgrade pip
pip install -r requirements.txt

gunicorn application:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000