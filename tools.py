import json

import pandas as pd
import shapely.geometry
import h3
import geopandas as gpd
import s2, s2sphere

S2_RES = 22


def load_data(path: str):
    data = pd.read_csv(filepath_or_buffer=path, dtype={'location_context': 'string', 'carrier_name': 'string'})
    data["lat"] = data["geo_location"].str.extract(r'latitude=(.*?),')
    data["lon"] = data["geo_location"].str.extract(r'longitude=(.*?)}')
    data["h3_index_str"] = data.apply(lambda row: h3.h3_to_string(row["h3_index"]), axis=1)
    data["s2_object"] = data.apply(lambda row: s2sphere.CellId(row["s2_cell_id"]), axis=1)
    data["h3_manual_res_12"] = data.apply(lambda row: h3.geo_to_h3(lat=float(row["lat"]), lng=float(row["lon"]), resolution=12), axis=1)
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


def coord_matching(df: pd.DataFrame, amount: int, coord_poly: dict):
    point_in_polygon = {}
    matches = []

    for row in df.head(amount).itertuples():
        device_id = row.device_id

        matched_polygon = None
        for polygon_key, polygon in coord_poly.items():
            if row.points.within(polygon):
                matched_polygon = polygon_key
                break
        if matched_polygon is not None:
            point_in_polygon[device_id] = matched_polygon

    for point in df["points"].head(amount):
        for key in coord_poly:
            if point.within(coord_poly[key]):
                matches.append(key)
                break

    return point_in_polygon, matches


def h3_matching(df: pd.DataFrame, amount: int, h3_poly: dict):
    h3_matches = {}
    matches = df["h3_parent_to_maid"].head(amount).isin(h3_poly.values())

    for index, row in df[matches].iterrows():
        device_id = row["device_id"]
        for polygon_key, h3_values in h3_poly.items():
            if row["h3_parent_to_maid"] in h3_values:
                h3_matches[device_id] = polygon_key
                break

    return h3_matches


def s2_matching(df: pd.DataFrame, amount: int, s2_poly: dict):
    s2_matches = []

    for point in df["s2_parent_to_maid"].head(amount):
        for key in s2_poly:
            if point in s2_poly[key]:
                s2_matches.append(key)
                break
    return s2_matches



