## Instalación de Django y dependencias

1. Instala Django:
    ```bash
    python -m pip install Django==5.1.6
    ```

2. Instala `drf_yasg` (debes instalarlo dentro del proyecto, en la raíz del proyecto):
    ```bash
    pip install drf_yasg
    ```

3. Instala `rest_framework` en la misma ubicación del anterior:
    ```bash
    pip install rest_framework
    ```

4. En caso de que no funcione el anterior, ejecutar:
    ```bash
    pip install djangorestframework
    ```

5. Instala `django-cors-headers` si hay errores y vuelve a repetir el comando de migración:
    ```bash
    pip install django-cors-headers
    ```

## Migraciones

1. Ejecuta este comando para iniciar la migración:
    ```bash
    python manage.py makemigrations
    ```

2. Ahora ejecuta este:
    ```bash
    python manage.py migrate
    ```

## Creación del contenedor MySQL

1. Comando de consola para poder crear el contenedor:
    ```bash
    docker run -d -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=123456 mysql:latest
    ```
2. desplegar con portainer:
    ```bash
        docker run -d --name portainer `
        -p 9000:9000 `
        -p 8000:8000 `
        --restart=always `
        -v /var/run/docker.sock:/var/run/docker.sock `
        -v portainer_data:/data `
         portainer/portainer-ce

    ```

    se abre con:
    ```
    http://localhost:9000
    ```
## desplegar el back-end
1. ejecita el sigiente comando para desplegar el back-end
```bash
    python manage.py runserver
```
## Instalación del Frontend

1. Inicializar en la terminal desde la raíz del proyecto (en este caso: `AutoGestionSena\front-desercion`):
    ```bash
    npm install
    ```

2. Debería de aparecer la carpeta `node_modules`.

3. Iniciar el front con el comando:
    ```bash
    npm run dev
    ```
4. listo deberias de poder ver tu proyecto
