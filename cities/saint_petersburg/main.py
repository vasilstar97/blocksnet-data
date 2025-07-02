import os
import json
import geopandas as gpd
from blocksnet.config import log_config, service_types_config
from blocksnet.enums import LandUse
from blocksnet.blocks.assignment import assign_land_use
from blocksnet.preprocessing.imputing import impute_buildings, impute_services
from blocksnet.blocks.aggregation.core import aggregate_objects, COUNT_COLUMN

# const
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
SERVICES_FOLDER = 'services'
BLOCKS_FILE_NAME = 'blocks.geojson'
BUILDINGS_FILE_NAME = 'buildings.geojson'
LU_RULES_FILE_NAME = 'land_use_rules.json'

BUILDINGS_COLUMNS = {
    'geometry':'geometry',
    'storeys_count':'number_of_floors',
    'is_living':'is_living',
    'building_area':'footprint_area',
    'living_area':'living_area',
    'population_balanced':'population',
}
BUILDINGS_DROP_COLUMNS = ['is_living', 'number_of_floors']
COUNT_BUILDINGS_COLUMN = 'count_buildings'

# disable output
log_config.set_disable_tqdm(True)
log_config.set_logger_level('ERROR')

# read blocks
print('Reading blocks')
blocks = gpd.read_file(os.path.join(DATA_PATH, BLOCKS_FILE_NAME))
crs = blocks.estimate_utm_crs()
blocks = blocks.to_crs(crs)

# assign functional zones
print('Assigning functional zones')
functional_zones = gpd.read_file(os.path.join(DATA_PATH, 'functional_zones.geojson')).to_crs(crs)
with open(os.path.join(DATA_PATH, LU_RULES_FILE_NAME)) as o:
    land_use_rules = json.loads(o.read())
    land_use_rules = {zone : LandUse(lu.lower()) for zone,lu in land_use_rules.items()}
blocks_lu = assign_land_use(blocks, functional_zones, land_use_rules)

# aggregate buildings parameters
print('Aggregating')
buildings = gpd.read_file(os.path.join(DATA_PATH, BUILDINGS_FILE_NAME)).to_crs(crs)
buildings = buildings[BUILDINGS_COLUMNS.keys()].rename(columns=BUILDINGS_COLUMNS)
buildings = impute_buildings(buildings[BUILDINGS_COLUMNS.values()])

blocks_buildings,_ = aggregate_objects(blocks, buildings)
blocks_buildings = blocks_buildings.drop(columns=BUILDINGS_DROP_COLUMNS).rename(columns={COUNT_COLUMN: COUNT_BUILDINGS_COLUMN})

# aggregate services parameters
print('Aggregating services parameters')
services_path = os.path.join(DATA_PATH, SERVICES_FOLDER)
for file_name in os.listdir(services_path):
    service_type = file_name.split('.')[0]
    if service_type not in service_types_config:
        print(f'- {service_type} is presented, but not in the config')

for service_type in service_types_config:
    file_name = os.path.join(services_path, f'{service_type}.geojson')
    if not os.path.exists(file_name):
        print(f'- {service_type} is in the config, but not presented')

services_gdfs = {}

for service_type in service_types_config:
    file_name = os.path.join(services_path, f'{service_type}.geojson')
    if os.path.exists(file_name):
        gdf = gpd.read_file(file_name).to_crs(crs)
        gdf = gdf[~gdf.geometry.isna()].copy()
        services_gdfs[service_type] = gdf

print(f'{len(services_gdfs)} / {len(service_types_config.service_types)} service types will be in the result')

services_gdfs = {st:impute_services(gdf,st) for st,gdf in services_gdfs.items()}

blocks_services = {}

for service_type,services_gdf in services_gdfs.items():
    gdf,_ = aggregate_objects(blocks, services_gdf)
    gdf = gdf.rename(columns={
        'capacity':f'capacity_{service_type}',
        'count':f'count_{service_type}',
    })
    blocks_services[service_type] = gdf

# finale
print('Finalizing the blocks')
blocks['site_area'] = blocks.area
blocks = blocks.join(blocks_lu.drop(columns=['geometry']))
blocks = blocks.join(blocks_buildings.drop(columns=['geometry']))
for gdf in blocks_services.values():
    blocks = blocks.join(gdf.drop(columns=['geometry']))

blocks.to_pickle('blocks.pickle')
blocks.to_file('blocks.geojson')