#!/bin/bash
cd ./src
# python3 main.py
uvicorn main:app --host 0.0.0.0
