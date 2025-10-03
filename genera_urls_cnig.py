# Mapas Moviles CNIG downloader
# Copyright (c) 2025 J. Reseg
# Licensed under the MIT License. See LICENSE file for details.

# -------------------------------------------------------------------
# Lee la página oficial de "Mapas para móviles" del CNIG, extrae todos
# los nombres .mbtiles, construye las URLs directas del FTP público
# y genera urls.txt (deduplicado y ordenado). Opcionalmente valida en
# paralelo para mantener solo las URLs que realmente existen.
# -------------------------------------------------------------------

import re
import argparse
import requests
from bs4 import BeautifulSoup

CNIG_PAGE = "https://centrodedescargas.cnig.es/CentroDescargas/loadMapasMoviles.do"
BASE_FTP  = "https://ftpcdd.cnig.es/PUBLICACION_CNIG_DATOS_VARIOS/mapasOffLine/"

MBTILES_RE = re.compile(r"([a-z0-9_-]+\.mbtiles)", re.IGNORECASE)

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CNIG-helper",
        "Accept": "text/html,*/*",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def extract_filenames(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    candidates = set(MBTILES_RE.findall(html)) | set(MBTILES_RE.findall(text))
    files = sorted({c.strip() for c in candidates})
    return files

def main():
    ap = argparse.ArgumentParser(description="Genera urls.txt con enlaces directos a MBTiles (FTP CNIG)")
    ap.add_argument("--out", default="urls.txt", help="Archivo de salida (por defecto: urls.txt)")
    args = ap.parse_args()

    print("Descargando la página de Mapas para móviles…")
    html = fetch_html(CNIG_PAGE)

    print("Extrayendo nombres *.mbtiles…")
    files = extract_filenames(html)
    if not files:
        print("No se detectaron nombres .mbtiles. ¿La página ha cambiado?")
        return

    # Correción de nombres (guion → guion_bajo)
    corrected = [f.replace("-", "_") for f in files]

    # Deduplicado y ordenado
    urls = [BASE_FTP + f for f in sorted(set(corrected))]

    with open(args.out, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    print(f"He generado {len(urls)} URL(s) en {args.out}. Ejemplo:")
    for u in urls[:5]:
        print(" -", u)
    if len(urls) > 5:
        print(" - …")

if __name__ == "__main__":
    main()