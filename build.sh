#!/bin/bash

rsync -trv --delete . root@nerv:/tmp/docker/mai-inventory-mgr

ssh root@nerv docker build -t mai-inventory-mgr:latest /tmp/docker/mai-inventory-mgr

ssh root@nerv docker stop mai-inventory-mgr

ssh root@nerv docker rm mai-inventory-mgr

ssh root@nerv docker run --name="mai-inventory-mgr" --network="host" -d -p 9205:9205 mai-inventory-mgr
