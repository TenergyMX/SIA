#!/bin/bash
cd /home/ubuntu/test-sia
docker login -u AWS -p $(aws ecr get-login-password --region us-east-2) 903371078608.dkr.ecr.us-east-2.amazonaws.com
docker compose -f docker-compose.prod.yaml up --build -d