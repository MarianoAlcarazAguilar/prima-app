#! /bin/bash

# Este script sirve para sacar los logs del contenedor
CONTAINER_NAME="prima-values-automation-container"

# Sobreescribimos los logs de la nube al local del ec2
sudo docker cp $CONTAINER_NAME:/app/logs /home/ubuntu/prima-app/