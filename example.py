import fused


@fused.udf
def udf(bbox: fused.types.TileGDF = None):
    import s3fs
    import xarray as xr
    import rioxarray
    import numpy as np
    import mercantile
    from pyproj import Transformer
    from rasterio.transform import from_bounds
    from rasterio.enums import Resampling

    fs = s3fs.S3FileSystem(
        key=KEY,
        secret=SECRET,
        client_kwargs={
            "endpoint_url": "https://fsn1.your-objectstorage.com",
            "region_name": "fsn1",
        },
    )
    path = "treeo-saas/remote_sensing_saas/01-korindo/final_zone/final_ds.zarr"
    ds = xr.open_zarr(fs.get_mapper(path), consolidated=False)
    zone = ds["subtype_zone"].rio.write_crs("EPSG:32749")

    if bbox is None:
        west, south, east, north = mercantile.bounds(830, 512, 10)
    else:
        west, south, east, north = bbox.total_bounds
    print("BBOX:", west, south, east, north)

    to_merc = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    xmin, ymin = to_merc.transform(west, south)
    xmax, ymax = to_merc.transform(east, north)

    to_utm = Transformer.from_crs("EPSG:3857", "EPSG:32749", always_xy=True)
    corners = [to_utm.transform(cx, cy) for cx in (xmin, xmax) for cy in (ymin, ymax)]
    xs, ys = zip(*corners)
    buf = 500

    empty = np.zeros((4, 256, 256), dtype=np.uint8)
    try:
        crop = zone.rio.clip_box(
            minx=min(xs) - buf, maxx=max(xs) + buf,
            miny=min(ys) - buf, maxy=max(ys) + buf,
        )
    except Exception as e:
        print("No data for tile:", e)
        return empty

    tile = crop.rio.reproject(
        "EPSG:3857",
        transform=from_bounds(xmin, ymin, xmax, ymax, 256, 256),
        shape=(256, 256),
        resampling=Resampling.nearest,
    )
    arr = np.nan_to_num(tile.values.squeeze(), nan=0).astype(np.uint8)

    colors = {
        1: (34, 139, 34, 180),   2: (154, 205, 50, 180),
        3: (144, 238, 144, 180), 4: (210, 180, 140, 180),
        5: (30, 144, 255, 180),  6: (255, 165, 0, 180),
        7: (128, 128, 128, 180), 8: (255, 99, 71, 180),
        9: (238, 232, 170, 180), 10: (139, 69, 19, 180),
    }
    img = empty.copy()
    for value, rgba in colors.items():
        mask = arr == value
        for b in range(4):
            img[b][mask] = rgba[b]
    return img