# Notas
Este repostiorio necesita el submódulo de mis apis. Para ejecutarlo de manera adecuada es necesario seguir los siguientes pasos:

1. En vez de clonar simplemente el repositorio, es necesario correr este comando para también traer el contenido de **my_apis**

```sh
git clone --recurse-submodules https://github.com/MarianoAlcarazAguilar/prima-app
```

Si ya clonaste el repositorio y se te olvidó correr el comando así, es necesario correr los siguientes comandos.

```sh
git submodule init
git submodule update
```

2. Para traer los cambios que haya en el repositorio de my_apis hay dos opciones.

La **primera opción** es meterse al directorio y correr los siguientes comandos,

```sh
git fetch
git merge
```

La **segunda opción** es correr este comando desde el directorio de la app,

```sh
git submodule update --remote my_apis
```

Con cualquiera de esas dos ya estará actualizado el directorio de las apis.  
**No es recomendable hacer cambios a my_apis desde aquí, mejor hacerlo directo en el otro repo**.







