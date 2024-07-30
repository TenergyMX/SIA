#! /bin/bash
aws s3 cp s3://sia-docker-image/sia-app.tar .
tar -xvf sia-app.tar