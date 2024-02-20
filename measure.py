import cProfile
from tools import coord_matching, h3_matching, s2_matching


def measure_match_coords_4(coords_poly, df, res):
    p_coord_4 = cProfile.Profile()
    p_coord_4.enable()
    coord_matches_4 = coord_matching(df=df, coord_poly=coords_poly, res=res)
    p_coord_4.disable()
    p_coord_4.dump_stats(f"data/coord_4_stats")

    num_matches = coord_matches_4[f"matching_polygon_4"].notna().sum()
    print(f"Coord Matches_{res}: {num_matches} out of {len(df)} points")
    device_matches = list(zip(coord_matches_4["device_id"], coord_matches_4[f"matching_polygon_4"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return coord_matches_4


def measure_match_coords_5(coords_poly, df, res):
    p_coord_5 = cProfile.Profile()
    p_coord_5.enable()
    coord_matches_5 = coord_matching(df=df, coord_poly=coords_poly, res=res)
    p_coord_5.disable()
    p_coord_5.dump_stats(f"data/coord_5_stats")

    num_matches = coord_matches_5[f"matching_polygon_5"].notna().sum()
    print(f"Coord Matches_{res}: {num_matches} out of {len(df)} points")
    device_matches = list(zip(coord_matches_5["device_id"], coord_matches_5[f"matching_polygon_5"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return coord_matches_5


def measure_match_h3_13(h3_poly, df, res):
    p_h3_13 = cProfile.Profile()
    p_h3_13.enable()
    h3_13_matches = h3_matching(df=df, h3_poly=h3_poly, res=res)
    p_h3_13.disable()
    p_h3_13.dump_stats(f"data/h3_13_stats")

    num_matches = h3_13_matches[f"matching_h3_13_cell"].notna().sum()
    print(f"H3_{res} Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(h3_13_matches["device_id"], h3_13_matches[f"matching_h3_13_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return h3_13_matches


def measure_match_h3_14(h3_poly, df, res):
    p_h3_14 = cProfile.Profile()
    p_h3_14.enable()
    h3_14_matches = h3_matching(df=df, h3_poly=h3_poly, res=res)
    p_h3_14.disable()
    p_h3_14.dump_stats(f"data/h3_14_stats")

    num_matches = h3_14_matches[f"matching_h3_14_cell"].notna().sum()
    print(f"H3_{res} Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(h3_14_matches["device_id"], h3_14_matches[f"matching_h3_14_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return h3_14_matches

def measure_match_s2_21(s2_poly, df, res):
    p_s2_21 = cProfile.Profile()
    p_s2_21.enable()
    s2_21_matches = s2_matching(df=df, s2_poly=s2_poly, res=res)
    p_s2_21.disable()
    p_s2_21.dump_stats(f"data/s2_21_stats")

    num_matches = s2_21_matches[f"matching_s2_21_cell"].notna().sum()
    print(f"S2 Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(s2_21_matches["device_id"], s2_21_matches[f"matching_s2_21_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return s2_21_matches


def measure_match_s2_22(s2_poly, df, res):
    p_s2_22 = cProfile.Profile()
    p_s2_22.enable()
    s2_22_matches = s2_matching(df=df, s2_poly=s2_poly, res=res)
    p_s2_22.disable()
    p_s2_22.dump_stats(f"data/s2_22_stats")

    num_matches = s2_22_matches[f"matching_s2_22_cell"].notna().sum()
    print(f"S2 Matches: {num_matches} out of {len(df)} points")
    device_matches = list(zip(s2_22_matches["device_id"], s2_22_matches[f"matching_s2_22_cell"]))
    print(f"Matching device IDs and polygons: {device_matches}\n")
    return s2_22_matches
