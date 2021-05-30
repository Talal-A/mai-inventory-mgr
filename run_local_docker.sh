#!/bin/bash

docker build -t mai-inventory-mgr -f docker/Dockerfile .

docker rm "mai-inventory-mgr"
docker run --name="mai-inventory-mgr" \
     -e TZ="America/Los_Angeles" \
     -e STAGE="beta" \
     -p 9205:9205 \
     -v ~/dev/mai-ucla-2/data:/data mai-inventory-mgr