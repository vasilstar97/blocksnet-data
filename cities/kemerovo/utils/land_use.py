import geopandas as gpd
import pandas as pd
from blocksnet.enums import LandUse
from blocksnet.blocks.assignment import assign_land_use

def get_land_use_df(blocks_gdf : gpd.GeoDataFrame, file_path : str) -> pd.DataFrame:
    print('Assigning land use')
    functional_zones_gdf = gpd.read_file(file_path).to_crs(blocks_gdf.crs)
    functional_zones_gdf.geometry = functional_zones_gdf.representative_point()

    for lu in LandUse:
        functional_zones_gdf[lu.value] = (functional_zones_gdf['land_use'] == lu).astype(int) 
    functional_zones_gdf['land_use'] = functional_zones_gdf['land_use'].map(LandUse)
    functional_zones_gdf['share'] = 1.0

    return blocks_gdf.sjoin(functional_zones_gdf)[[*[lu.value for lu in LandUse], 'land_use', 'share']].copy()