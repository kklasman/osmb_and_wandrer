import file_utils as fu
import geopandas as gpd
import json
import logging_functions as lf
import pandas as pd
from pympler import asizeof
from shapely.geometry import LineString

def bounds_to_linestrings(gdf):
    """
    Converts the bounds of each geometry in a GeoDataFrame to a LineString.

    Args:
        gdf: A GeoDataFrame.

    Returns:
        A GeoDataFrame with LineString geometries representing the bounds.
    """

    lines = []
    for index, row in gdf.iterrows():
        minx, miny, maxx, maxy = row.geometry.bounds
        # line = LineString([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])
        line = LineString([(maxx, miny), (minx, maxy)])
        lines.append(line)

    return gpd.GeoDataFrame(geometry=lines, crs=gdf.crs)


def column_exists_case_insensitive(df, col_name):
    return col_name.lower() in [col.lower() for col in df.columns]


def rename_column_case_insensitive(df, old_col, new_col):
    """Rename a column in a DataFrame, ignoring case."""

    col_names = df.columns
    for col in col_names:
        if col.lower() == old_col.lower():
            df.rename(columns={col: new_col}, inplace=True)
            break


def convert_bounds_to_linestrings(source_gdf):
    # Convert bounds to LineStrings
    line_gdf = bounds_to_linestrings(source_gdf)
    # data = line_gdf.to_json()
    data = json.loads(line_gdf.to_json())
    # create empty new column
    source_gdf['diagonal'] = ''
    for index, item in enumerate(data['features']):
        # print(f"Index: {index}, geometry: {item['geometry']}")
        s = str(item['geometry']).replace("\'", "\"")
        source_gdf.at[index, 'diagonal'] = str(s)
    # for item in data['features']:
    #     print(item['geometry'])


def get_geopandas_df_for_state(selected_state, file_path=None):
    # if selected_state not in st.session_state.gdfs.keys():
        if file_path is None:
            file_path = fu.get_geojson_filename(selected_state)
            if len(file_path) == 0:
                return gpd.GeoDataFrame(),  -1

        gdf = gpd.read_file(f'{file_path}')
        if 'id' in gdf.columns:
            if 'osm_id' not in gdf.columns:
                gdf['osm_id'] = None

            gdf['osm_id'] = gdf['osm_id'].fillna(gdf['id'].str.split('/').str[-1]) if '/' in gdf['id'] else gdf['id']
            # gdf['osm_id'] = gdf['osm_id'].fillna(gdf['id'].str.split('/').str[-1])
        else:
            lf.logger.info(f'id column missing in {selected_state} geojson')

        convert_bounds_to_linestrings(gdf)
        # st.session_state.gdfs[selected_state] = gdf
        # if not column_exists_case_insensitive(gdf, 'normalized'):
        #     county_gdf, gdf = normalize_geojson(selected_state, gdf)

        columns_to_drop = gdf.select_dtypes(include=['datetime64']).columns
        gdf.drop(columns=columns_to_drop, axis=1, inplace=True)

        current_gdf_size = asizeof.asizeof(gdf)
        lf.logger.info(f'Creating geopandas df for {selected_state}, size: {current_gdf_size:,} bytes from {file_path}')
        return gdf, current_gdf_size


def get_geopandas_df_for_region(state_list):
    # if not set(selected_region).issubset(set(st.session_state.gdfs.keys())):
    #     logger.info(f'Creating geopandas df for {selected_region}')
    # file_path = get_geojson_filename(state_selectbox)
    # file_paths = wandrer_regions.geojson_filename.to_list()
    gdfs = gpd.GeoDataFrame()
    county_gdfs = gpd.GeoDataFrame()
    total_gdf_size = 0
    for state in state_list:
        gdf, current_gdf_size = get_geopandas_df_for_state(state)
        if gdf.empty:
            continue

        total_gdf_size += current_gdf_size

        # if not column_exists_case_insensitive(gdf, 'normalized'):
        #     county_gdf, gdf = normalize_geojson(state, gdf)
        # else:
        #     county_gdf = create_county_gdf(gdf)

        if gdfs.empty:
            # gdfs = gpd.read_file(f'{file_path}')
            gdfs = gdf
            # county_gdfs = county_gdf
            # gdfs['State'] = state
        else:
            gdfs = pd.concat([gdfs, gdf])
            # county_gdfs = pd.concat([county_gdfs, county_gdf])

    lf.logger.info(f'Total size for {len(state_list)} states: {total_gdf_size:,} bytes')

    # if county_gdfs.empty:
    #     return gdfs
    # else:
    #     return gdfs, county_gdfs
    return gdfs
