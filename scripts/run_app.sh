#!/bin/bash
cd /home/ubuntu/test-sia
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 903371078608.dkr.ecr.us-east-2.amazonaws.com
docker compose -f docker-compose.prod.yaml up --build -d