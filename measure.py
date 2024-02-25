import cProfile

import pandas as pd

from tools import coord_matching, h3_matching, s2_matching
import memory_profiler
import time


def measure_match(method, poly_data, df, res):
    method_to_column_map = {
        "Coord": f"matching_polygon_{res}",
        "H3": f"matching_h3_{res}_cell",
        "S2": f"matching_s2_{res}_cell"
    }

    start_time = time.time()
    mem_usage = memory_profiler.memory_usage()
    matches = pd.DataFrame()

    if method == "Coord":
        matches = coord_matching(df=df, coord_poly=poly_data, res=res)
    elif method == "H3":
        matches = h3_matching(df=df, h3_poly=poly_data, res=res)
    elif method == "S2":
        matches = s2_matching(df=df, s2_poly=poly_data, res=res)
    column = method_to_column_map[method]

    end_time = time.time()
    total_time = end_time - start_time
    peak_memory = max(mem_usage)
    num_matches = matches[column].notna().sum()

    print(f"{method} Matches_{res}: {num_matches} out of {len(df)} points")
    print(f"Peak memory usage: {peak_memory:.2f} MB")
    print(f"Total runtime: {total_time:.4f} seconds\n")
    return matches


# def measure_match_coords_5(coords_poly, df, res):
#     p_coord_5 = cProfile.Profile()
#     p_coord_5.enable()
#     coord_matches_5 = coord_matching(df=df, coord_poly=coords_poly, res=res)
#     p_coord_5.disable()
#     p_coord_5.dump_stats(f"data/coord_5_stats")
#
#     num_matches = coord_matches_5[f"matching_polygon_5"].notna().sum()
#     print(f"Coord Matches_{res}: {num_matches} out of {len(df)} points")
#     return coord_matches_5
#
#
# def measure_match_h3_13(h3_poly, df, res):
#     p_h3_13 = cProfile.Profile()
#     p_h3_13.enable()
#     h3_13_matches = h3_matching(df=df, h3_poly=h3_poly, res=res)
#     p_h3_13.disable()
#     p_h3_13.dump_stats(f"data/h3_13_stats")
#
#     num_matches = h3_13_matches[f"matching_h3_13_cell"].notna().sum()
#     print(f"H3_{res} Matches: {num_matches} out of {len(df)} points")
#     return h3_13_matches
#
#
# def measure_match_h3_14(h3_poly, df, res):
#     p_h3_14 = cProfile.Profile()
#     p_h3_14.enable()
#     h3_14_matches = h3_matching(df=df, h3_poly=h3_poly, res=res)
#     p_h3_14.disable()
#     p_h3_14.dump_stats(f"data/h3_14_stats")
#
#     num_matches = h3_14_matches[f"matching_h3_14_cell"].notna().sum()
#     print(f"H3_{res} Matches: {num_matches} out of {len(df)} points")
#     return h3_14_matches
#
# def measure_match_s2_21(s2_poly, df, res):
#     p_s2_21 = cProfile.Profile()
#     p_s2_21.enable()
#     s2_21_matches = s2_matching(df=df, s2_poly=s2_poly, res=res)
#     p_s2_21.disable()
#     p_s2_21.dump_stats(f"data/s2_21_stats")
#
#     num_matches = s2_21_matches[f"matching_s2_21_cell"].notna().sum()
#     print(f"S2 Matches_{res}: {num_matches} out of {len(df)} points")
#     return s2_21_matches
#
#
# def measure_match_s2_22(s2_poly, df, res):
#     p_s2_22 = cProfile.Profile()
#     p_s2_22.enable()
#     s2_22_matches = s2_matching(df=df, s2_poly=s2_poly, res=res)
#     p_s2_22.disable()
#     p_s2_22.dump_stats(f"data/s2_22_stats")
#
#     num_matches = s2_22_matches[f"matching_s2_22_cell"].notna().sum()
#     print(f"S2_{res} Matches: {num_matches} out of {len(df)} points")
#     return s2_22_matches
