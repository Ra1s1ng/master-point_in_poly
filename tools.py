import json

import pandas as pd
import shapely.geometry
import h3
import geopandas as gpd
import s2, s2sphere

S2_RES = 22


def load_data(path: str, amount: int):
    data = pd.read_csv(filepath_or_buffer=path, dtype={'location_context': 'string', 'carrier_name': 'string'})
    data = data.head(amount)
    data["lat"] = pd.to_numeric(data["geo_location"].str.extract(r'latitude=(.*?),', expand=False), errors='coerce')
    data["lon"] = pd.to_numeric(data["geo_location"].str.extract(r'longitude=(.*?)}', expand=False), errors='coerce')
    # data["lat"] = data["lat"].apply(lambda x: f"{x:.4f}")
    # data["lon"] = data["lon"].apply(lambda x: f"{x:.4f}")
    data["h3_index_str"] = data.apply(lambda row: h3.h3_to_string(row["h3_index"]), axis=1)
    data["s2_object"] = data.apply(lambda row: s2sphere.CellId(row["s2_cell_id"]), axis=1)
    data["h3_manual_res_12"] = data.apply(lambda row: h3.geo_to_h3(lat=row["lat"], lng=row["lon"], resolution=12), axis=1)
    return data


def define_polygons_shapely(poly_path: str):
    gdf = gpd.read_file(poly_path)
    shapely_polygons_dict = {}

    for i, geometry in enumerate(gdf['geometry']):
        key = f"poly-{i}"
        shapely_polygons_dict[key] = geometry

    return shapely_polygons_dict


def define_polygons_h3(poly_path: str, h3_res: int):
    h3_polygons_dict = {}
    n = 0

    with open(poly_path) as poly_file:
        poly_data = json.load(poly_file)
        for feature in poly_data.get('features'):
            coordinates = feature['geometry']
            h3_poly = h3.polyfill(coordinates, res=h3_res)
            h3_polygons_dict[f"Poly-{n}"] = h3_poly
            n += 1

    return h3_polygons_dict


def define_polygons_s2(poly_path: str, s2_res: int):
    s2_polygons_dict = {}
    n = 0

    with open(poly_path) as poly_file:
        poly_data = json.load(poly_file)
        for feature in poly_data.get('features'):
            geometry = feature["geometry"]
            for ring in geometry["coordinates"]:
                cell_ids = []
                for lat, lng in ring:
                    ll = s2sphere.LatLng.from_degrees(lat, lng)
                    cell = s2sphere.Cell.from_lat_lng(ll)
                    parent_cell_id = cell.id().parent(s2_res)
                    cell_ids.append(parent_cell_id)
                s2_polygons_dict[f"Polygon-{n}"] = cell_ids
                n += 1
    return s2_polygons_dict


def prepare_cells_and_points(df: pd.DataFrame, s2_res: int, h3_res: int):
    df["points"] = df.apply(lambda row: shapely.geometry.Point(row["lon"], row["lat"]), axis=1)
    df["h3_parent_to_maid"] = df.apply(lambda row: h3.h3_to_parent(h=row["h3_index_str"], res=h3_res), axis=1)
    df["s2_parent_to_maid"] = df.apply(lambda row: s2sphere.CellId.parent(row["s2_object"], s2_res), axis=1)
    return df


def coord_matching(df: pd.DataFrame, coord_poly: dict):
    df["matching_polygon"] = pd.Series(dtype=str)

    def find_matching_polygon(row):
        for polygon_key, polygon in coord_poly.items():
            if row[f"points"].within(polygon):
                return polygon_key
        return None

    df["matching_polygon"] = df.apply(find_matching_polygon, axis=1)
    matching_df = df[df["matching_polygon"].notna()]
    return matching_df


def h3_matching(df: pd.DataFrame, h3_poly: dict):
    df["matching_h3_cell"] = pd.Series(dtype=str)

    def find_h3_polygon(row):
        for polygon_key, poly_h3_values in h3_poly.items():
            if row["h3_parent_to_maid"] in poly_h3_values:
                return polygon_key
        return None

    df["matching_h3_cell"] = df.apply(find_h3_polygon, axis=1)
    matching_df = df[df["matching_h3_cell"].notna()]
    return matching_df


def s2_matching(df: pd.DataFrame, s2_poly: dict):
    df["matching_s2_cell"] = pd.Series(dtype=str)

    def find_s2_polygon(row):
        for polygon_key, poly_s2_values in s2_poly.items():
            if row["s2_parent_to_maid"] in poly_s2_values:
                return polygon_key
        return None

    df["matching_h3_cell"] = df.apply(find_s2_polygon, axis=1)
    matching_df = df[df["matching_s2_cell"].notna()]
    return matching_df



