Este script permite  descargar de forma automática y masiva todo los mapas en formato MBTiles publicados para libre descarga por el Centro Nacional de Información Geográfica (CNIG) en el siguiente repositorio de su página oficial (https://centrodedescargas.cnig.es/CentroDescargas/loadMapasMoviles.do)

Los archivos .mbtiles son mapas vectoriales que pueden usarse sin conexión en aplicaciones compatibles como es el caso de la aplicación oficial del Instituto Geográfico Nacional (https://www.ign.es/web/dir-aplicaciones-moviles)

##### Características
- Descarga masiva de los 165 mapas de España para móviles del CNIG, con un tamaño aproximado de 176 Gb en total.

- Organización automática en carpetas por Provincias, Islas y Parques Nacionales.

- Descargas en paralelo (`--max-workers`) con reintentos automáticos.

- Validación básica de archivos (mínimo de bytes, evita guardar HTML de error).

- Soporte de reanudación: si se cancela la ejecución y se reanuda, los ficheros ya completos se saltan.

##### Funcionamiento
1. En primer lugar se debe ejecutar el script `genera_urls_cnig.py`, el cual creará el fichero `urls.txt` con los 165 enlaces de descarga directos a los `.mbtiles`:
  ```
  python genera_urls_cnig.py
  ```

2. Una vez generado el fichero `.txt` se debe ejecutar el segundo script que lleva a cabo la descarga de los mapas `.mbtiles`:
  ```
python descarga_cnig.py --from-file urls.txt --dest mapas_cnig --max-workers 2
  ```
###### Opciones de descarga:
`--max-workers N` → nº de descargas simultáneas (predefinido: 3).

`--min-bytes 200000` → tamaño mínimo aceptado (predefinido: 200 KB).

`--timeout 90` → tiempo máximo por petición en segundos.

`--sleep-between 1` → pausa entre descargas (segundos).

`--retries 4` → nº de reintentos en caso de fallo.

###### Rendimiento
Conexión rápida (~100 Mb/s): `--max-workers``entre 2 o 3.

Si hay fallos de rechazo de descarga por pare del servidor, reducir el numero de descargas simultáneas `--max-workers 1` y hacer una pausa entre descargas `--sleep-between 15`.























