#!/bin/bash

docker build -t mai-inventory-mgr -f docker/Dockerfile .

#!/bin/bash

docker rm "mai-inventory-mgr"
docker run --name="mai-inventory-mgr" -p 9205:9205 mai-inventory-mgr