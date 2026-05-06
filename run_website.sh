#!/bin/bash

if [ -d "./data" ]; then
  echo "Data directory exists."
else
  echo "Data directory does not exist."
  mkdir data
fi


echo -e "\033[1;37m Running on https://127.0.0.1:9205/ \033[0m"
if [ -x "./.venv/bin/python" ]; then
  PYTHON_CMD="./.venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_CMD="python3.12"
else
  PYTHON_CMD="python3"
fi

export $(cat .secrets | xargs) && "$PYTHON_CMD" run-website.py d
