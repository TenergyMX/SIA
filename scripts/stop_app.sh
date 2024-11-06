#!/bin/bash
cd /home/ubuntu/test-sia
docker compose -f docker-compose.prod.yaml down
IMAGE=903371078608.dkr.ecr.us-east-2.amazonaws.com/sia-app
if docker images | grep -q "$IMAGE"; then
  echo "Image $IMAGE exists. Removing it..."
  docker image remove 903371078608.dkr.ecr.us-east-2.amazonaws.com/sia-app
  echo "Image $IMAGE removed successfully."
else
  echo "Image $IMAGE not found"
fi