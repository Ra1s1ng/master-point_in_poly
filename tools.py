import pandas as pd
import shapely.geometry
import h3
import s2sphere
import babelgrid
import geopandas
import h3pandas


def load_data(path: str, amount: int):
    def get_s2_parent_cell_id(cell_object, s2_res):
        parent_cell_id = cell_object.parent(s2_res)
        return parent_cell_id.to_token()

    data = pd.read_csv(filepath_or_buffer=path, dtype={'location_context': 'string', 'carrier_name': 'string'})
    data = data.sample(n=amount, random_state=14)
    data["lat"] = pd.to_numeric(data["geo_location"].str.extract(r'latitude=(.*?),', expand=False), errors='coerce')
    data["lon"] = pd.to_numeric(data["geo_location"].str.extract(r'longitude=(.*?)}', expand=False), errors='coerce')
    data["lat_4"] = data["lat"].apply(lambda x: f"{x:.4f}")
    data["lon_4"] = data["lon"].apply(lambda x: f"{x:.4f}")

    data["s2_ll"] = data.apply(lambda row: s2sphere.LatLng.from_degrees(lat=row["lat"], lng=row["lon"]), axis=1)
    data["s2_object"] = data.apply(lambda row: s2sphere.CellId.from_lat_lng(row["s2_ll"]), axis=1)
    data["points_res_5"] = data.apply(lambda row: shapely.geometry.Point(row["lon"], row["lat"]), axis=1)
    data["points_res_4"] = data.apply(lambda row: shapely.geometry.Point(row["lon_4"], row["lat_4"]), axis=1)
    data["h3_res_14"] = data.apply(lambda row: h3.geo_to_h3(lat=row["lat"], lng=row["lon"], resolution=14), axis=1)
    data["h3_res_13"] = data.apply(lambda row: h3.h3_to_parent(h=row["h3_res_14"], res=13), axis=1)
    data["s2_res_22"] = data.apply(lambda row: get_s2_parent_cell_id(row["s2_object"], 22), axis=1)
    data["s2_res_21"] = data.apply(lambda row: get_s2_parent_cell_id(row["s2_object"], 21), axis=1)
    return data


def define_polygons_shapely(gdf_poly):
    shapely_polygons_dict = {}

    for i, geometry in enumerate(gdf_poly['geometry']):
        key = f"poly-{i}"
        shapely_polygons_dict[key] = geometry

    return shapely_polygons_dict


def define_polygons_h3(gdf_poly, h3_res: int):
    gdf_poly = gdf_poly.h3.polyfill(resolution=h3_res)
    h3_polygons_dict = {}

    for i, polyfill in enumerate(gdf_poly['h3_polyfill']):
        key = f"poly-{i}"
        h3_polygons_dict[key] = polyfill

    return h3_polygons_dict


def define_polygons_s2(gdf_poly, s2_res: int):
    s2_polygons_dict = {}

    def apply_s2(row):
        s2_geom = babelgrid.Babel("s2").polyfill(row["geometry"], resolution=s2_res)
        tile_ids = [tile.tile_id for tile in s2_geom]
        return tile_ids

    gdf_poly["s2_polyfill"] = gdf_poly.apply(lambda row: apply_s2(row), axis=1)
    for i, s2_polyfill in enumerate(gdf_poly["s2_polyfill"]):
        key = f"poly-{i}"
        s2_polygons_dict[key] = s2_polyfill

    return s2_polygons_dict


def coord_matching(df: pd.DataFrame, coord_poly: dict, res):
    df_copy = df.copy()
    df_copy[f"matching_polygon_{res}"] = pd.Series(dtype=str)

    def find_matching_polygon(row):
        for polygon_key, polygon in coord_poly.items():
            if row[f"points_res_{res}"].within(polygon):
                return polygon_key
        return None

    df_copy[f"matching_polygon_{res}"] = df_copy.apply(find_matching_polygon, axis=1)
    matching_df = df_copy[df_copy[f"matching_polygon_{res}"].notna()]
    return matching_df


def h3_matching(df: pd.DataFrame, h3_poly: dict, res):
    df_copy = df.copy()
    df_copy[f"matching_h3_{res}_cell"] = pd.Series(dtype=str)

    def find_h3_polygon(row):
        for polygon_key, poly_h3_values in h3_poly.items():
            if row[f"h3_res_{res}"] in poly_h3_values:
                return polygon_key
        return None

    df_copy[f"matching_h3_{res}_cell"] = df_copy.apply(find_h3_polygon, axis=1)
    matching_df = df_copy[df_copy[f"matching_h3_{res}_cell"].notna()]
    return matching_df


def s2_matching(df: pd.DataFrame, s2_poly: dict, res):
    df_copy = df.copy()
    df_copy[f"matching_s2_{res}_cell"] = pd.Series(dtype=str)

    def find_s2_polygon(row):
        for polygon_key, poly_s2_values in s2_poly.items():
            if row[f"s2_res_{res}"] in poly_s2_values:
                return polygon_key
        return None

    df_copy[f"matching_s2_{res}_cell"] = df_copy.apply(find_s2_polygon, axis=1)
    matching_df = df_copy[df_copy[f"matching_s2_{res}_cell"].notna()]
    return matching_df


def merge_dfs(df1, df2, df3=pd.DataFrame()):

    def intersection(df):
        method_columns = ["device_id",
                          "matching_polygon_4",
                          "matching_polygon_5",
                          "matching_h3_13_cell",
                          "matching_h3_14_cell",
                          "matching_s2_21_cell",
                          "matching_s2_22_cell"]

        columns = df.columns.tolist()
        common_columns = [value for value in columns if value in method_columns]
        return common_columns

    df1 = df1[intersection(df1)]
    df2 = df2[intersection(df2)]
    if not df3.empty:
        df3 = df3[intersection(df3)]

    if df3.empty:
        merge_1 = df2
    else:
        merge_1 = pd.merge(df2, df3, on="device_id", how="outer")

    merged_df = pd.merge(df1, merge_1, on="device_id", how="outer")
    # merged_df = merged_df[[col for col in df1.columns if col in method_columns]]
    return merged_df


def get_confusion_matrix(df):
    def map_classification(row, method):
        if row["matching_polygon_5"] == row[method]:
            return "TP"
        elif pd.isna(row["matching_polygon_5"]) and not pd.isna(row[method]):
            return "FP"
        elif pd.isna(row["matching_polygon_5"]) and pd.isna(row[method]):
            return "TN"
        elif not pd.isna(row["matching_polygon_5"]) and pd.isna(row[method]):
            return "FN"

    columns = [col for col in df.columns if col != 'device_id']

    for column in columns:
        df[f"conf_{column}"] = df.apply(
            lambda row: map_classification(row=row, method=f"{column}"),
            axis=1)
    return df


def calculate_metrics(df, n_amount):
    method_columns = [col for col in df.columns if col.startswith("conf_")]
    results = {}

    for method in method_columns:
        true_positives = (df[f"{method}"] == "TP").sum()
        false_positives = (df[f"{method}"] == "FP").sum()
        true_negatives = (df[f"{method}"] == "TN").sum() + (n_amount - len(df))
        # + all device_ids that are dropped from the original df.head(amount) to this df
        false_negatives = (df[f"{method}"] == "FN").sum()

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
        jaccard_index = true_positives / (true_positives + false_positives + false_negatives) if (true_positives + false_positives + false_negatives) else 0

        results[method] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "jaccard_index": jaccard_index,
            # "TP": true_positives,
            # "FP": false_positives,
            # "TN": true_negatives,
            # "FN": false_negatives
        }

    return pd.DataFrame(results).transpose()

