import os
import pandas as pd
import geopandas as gpd
from blocksnet.blocks.aggregation import aggregate_objects
from blocksnet.preprocessing.imputing import impute_services
from blocksnet.config import service_types_config

def get_services_dfs(blocks_gdf : gpd.GeoDataFrame, path : str) -> list[pd.DataFrame]:
    # aggregate services parameters
    print('Aggregating services parameters')
    for file_name in os.listdir(path):
        service_type = file_name.split('.')[0]
        if service_type not in service_types_config:
            print(f'- {service_type} is presented, but not in the config')

    agg_dfs = []
    for service_type in service_types_config:
        file_name = os.path.join(path, f'{service_type}.geojson')
        if os.path.exists(file_name):
            services_gdf = gpd.read_file(file_name).to_crs(blocks_gdf.crs)
            services_gdf = impute_services(services_gdf, service_type)
            agg_df,_ = aggregate_objects(blocks_gdf, services_gdf)
            agg_dfs.append(agg_df[['capacity', 'count']].rename(columns={
                'capacity': f'capacity_{service_type}',
                'count': f'count_{service_type}',
            }))
        else:
            print(f'- {service_type} is in the config, but not presented')

    print(f'{len(agg_dfs)} / {len(service_types_config.service_types)} service types will be in the result')

    return agg_dfs