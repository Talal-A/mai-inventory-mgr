#!/bin/bash

export $(cat .secrets | xargs) && python3 run-website.py d
