import geopandas as gpd
from measure import measure_match_coords_4, measure_match_coords_5, measure_match_h3_13, measure_match_h3_14, measure_match_s2_21, measure_match_s2_22
from tools import load_data, define_polygons_h3, define_polygons_shapely, \
    define_polygons_s2, merge_dfs, get_confusion_matrix, calculate_metrics

N_AMOUNT = 1000000
GEOMETRY_FILE = "./data/polygon_100_ber.geojson"
MAID_FILE = "./data/athena_output_1m_berlin.csv"

df = load_data(MAID_FILE, amount=N_AMOUNT)
gdf_poly = gpd.read_file(GEOMETRY_FILE)

coords_poly = define_polygons_shapely(gdf_poly=gdf_poly)
h3_13_poly = define_polygons_h3(gdf_poly=gdf_poly, h3_res=13)
h3_14_poly = define_polygons_h3(gdf_poly=gdf_poly, h3_res=14)
s2_21_poly = define_polygons_s2(gdf_poly=gdf_poly, s2_res=21)
s2_22_poly = define_polygons_s2(gdf_poly=gdf_poly, s2_res=22)

coord_4_matches = measure_match_coords_4(coords_poly=coords_poly,  df=df, res=4)
coord_5_matches = measure_match_coords_5(coords_poly=coords_poly,  df=df,  res=5)
h3_13_matches = measure_match_h3_13(h3_poly=h3_13_poly, df=df, res=13)
h3_14_matches = measure_match_h3_14(h3_poly=h3_14_poly, df=df, res=14)
s2_21_matches = measure_match_s2_21(s2_poly=s2_21_poly,  df=df, res=21)
s2_22_matches = measure_match_s2_22(s2_poly=s2_22_poly,  df=df, res=22)

confusion_df = get_confusion_matrix(merge_dfs(coord_4_matches, coord_5_matches, h3_13_matches, h3_14_matches, s2_21_matches, s2_22_matches))
result = calculate_metrics(confusion_df)
print(result)

