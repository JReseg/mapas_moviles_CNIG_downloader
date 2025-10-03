# Mapas Moviles CNIG downloader
# Copyright (c) 2025 J. Reseg
# Licensed under the MIT License. See LICENSE file for details.

# -------------------------------------------------------------------
# Toma las URLs generadas por el script genera_urls_cnig.py en el archivo
# urls.txt procede a la descarga de los "Mapas para móviles" del CNIG,
# en formato .mbtiles.
# -------------------------------------------------------------------

import argparse
import concurrent.futures as futures
import os, re, time
from urllib.parse import urlparse, parse_qs
import requests

PARQUES_SLUGS = {
    "aigues-tortes","cabaneros","caldera","donana","garajonay","islas-atlanticas",
    "cabrera","monfrague","ordesa","picos-de-europa","guadarrama","sierra-nevada",
    "daimiel","timanfaya","teide","sierra-nieves",
}
ISLAS_SLUGS = {
    "mallorca","menorca","ibiza-y-formentera","cabrera","el-hierro","gomera","la-palma",
    "tenerife","fuerteventura","lanzarote","gran-canaria","melilla-e-islas-chafarinas",
}

CNIG_REFERER = "https://centrodedescargas.cnig.es/CentroDescargas/loadMapasMoviles.do"

def human_size(n: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def slug_from_url(u: str) -> str:
    q = parse_qs(urlparse(u).query)
    name = q.get("file", [os.path.basename(urlparse(u).path)])[0]
    return re.sub(r"\.mbtiles$", "", name, flags=re.IGNORECASE)

def pretty_name(slug: str) -> str:
    return " ".join(("y" if p.lower()=="y" else p.capitalize()) for p in slug.replace("-", " ").split())

def clasificar(slug: str):
    """
    Devuelve (categoria, subcarpeta).
    - Parques: carpeta por parque.
    - Islas: carpeta por isla.
    - Provincias: carpeta por provincia base (todas sus variantes juntas).
    """
    if slug in PARQUES_SLUGS:
        return "Parques", pretty_name(slug)

    for isl in sorted(ISLAS_SLUGS, key=len, reverse=True):
        if slug == isl or slug.startswith(isl):
            return "Islas", pretty_name(isl)

    # Provincias: tomar todo lo anterior al primer "_"
    base = slug.split("_")[0]
    return "Provincias", pretty_name(base)

def nombre_archivo(u: str) -> str:
    q = parse_qs(urlparse(u).query)
    if "file" in q and q["file"]:
        return q["file"][0]
    base = os.path.basename(urlparse(u).path)
    return base if base else "descarga.mbtiles"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CNIG-batch-downloader",
    "Accept": "*/*",
    "Connection": "keep-alive",
})

def descargar(url: str, dest_root: str, min_bytes: int, timeout=90, max_reintentos=4, backoff=2):
    """Descarga una URL en su carpeta clasificada."""
    try:
        slug = slug_from_url(url)
        categoria, subcarpeta = clasificar(slug)
        carpeta = os.path.join(dest_root, categoria, subcarpeta)
        os.makedirs(carpeta, exist_ok=True)
        os.makedirs(os.path.join(dest_root, "errores"), exist_ok=True)

        fname = nombre_archivo(url)
        destino = os.path.join(carpeta, fname)

        # si ya existe y parece válido, se salta
        if os.path.exists(destino) and os.path.getsize(destino) >= min_bytes:
            return (destino, True, f"skip (existe {human_size(os.path.getsize(destino))})")

        intento = 0
        while intento < max_reintentos:
            intento += 1
            try:
                # header Referer para evitar anti-hotlink
                with SESSION.get(url, stream=True, timeout=timeout,
                                 headers={"Referer": CNIG_REFERER}, allow_redirects=True) as r:
                    status = r.status_code
                    ctype = (r.headers.get("Content-Type") or "").lower()
                    # Si claramente es HTML (login/error), se guarda para diagnóstico
                    if "text/html" in ctype or status >= 400:
                        html_path = os.path.join(dest_root, "errores", f"{slug}-intento{intento}.html")
                        with open(html_path, "wb") as f:
                            f.write(r.content)
                        raise IOError(f"respuesta {status} ({ctype})")

                    # Descarga binaria
                    tmp_path = destino + ".part"
                    descargados = 0
                    with open(tmp_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*128):
                            if chunk:
                                f.write(chunk)
                                descargados += len(chunk)
                    # Validación mínima
                    os.replace(tmp_path, destino)
                    if descargados < min_bytes:
                        raise IOError(f"archivo demasiado pequeño ({human_size(descargados)})")

                    return (destino, True, f"ok ({human_size(descargados)})")

            except Exception as e:
                if intento < max_reintentos:
                    time.sleep(backoff ** intento)  # backoff exponencial
                else:
                    # último intento: si quedó .part, se elimina
                    try:
                        if os.path.exists(destino + ".part"): os.remove(destino + ".part")
                    except Exception:
                        pass
                    return (destino, False, f"error: {e}")

    except Exception as e:
        return ("", False, f"error de clasificación: {e}")

def leer_urls(path: str):
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            u = ln.strip()
            if u and not u.startswith("#"):
                urls.append(u)
    return urls

def main():
    ap = argparse.ArgumentParser(description="Descarga CNIG Mapas móviles desde urls.txt")
    ap.add_argument("--from-file", default="urls.txt", help="Archivo con URLs (una por línea)")
    ap.add_argument("--dest", default="descargas_cnig", help="Carpeta raíz de salida")
    ap.add_argument("--max-workers", type=int, default=3, help="Descargas en paralelo (menos para evitar bloqueos)")
    ap.add_argument("--min-bytes", type=int, default=200_000, help="Tamaño mínimo para considerar éxito (por defecto 200KB)")
    args = ap.parse_args()

    urls = leer_urls(args.from_file)
    if not urls:
        print("No hay URLs en", args.from_file); return

    print(f"Procesando {len(urls)} URL(s). Carpeta: {args.dest}. Concurrencia: {args.max_workers}")
    ok = fail = 0
    with futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futs = [ex.submit(descargar, u, args.dest, args.min_bytes) for u in urls]
        for fu in futures.as_completed(futs):
            destino, success, msg = fu.result()
            print(f"[{'OK' if success else 'XX'}] {destino} -> {msg}")
            ok += int(success); fail += int(not success)

    print("\nResumen:")
    print(f"   Éxitos : {ok}")
    print(f"   Fallos : {fail}")
    if fail:
        print("  Revisa la carpeta 'errores/' para ver las páginas HTML devueltas por el servidor;")
        print("  baja --max-workers, vuelve a ejecutar, o inicia sesión en el navegador y exporta cookies si hiciera falta.")

if __name__ == "__main__":
    main()
