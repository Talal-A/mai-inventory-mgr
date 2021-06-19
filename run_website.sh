#!/bin/bash

export $(cat .secrets | xargs) && python3 run.py d