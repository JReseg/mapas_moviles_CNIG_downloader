---English bellow---

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

##### Rendimiento
Conexión rápida (~100 Mb/s): `--max-workers``entre 2 o 3.

Si hay fallos de rechazo de descarga por pare del servidor, reducir el numero de descargas simultáneas `--max-workers 1` y hacer una pausa entre descargas `--sleep-between 15`.

##### Licencia

Este proyecto se distribuye bajo licencia MIT.

Los datos descargados pertenecen al Centro Nacional de Información Geográfica (CNIG, IGN España). Consulta sus términos de uso en la web oficial del CNIG.

---
This script allows you to **automatically and massively download all maps in MBTiles format** published for free download by the *Centro Nacional de Información Geográfica (CNIG)* in the following repository on their official website:  
[https://centrodedescargas.cnig.es/CentroDescargas/loadMapasMoviles.do](https://centrodedescargas.cnig.es/CentroDescargas/loadMapasMoviles.do)

The `.mbtiles` files are vector maps that can be used offline in compatible applications, such as the official app of the *Instituto Geográfico Nacional (IGN)*:  
[https://www.ign.es/web/dir-aplicaciones-moviles](https://www.ign.es/web/dir-aplicaciones-moviles)

##### Features
- Bulk download of the 165 Spain mobile maps from CNIG, with a total size of approximately 176 GB.  
- Automatic organization into folders by Provinces, Islands, and National Parks.  
- Parallel downloads (`--max-workers`) with automatic retries.  
- Basic file validation (minimum size, avoids saving error HTML).  
- Resume support: if execution is canceled and restarted, already completed files are skipped.

##### Usage
1. First, run the script `genera_urls_cnig.py`, which will create the file `urls.txt` with the 165 direct download links to the `.mbtiles` files:
  
  ```
   python genera_urls_cnig.py
  ```

2. Once the `.txt` file has been generated, run the second script to perform the download of the `.mbtiles` maps:

  ```
  python descarga_cnig.py --from-file urls.txt --dest mapas_cnig --max-workers 2
  ```

##### Download options:

`--max-workers N` → number of simultaneous downloads (default: 3).

`--min-bytes 200000` → minimum accepted file size (default: 200 KB).

`--timeout 90` → maximum time per request in seconds.

`--sleep-between 1` → pause between downloads (seconds).

`--retries 4` → number of retries per file in case of failure.

##### Performance

For a fast connection (~100 Mb/s): set `--max-workers between 2 or 3`.

If the server rejects too many downloads, reduce simultaneous downloads (`--max-workers 1`) and add a pause between downloads (`--sleep-between 15`).

##### License

This project is distributed under the MIT License.

The downloaded data belongs to the Centro Nacional de Información Geográfica (CNIG, IGN Spain). Please check their official website for usage terms










