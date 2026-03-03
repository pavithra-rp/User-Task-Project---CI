#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
uvicorn application:app --host 0.0.0.0 --port 8000