# Instalamos python 3.11
FROM python:3.11

# Especificamos el directorio de trabajo
WORKDIR /app

# Copiamos todos los archivos a la imagen 
# Aquí vale la pena mencionar que lo estoy haciendo de forma simplificada
# En realidad debería de eliminar todos los archivos de excel que ya existen 
COPY my_apis/ /app/my_apis/
COPY pages/ /app/pages/
COPY queries/ /app/queries/
COPY scripts/ /app/scripts/
COPY 1__Login_Info.py /app/
COPY requirements.txt /app/
COPY st_functions.py /app/
COPY style.css /app/

# Montamos todo para que pueda ejecutarse la aplicación
# Yo no lo voy a hacer dentro de un ambiente virtual.
RUN pip install -r requirements.txt 
RUN mv 1__Login_Info.py 1_📇_Login_Info.py

# Mencionamos el puerto que vamos a exponer al ejecutar el contenedor
ENV PORT 8501

# Quiero que puedan sobreescribir el comando
# Si se desea lo contrario, solo descomentar ENTRYPOINT
# ENTRYPOINT [ "executable" ] [ "streamlit", "run", "1_📝_Reportes.py" ]
CMD [ "streamlit", "run", "1_📇_Login_Info.py" ]