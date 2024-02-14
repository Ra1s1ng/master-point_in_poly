import pandas
import pandas as pd
import geopandas as gpd
import s2.s2
import s2sphere

from tools import load_data, coord_matching, h3_matching, define_polygons_h3, define_polygons_shapely, \
    define_polygons_s2, s2_matching, prepare_cells_and_points
import cProfile
import timeit

N_AMOUNT = 100000
GEOMETRY_FILE = "data/polygon_100_ber.geojson"
MAID_FILE = "./data/athena_output_1m_be_de.csv"
H3_RES = 12
S2_RES = 22



def measure_match_coords(coords_poly):
    p_coord = cProfile.Profile()
    p_coord.enable()
    coord_matches = coord_matching(df=df, amount=N_AMOUNT, coord_poly=coords_poly)
    print(f"Coord Matches: {coord_matches}")
    print(f"Points inside of the polygon: {len(coord_matches)} out of {N_AMOUNT}\n")
    p_coord.disable()
    p_coord.dump_stats("data/coord_stats")


def measure_match_h3(h3_poly):
    p_h3 = cProfile.Profile()
    p_h3.enable()
    h3_matches = h3_matching(df=df, amount=N_AMOUNT, h3_poly=h3_poly)
    print(f"H3 Matches: {h3_matches}")
    print(f"Points inside of the polygon: {len(h3_matches)} out of {N_AMOUNT}\n")
    p_h3.disable()
    p_h3.dump_stats("data/h3_stats")


def measure_match_s2(s2_poly):
    p_s2 = cProfile.Profile()
    p_s2.enable()
    s2_matches = s2_matching(df=df, amount=N_AMOUNT, s2_poly=s2_poly)
    print(f"S2 Matches: {s2_matches}")
    print(f"Points inside of the polygon: {len(s2_matches)} out of {N_AMOUNT}")
    p_s2.disable()
    p_s2.dump_stats("data/s2_stats")


df = load_data(MAID_FILE)

gdf = gpd.read_file(GEOMETRY_FILE)

prepare_cells_and_points(df=df, h3_res=H3_RES, s2_res=S2_RES)

coords_poly = define_polygons_shapely(poly_path=GEOMETRY_FILE)
# h3_poly = define_polygons_h3(poly_path=GEOMETRY_FILE, h3_res=H3_RES)
# s2_poly = define_polygons_s2(poly_path=GEOMETRY_FILE, s2_res=S2_RES)

measure_match_coords(coords_poly=coords_poly)
# measure_match_h3(h3_poly=h3_poly)
# measure_match_s2(s2_poly=s2_poly)


