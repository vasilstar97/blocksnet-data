import geopandas as gpd
import pandas as pd
import networkx as nx
from blocksnet.relations.accessibility import get_accessibility_graph, calculate_accessibility_matrix

def get_accessibility_tuple(blocks_gdf : gpd.GeoDataFrame, graph_type : str) -> tuple[nx.Graph, pd.DataFrame]:
    print(f'Making {graph_type} graph and matrix')
    graph = get_accessibility_graph(blocks_gdf, graph_type)
    acc_mx = calculate_accessibility_matrix(blocks_gdf, graph)
    return graph, acc_mx

    