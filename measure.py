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