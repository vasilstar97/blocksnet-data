import os
import json
import geopandas as gpd
from blocksnet.config import log_config

# disable output
log_config.set_disable_tqdm(True)
log_config.set_logger_level('ERROR')

# const
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
BLOCKS_FILE_NAME = 'blocks.geojson'
BUILDINGS_FILE_NAME = 'buildings.geojson'
DISTRICTS_FILE_NAME = 'districts.geojson'
SERVICES_FOLDER = 'services'

from utils import get_blocks_gdf, get_land_use_df, get_buildings_df, get_services_dfs

blocks_gdf = get_blocks_gdf(
    os.path.join(DATA_PATH, BLOCKS_FILE_NAME)
)
land_use_df = get_land_use_df(
    blocks_gdf, 
    os.path.join(DATA_PATH, BLOCKS_FILE_NAME)
)
buildings_df = get_buildings_df(
    blocks_gdf, 
    os.path.join(DATA_PATH, BUILDINGS_FILE_NAME),
    os.path.join(DATA_PATH, DISTRICTS_FILE_NAME)
)
services_dfs = get_services_dfs(
    blocks_gdf, 
    os.path.join(DATA_PATH, SERVICES_FOLDER)
)

result_gdf = blocks_gdf.copy()

for df in [land_use_df, buildings_df, *services_dfs]:
    result_gdf = result_gdf.join(df)

result_gdf.to_pickle('blocks.pickle')
result_gdf.to_file('blocks.geojson')

from utils import get_accessibility_tuple
import pickle

for graph_type in ['drive', 'intermodal']:
    graph, acc_mx = get_accessibility_tuple(blocks_gdf, graph_type)
    with open(f'graph_{graph_type}.pickle', 'wb') as file:
        pickle.dump(graph, file)
    acc_mx.to_pickle(f'accessibility_matrix_{graph_type}.pickle')