import geopandas as gpd
from blocksnet.blocks.postprocessing import postprocess_urban_blocks
from blocksnet.analysis.geometry import calculate_area_length

def get_blocks_gdf(file_path : str) -> gpd.GeoDataFrame:
    print('Processing blocks')
    blocks_gdf = gpd.read_file(file_path)
    blocks_gdf = postprocess_urban_blocks(blocks_gdf)
    return calculate_area_length(blocks_gdf).drop(columns=['site_length'])
