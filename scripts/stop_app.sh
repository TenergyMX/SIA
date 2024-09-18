#!/bin/bash
cd /home/ubuntu/test-sia
docker compose -f docker-compose.prod.yaml down
#docker image remove 903371078608.dkr.ecr.us-east-2.amazonaws.com/sia-app