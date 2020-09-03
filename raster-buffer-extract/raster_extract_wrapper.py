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


def main():
    # Prep playa centroid dataframe
    playa_gdf = gpd.read_file(shp)
    playa_gdf = playa_gdf[['id','geometry']]
    playa_gdf['geometry'] = playa_gdf['geometry'].centroid
    playa_gdf = playa_gdf.to_crs('epsg:4326')

    batch_size = 10000
    output_df = pd.DataFrame({'id':playa_gdf['id']})
    for raster in glob.glob(os.path.join(raster_dir, '*.tif')):
        year_search = re.findall(r'[0-9]{4}', raster) 
        if len(year_search)==0:
            print('Could not find raster year, skipping')
            break
        else:
            year = year_search[0]
        print('Start: {}'.format(year))
        ds = rio.open(raster)
        all_vals = []
        i = 0
        while i < playa_gdf.shape[0]:
            end = min(i+batch_size, playa_gdf.shape[0])
            all_vals += fe.random_buffer(playa_gdf.iloc[i:end]['geometry'], ds, radius=radius, n_sample=5000, stat='count_dict')
            i+=batch_size
        output_df['{}_r{}'.format(year, radius)] = all_vals
        print('Done: {}'.format(year))

    output_df.to_csv(output_csv, index=False)


if __name__=='__main__':
    main()
