#! /bin/bash

# Este script sirve para sacar los logs del contenedor
CONTAINER_NAME="prima-values-automation-container"

sudo docker cp $CONTAINER_NAME:/app/logs .