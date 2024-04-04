#! /bin/bash

# Primero sacamos los datos del contenedor
ssh -i ~/.ssh/prima-key.pem ubuntu@18.224.199.4 "bash /home/ubuntu/prima-app/scripts/retrieve_change_logs.sh"
# Luego traemos los documentos a la computadora local
scp -i ~/.ssh/prima-key.pem -r ubuntu@18.224.199.4:/home/ubuntu/prima-app/logs/logs .
