#! /bin/bash

# Este script sirve para sacar los logs del contenedor
CONTAINER_NAME="prima-values-automation-container"

sudo docker cp $CONTAINER_NAME:/app/logs ./logs

# El comando de abajo es para sacarlo de aws y a mi computadora local
# scp -i ~/.ssh/prima-key.pem -r ubuntu@18.224.199.4:/home/ubuntu/prima-app/logs/logs .