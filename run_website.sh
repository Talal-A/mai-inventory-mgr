#!/bin/bash

echo -e "\033[1;37m Running on https://127.0.0.1:9205/ \033[0m"
export $(cat .secrets | xargs) && python3 run-website.py d
