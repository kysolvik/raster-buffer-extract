"""Requires fraster_extract.py in working dir"""
import fraster_extract as fe
import os
import glob
import geopandas as gpd
import re
import pandas as pd
import rasterio as rio


shp = ''
raster_dir = '../data/landcover/wgs84/'
output_csv = '../data/fraster_landcover_allyears_bigger.csv'
radius = 200

def argparse_init():
    """Prepare ArgumentParser for inputs"""

    p = argparse.ArgumentParser(
            description='Run Random Buffer Extract on Shapefile',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('shp',
        help = 'Path to shapefile with polygons or points',
        type = str)
    p.add_argument('raster',
        help = 'Path to raster, must be in WGS84 (lat/lon)',
        type = str)
    p.add_argument('output_csv',
        help = 'Path for output csv',
        type = str)
    p.add_argument('radius',
        help = 'Buffer radius, in meters',
        type = int)

    return(p)


def main():
    
    # Get Command Line Args
    parser = argparse_init()
    args = parser.parse_args()
     
    # Prep centroid dataframe
    gdf = gpd.read_file(args.shp)
    gdf['geometry'] = gdf['geometry'].centroid
    gdf = gdf.to_crs('epsg:4326')

    batch_size = args.batch_size
    output_df = gdf.copy().drop(columns='geometry')
    ds = rio.open(args.raster)
    all_vals = []
    i = 0
    while i < gdf.shape[0]:
        end = min(i+batch_size, gdf.shape[0])
        all_vals += fe.random_buffer(gdf.iloc[i:end]['geometry'], ds, radius=radius, n_sample=args.n_sample, stat=args.stat)
        i+=batch_size
    output_df[os.path.basename(args.raster)] = all_vals

    output_df.to_csv(args.output_csv, index=False)


if __name__=='__main__':
    main()
