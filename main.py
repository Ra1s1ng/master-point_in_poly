import geopandas as gpd
from measure import measure_match
import pandas as pd
from tools import load_data, define_polygons_h3, define_polygons_shapely, \
    define_polygons_s2, merge_dfs, get_confusion_matrix, calculate_metrics

N_AMOUNT = 1000000
POLY_AMOUNT = 100
GEOMETRY_FILE = "./data/polygon_100_ber.geojson"
MAID_FILE = "./data/athena_output_1m_ber.csv"

df = load_data(MAID_FILE, amount=N_AMOUNT)
gdf_poly = gpd.read_file(GEOMETRY_FILE).sample(n=POLY_AMOUNT, random_state=14)

coords_poly = define_polygons_shapely(gdf_poly=gdf_poly)
# h3_13_poly = define_polygons_h3(gdf_poly=gdf_poly, h3_res=13)
# h3_14_poly = define_polygons_h3(gdf_poly=gdf_poly, h3_res=14)
# s2_21_poly = define_polygons_s2(gdf_poly=gdf_poly, s2_res=21)
# s2_22_poly = define_polygons_s2(gdf_poly=gdf_poly, s2_res=22)

coord_4_matches = measure_match(method="Coord", poly_data=coords_poly,  df=df, res=4)
coord_5_matches = measure_match(method="Coord", poly_data=coords_poly,  df=df, res=5)
# h3_13_matches = measure_match(method="H3", poly_data=h3_13_poly, df=df, res=13)
# h3_14_matches = measure_match(method="H3", poly_data=h3_14_poly, df=df, res=14)
# s2_21_matches = measure_match(method="S2", poly_data=s2_21_poly,  df=df, res=21)
# s2_22_matches = measure_match(method="S2", poly_data=s2_22_poly,  df=df, res=22)

confusion_df = get_confusion_matrix(merge_dfs(df1=coord_4_matches, df2=coord_5_matches))
result = calculate_metrics(df=confusion_df, n_amount=N_AMOUNT)
pd.set_option('display.max_columns', 8)
print(result)

