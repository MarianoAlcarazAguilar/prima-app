#! /bin/bash

IMAGE_NAME="prima-values-automation:latest"
CONTAINER_NAME="prima-values-automation-container"

sudo docker stop $CONTAINER_NAME
sudo docker rm $CONTAINER_NAME
sudo docker rmi $IMAGE_NAME

sudo docker system prune