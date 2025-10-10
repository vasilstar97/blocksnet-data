import geopandas as gpd
from blocksnet.preprocessing.imputing import impute_buildings, impute_population
from blocksnet.blocks.aggregation import aggregate_objects

def get_buildings_df(blocks_gdf : gpd.GeoDataFrame, buildings_path : str, districts_path : str) -> gpd.GeoDataFrame:
    print('Imputing buildings parameters')
    buildings_gdf = gpd.read_file(buildings_path).to_crs(blocks_gdf.crs)
    districts_gdf = gpd.read_file(districts_path).to_crs(blocks_gdf.crs)

    buildings_gdf['is_living'] = buildings_gdf['is_living'].astype(bool)
    buildings_gdf['number_of_floors'] = buildings_gdf['building:levels']
    buildings_gdf['build_floor_area'] = buildings_gdf['AREA_2']
    buildings_gdf['living_area'] = buildings_gdf['AREA_LIVE_']
    buildings_gdf['non_living_area'] = buildings_gdf['AREA_NLIVE']
    buildings_gdf['footprint_area'] = buildings_gdf['build_floor_area'] / buildings_gdf['number_of_floors']
    buildings_gdf = impute_buildings(buildings_gdf)

    print('Imputing buildings population')
    buildings_gdf['population'] = None
    buildings_gdf.geometry = buildings_gdf.representative_point()

    for district_id in districts_gdf.index:
        population = districts_gdf.loc[district_id, 'population']
        district_gdf = districts_gdf.loc[[district_id]].copy()
        tmp_gdf = buildings_gdf.sjoin(district_gdf)
        tmp_gdf = impute_population(tmp_gdf, int(population))
        buildings_gdf.loc[tmp_gdf.index, tmp_gdf.columns] = tmp_gdf

    print('Aggregating buildings')
    agg_df,_ = aggregate_objects(blocks_gdf, buildings_gdf)
    return agg_df.drop(columns=['is_living', 'number_of_floors', 'geometry']).rename(columns={'count': 'count_buildings'})
    
