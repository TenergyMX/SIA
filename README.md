# SISTEMA DE INFRAESTRUCTURA Y ACTIVOS (SIA)
## Guía de Instalación Inicial:
#### Paso 1: Instalación de Dependencias
Primero, instala las dependencias necesarias utilizando pip:

```bash
pip install -r requirements.txt
```

#### Paso 2: Agregar Registros desde JSON a la Base de Datos

Para agregar registros desde archivos JSON a la base de datos, sigue estos pasos:

- Ejecuta el siguiente comando para agregar registros desde el archivo `roles.json`:
  
  ```bash
  python manage.py loaddata data/roles.json
  ```

- Luego, agrega registros desde el archivo `modulos.json`:

  ```bash
  python manage.py loaddata data/modulos.json
  ```

- Finalmente, agrega registros desde el archivo `submodulos.json`:

  ```bash
  python manage.py loaddata data/submodulos.json
  ```

#### Paso 3: Generar Archivos CSS

Genera los archivos `styles.css` y `styles.css.map` ejecutando el siguiente comando:

```bash
sass /static/assets/css/styles.scss /static/assets/css/styles.css
```

---
# Comandos Útiles

### Generar el archivo `requirements.txt`:

Puedes generar automáticamente el archivo `requirements.txt` con las dependencias de tu proyecto ejecutando el siguiente comando:

```bash
pip freeze > requirements.txt
```

### Generar un JSON a partir de los Datos en la Tabla:

Para exportar datos de una tabla a un archivo JSON, utiliza el siguiente comando:

```bash
python manage.py dumpdata nombre_app.nombre_tabla --indent 2 > nombre_archivo.json
```

Por ejemplo:

```bash
python manage.py dumpdata users.Role --indent 2 > roles.json
```

---
## Creado por
Tenergy