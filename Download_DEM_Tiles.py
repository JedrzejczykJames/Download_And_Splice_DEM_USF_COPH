import os
import re
import math
import time
import requests

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR = "/PATH/TO/BASE/DIR"
DEM_DIR  = os.path.join(BASE_DIR, "DEM")

WEST = /INSERT/WEST/HERE
SOUTH = /INSERT/SOUTH/HERE
EAST = /INSERT/EAST/HERE
NORTH = /INSERT/NORTH/HERE

# ── Helpers ───────────────────────────────────────────────────────────────────
def log(msg):
    print(msg, flush=True)

def print_progress(current, total, start_time):
    """Display overall tile download progress with elapsed time and ETA."""
    elapsed = time.time() - start_time
    fraction = current / total if total else 1.0
    eta = (elapsed / fraction - elapsed) if fraction > 0 else 0.0
    width = 30
    filled = int(width * fraction)
    bar = "#" * filled + "-" * (width - filled)

    print(
        f"\r  [{bar}] {fraction * 100:6.2f}% "
        f"({current}/{total}) "
        f"Elapsed: {elapsed:.1f}s "
        f"ETA: {eta:.1f}s",
        end="\n" if current == total else "",
        flush=True,
    )

def print_download_progress(downloaded, total, filename):
    """Display byte-level progress for an individual DEM tile."""
    if total <= 0:
        return

    fraction = min(downloaded / total, 1.0)
    width = 30
    filled = int(width * fraction)
    bar = "#" * filled + "-" * (width - filled)
    downloaded_mb = downloaded / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    print(
        f"\r    [{bar}] {fraction * 100:6.2f}% "
        f"{downloaded_mb:.1f}/{total_mb:.1f} MB",
        end="\n" if downloaded >= total else "",
        flush=True,
    )

def aoi_to_dem_tiles(west, east, south, north):
    """Return all COP-DEM tile identifiers covering the AOI."""
    tiles = set()
    for lat in range(int(math.floor(south)), int(math.ceil(north))):
        for lon in range(int(math.floor(west)), int(math.ceil(east))):
            lat_hem = "N" if lat >= 0 else "S"
            lon_hem = "E" if lon >= 0 else "W"
            tiles.add((lat_hem, abs(lat), lon_hem, abs(lon)))
    return tiles

def tile_filename(lat_hem, lat_tile, lon_hem, lon_tile):
    return (
        f"Copernicus_DSM_COG_10_{lat_hem}{lat_tile:02d}_00"
        f"_{lon_hem}{lon_tile:03d}_00_DEM.tif"
    )

def download_dem_tile(lat_hem, lat_tile, lon_hem, lon_tile):
    name     = f"Copernicus_DSM_COG_10_{lat_hem}{lat_tile:02d}_00_{lon_hem}{lon_tile:03d}_00_DEM"
    filename = f"{name}.tif"
    url      = f"https://copernicus-dem-30m.s3.amazonaws.com/{name}/{filename}"
    out_path = os.path.join(DEM_DIR, filename)

    if os.path.exists(out_path):
        log(f"  Already exists: {filename}")
        return True

    log(f"  Downloading: {filename}")
    temp_path = out_path + ".part"

    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(temp_path, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            print_download_progress(downloaded, total_size, filename)

        os.replace(temp_path, out_path)
        if total_size <= 0:
            log(f"  Done: {filename} ({downloaded / (1024 * 1024):.1f} MB)")
        else:
            log(f"  Done: {filename}")
        return True

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        log(f"  FAILED {filename}: {e}")
        return False

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DEM_DIR, exist_ok=True)

    tiles = sorted(aoi_to_dem_tiles(WEST, EAST, SOUTH, NORTH))
    log(f"Total DEM tiles to download: {len(tiles)}")

    start_time = time.time()
    completed = 0
    successful = 0
    skipped = 0

    for tile in tiles:
        filename = tile_filename(*tile)
        out_path = os.path.join(DEM_DIR, filename)

        if os.path.exists(out_path):
            log(f"  Already exists: {filename}")
            skipped += 1
            completed += 1
        elif download_dem_tile(*tile):
            successful += 1
            completed += 1
        else:
            completed += 1

        print_progress(completed, len(tiles), start_time)

    log(f"Done. Downloaded: {successful} | Already existed: {skipped} | Failed: {len(tiles) - successful - skipped}")
