import pandas
import pandas as pd
import geopandas as gpd
import s2.s2
import s2sphere
import shapely

from tools import load_data, coord_matching, h3_matching, define_polygons_h3, define_polygons_shapely, \
    define_polygons_s2, s2_matching, prepare_cells_and_points
import cProfile
import timeit

N_AMOUNT = 10
GEOMETRY_FILE = "data/polygon_ber_ber_mun.geojson"
MAID_FILE = "./data/athena_output_10k_de.csv"
H3_RES = 13
S2_RES = 22



def measure_match_coords(coords_poly):
    p_coord = cProfile.Profile()
    p_coord.enable()
    coord_matches = coord_matching(df=df, coord_poly=coords_poly)
    p_coord.disable()
    p_coord.dump_stats("data/coord_stats")

    num_matches = coord_matches["matching_polygon"].notna().sum()
    print(f"Coord Matches: {num_matches} out of {len(df)} points\n")


def measure_match_h3(h3_poly):
    p_h3 = cProfile.Profile()
    p_h3.enable()
    h3_matches = h3_matching(df=df, h3_poly=h3_poly)
    p_h3.disable()
    p_h3.dump_stats("data/h3_stats")

    num_matches = h3_matches["matching_h3_cell"].notna().sum()
    print(f"H3 Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(h3_matches["device_id"], h3_matches["matching_h3_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")


def measure_match_s2(s2_poly):
    p_s2 = cProfile.Profile()
    p_s2.enable()
    s2_matches = s2_matching(df=df, s2_poly=s2_poly)
    p_s2.disable()
    p_s2.dump_stats("data/s2_stats")

    num_matches = s2_matches["matching_h3_cell"].notna().sum()
    print(f"H3 Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(s2_matches["device_id"], s2_matches["matching_h3_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")


def measure_match_geopandas(gdf_poly, gdf):
    p_geopandas = cProfile.Profile()
    p_geopandas.enable()
    gdf_joined = gpd.tools.sjoin(gdf, gdf_poly, how="inner")
    p_geopandas.disable()
    p_geopandas.dump_stats("data/geopandas_stats")
    num_matches_geopandas = len(gdf_joined.notna())
    print(f"Coord Matches: {num_matches_geopandas} out of {len(gdf)} points\n")


df = load_data(MAID_FILE, amount=N_AMOUNT)
gdf_poly = gpd.read_file(GEOMETRY_FILE)
gdf = gpd.read_file(MAID_FILE)

prepare_cells_and_points(df=df, h3_res=H3_RES, s2_res=S2_RES)

coords_poly = define_polygons_shapely(poly_path=GEOMETRY_FILE)
h3_poly = define_polygons_h3(poly_path=GEOMETRY_FILE, h3_res=H3_RES)
s2_poly = define_polygons_s2(poly_path=GEOMETRY_FILE, s2_res=S2_RES)

measure_match_coords(coords_poly=coords_poly)
measure_match_h3(h3_poly=h3_poly)
measure_match_s2(s2_poly=s2_poly)
measure_match_geopandas(gdf_poly=gdf_poly, gdf=gdf)


