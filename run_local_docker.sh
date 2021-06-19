#!/bin/bash

docker build -t mai-inventory-mgr -f docker/Dockerfile .

docker rm "mai-inventory-mgr"
docker run --name="mai-inventory-mgr" \
     --env-file .secrets \
     -p 9205:9205 \
     -v ~/dev/mai-ucla-2/data:/data \
     -v ~/dev/mai-ucla-2/data/log:/var/log \
     mai-inventory-mgr