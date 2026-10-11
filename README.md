# Digital Elevation Model (DEM) Processing Pipeline

This repository contains Python scripts for downloading, organizing, and mosaicking Copernicus DEM GLO-30 elevation data for geospatial analysis. The workflow retrieves elevation tiles for a specified area of interest (AOI), then combines the downloaded tiles into a single GeoTIFF raster for use in GIS, remote sensing, and spatial modeling.

## Scripts

### `download_dem.py`
Downloads Copernicus DEM GLO-30 tiles covering a user-defined geographic area. Supports configurable AOI coordinates, output directories, download progress tracking, and temporary files to reduce the risk of incomplete downloads.

### `stitch_dem.py`
Combines downloaded DEM tiles into a single GeoTIFF mosaic. Uses GDAL when available, with a Rasterio-based fallback. Supports configurable input and output paths, NoData values, output data type, LZW compression, overwrite controls, and progress reporting.

## Requirements

- Python 3.9+
- `requests`
- `rasterio`
- `numpy`
- GDAL (optional; used for the preferred mosaicking workflow)

Install the Python dependencies with:

```bash
pip install requests rasterio numpy
```

GDAL can be installed separately if needed for the GDAL-based mosaicking workflow.

## Workflow

1. Configure the area of interest and output directory in `download_dem.py`.
2. Run the downloader to retrieve the required elevation tiles.
3. Configure `DEM_DIR` and `OUT_PATH` in `stitch_dem.py`.
4. Run the mosaicking script to combine the tiles into a single DEM GeoTIFF.
5. Inspect the resulting raster in GIS software or use it as an input to subsequent geospatial analyses.

## Configuration

Replace local file paths with paths appropriate for your system. The scripts are designed to use configurable directories rather than requiring a fixed project structure.

Important settings include:

- `BASE_DIR`: Base directory for downloaded DEM tiles.
- `DEM_DIR`: Directory containing the downloaded tiles.
- `OUT_PATH`: Destination path for the mosaicked DEM.
- `NODATA_IN` and `NODATA_OUT`: Input and output NoData values.
- `OUT_DTYPE`: Output raster data type.
- `COMPRESS`: GeoTIFF compression method.
- `OVERWRITE`: Whether existing outputs may be replaced.

## Outputs

- Individual Copernicus DEM GLO-30 elevation tiles.
- A mosaicked DEM GeoTIFF covering the combined tile extent.

## Notes

- Ensure the selected AOI is covered by the downloaded tiles.
- Keep the original tile files until the mosaic has been checked.
- GDAL provides native progress reporting during mosaicking. Progress reporting in the Rasterio fallback may be limited because the merge operation itself does not expose incremental progress through the current implementation.
- The resulting DEM can support terrain analysis, elevation mapping, slope calculations, and other spatial workflows.

## Disclaimer

This repository provides a configurable DEM download and processing workflow. Verify the geographic coverage, coordinate reference system, resolution, NoData handling, and output integrity before using the resulting raster in research or operational analyses.
