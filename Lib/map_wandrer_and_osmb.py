import sys
# import streamlit.cli
import geopandas as gpd
import plotly.graph_objects as go
# import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import sqlite3
import plotly.express as px
import streamlit as st
from streamlit import session_state as ss

def column_exists_case_insensitive(df, col_name):
    return col_name.lower() in [col.lower() for col in df.columns]

def rename_column_case_insensitive(df, old_col, new_col):
    """Rename a column in a DataFrame, ignoring case."""

    col_names = df.columns
    for col in col_names:
        if col.lower() == old_col.lower():
            df.rename(columns={col: new_col}, inplace=True)
            break


def create_county_map(source_osm_df, state):
    renamed_gdf = {}
    counties_gdf = {}

    if column_exists_case_insensitive(source_osm_df, 'admin_level'):
        counties_gdf = source_osm_df[osm_gdf['admin_level'] == 6.0]
        counties_gdf.rename(columns={'name': 'County'}, inplace=True)
        if not counties_gdf.County.str.endswith(' County').all():
            counties_gdf['County'] += ' County'
    else:
        counties_gdf = source_osm_df.dissolve(by='COUNTY')
        counties_gdf.reset_index(inplace=True)
        counties_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        counties_gdf['County'] += ' County'

    renamed_gdf = counties_gdf.copy()

    wandrerer_df = get_wandrer_totals_for_counties_for_state(state)
    # print(wandrerer_df)
    merged_df = renamed_gdf.merge(wandrerer_df, on='County')
    merged_df.drop(['name_en', 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'
                    ,'label_node_id', 'label_node_lat','label_node_lng']
                   , axis=1, inplace=True, errors='ignore')

    final_df = merged_df.dropna()
    lat = final_df.dissolve().centroid.iloc[0].y
    lon = final_df.dissolve().centroid.iloc[0].x
    print(f'lat: {lat} lon: {lon}')
    location_json = json.loads(final_df.to_json())
    zoom = 6
    fig = go.Figure(go.Choroplethmapbox(
        # customdata=final_df,
        geojson=location_json,
        featureidkey='properties.County',
        locations=final_df['County'],
        z=final_df['TotalMiles'],
        colorscale='ylorrd',
        # zmin=0,
        # zmax=z_max,
        marker_opacity=0.5,
        visible=True,
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center={"lat": lat, "lon": lon})
    fig = fig.update_layout(margin={"r": 10, "t": 5, "l": 1, "b": 1})
    fig.update_geos(fitbounds="locations", visible=True)
    return fig


def create_town_map(source_osm_df, state):
    if column_exists_case_insensitive(source_osm_df, 'admin_level'):
        source_osm_df['admin_level'] = source_osm_df['admin_level'].astype(float)
        towns_gdf = source_osm_df[source_osm_df['admin_level'] > 6.0]
        rename_column_case_insensitive(towns_gdf, 'name', 'Town')
    elif column_exists_case_insensitive(source_osm_df, 'town'):
        rename_column_case_insensitive(source_osm_df, 'town', 'Town')
        towns_gdf = source_osm_df.copy()
    else:
        print('Unexpected condition')
        print(towns_gdf.columns)

    wandrerer_df = get_wandrer_totals_for_towns_for_state(state)
    # print(wandrerer_df)
    town_merged_df = towns_gdf.merge(wandrerer_df, on='Town')
    town_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng'
                         ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')
    lat = town_merged_df.dissolve().centroid.iloc[0].y
    lon = town_merged_df.dissolve().centroid.iloc[0].x
    print(f'lat: {lat} lon: {lon}')
    # location_json = json.loads(final_df.geometry.to_json())
    location_json = json.loads(town_merged_df.to_json())
    zoom = 6
    fig = go.Figure(go.Choroplethmapbox(
        # customdata=final_df,
        geojson=location_json,
        featureidkey='properties.Town',
        locations=town_merged_df['Town'],
        z=town_merged_df['TotalMiles'],
        colorscale='ylorrd',
        # zmin=0,
        # zmax=z_max,
        marker_opacity=0.5,
        # marker_line_width=2,
        visible=True,
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center={"lat": lat, "lon": lon})
    fig = fig.update_layout(margin={"r": 10, "t": 5, "l": 1, "b": 1})
    # fig.update_geos(fitbounds="locations", visible=True)
    # fig.update_geos(fitbounds="geojson", visible=True)
    # fig.show()
    # print(town_merged_df)
    return fig


def create_state_map(source_osm_df, state):
    renamed_gdf = {}
    source_osm_df['State'] = state
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)

    wandrerer_df = get_wandrer_totals_for_state(state)
    # print(wandrerer_df)
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')
    state_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'admin_centre_node_id'
                         , 'admin_centre_node_lat', 'admin_centre_node_lng'
                         , 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng']
                         , axis=1, inplace=True, errors='ignore')
    lat = state_merged_df.dissolve().centroid.iloc[0].y
    lon = state_merged_df.dissolve().centroid.iloc[0].x
    # print(f'lat: {lat} lon: {lon}')
    location_json = json.loads(state_merged_df.to_json())
    zoom = 6
    fig = go.Figure(go.Choroplethmapbox(
        # customdata=final_df,
        geojson=location_json,
        featureidkey='properties.State',
        locations=state_merged_df['State'],
        z=state_merged_df['TotalMiles'],
        colorscale='ylorrd',
        # zmin=0,
        # zmax=z_max,
        marker_opacity=0.5,
        # marker_line_width=2,
        visible=True,
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center={"lat": lat, "lon": lon})
    fig = fig.update_layout(margin={"r": 10, "t": 5, "l": 1, "b": 1})
    return fig

def get_geojson_files_from_db():
    query = f'''select State, geojson_filename from vw_state_geo_data
	where geojson_filename is not NULL
	order by State'''
    # print(query)
    df = execute_query(query)
    result = df.set_index('State')['geojson_filename'].to_dict()
    return result

def get_wandrer_totals_for_state(state):
    query = f'''select Region, Country, State, sum(TotalMiles) as TotalMiles 
    	from vw_county_aggregates
    	where State = "{state}"'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_counties_for_state(state):
    query = f'''select * from vw_county_aggregates 
    	where State = "{state}"
    	order by County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_towns_for_state(state):
    query = f'''select fqtn.*
        , length as TotalMiles, "percentage" as ActualPct, "ActualLength" as ActualMiles, "Pct10", "Pct25", "Pct50"
        , "Pct75", "Pct90", "awarded", "Pct10Deficit", "Pct25Deficit", "Pct50Deficit", "Pct75Deficit"
        , "Pct90Deficit", "geometries_visible", "diagonal", "user_id"
        from arena_badge town
        inner join fq_town_name fqtn on fqtn.arena_id = town.id
        where fqtn.state = "{state}"
        order by fqtn.region, fqtn.country, fqtn.state, fqtn.county, fqtn.town'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def execute_query(query):
    cwd = os.getcwd()
    print(f'cwd = {cwd}')
    # db_path = os.path.join(cwd, r'data', 'wandrer_2.0.db')
    db_path = os.path.join(cwd, 'Lib', 'data', 'wandrer_2.0.db')
    print(f'db_path = {db_path}')
    filesize = os.path.getsize(db_path)
    print(f'file size: {filesize}')
    # print(f'db_path = {db_path}')

    try:
        conn = sqlite3.connect(db_path)
        # conn = sqlite3.connect(r'C:\Users\kk4si\PycharmProjects\osmb_and_wandrer\Lib\data\wandrer_2.0.db')
        # state = 'South Carolina'
        wandrerer_df = pd.read_sql_query(query, conn)
        return wandrerer_df
    except:
        print(f'Unable to open {db_path}')


def update(key, ):
    # print(f'update: ss[{key}] = {ss.select_state}')
    # print(f'update: preserve_map_selection = {ss.preserve_map_selection}')
    if key == 'select_map' and ss.preserve_map_selection:
        value = None
        ss[key] = value

def make_map_disable(b):
    st.session_state['make_map_disable'] = b

def enable_make_map():
    if 'select_map' in st.session_state:
        print(f"enable_make_map: {ss['select_map']}")
        if ss['select_state'] != None and ss['select_map'] != None:
            make_map_disable(False)
        else:
            make_map_disable(True)
            # st.session_state['make_map_disable'] = False
            # st.button('make_map_btn').disabled = Fale

# ss

options = ['State', 'Counties', 'Towns']
geojson_files = get_geojson_files_from_db()
# geojson_files = get_geojson_files()

# exit_app = st.button('Exit', key='exit_btn')
# if exit_app:
#     time.sleep(5)
#     keyboard.press_and_release('ctrl+w')
#     # sys.exit()
#     pid = os.getpid()
#     p = psutil.Process(pid)
#     p.terminate()

state_selectbox = st.selectbox('Select a location (US State):', geojson_files.keys(), key='select_state', index=None
                               , on_change=update, args=('select_map',))
preserve_map_selection = st.checkbox('Clear map type selection on state change', key='preserve_map_selection')
maptype_selectbox = st.selectbox('Select a map type:', options, key='select_map', index=None, on_change=enable_make_map())

make_map = st.button('Generate map', key='make_map_btn', disabled=st.session_state.get("make_map_disable", True))
print(f'state_selectbox: {state_selectbox}')
if make_map:
    # print(f'os.getcwd = {os.getcwd()}')
    cwd = os.getcwd()
    file_name = geojson_files[state_selectbox]
    # file_path = os.path.join(cwd, r'data\10150\boundaries', file_name)
    # file_path = os.path.join(cwd, r'data\boundaries', file_name)
    # file_path = os.path.join(cwd, r'data\boundaries', file_name)
    file_path = os.path.join(cwd, 'Lib', 'data', 'boundaries', file_name)
    print(f'filepath = {file_path}')
    filesize = os.path.getsize(file_path)
    print(f'file size: {filesize}')
    osm_gdf = gpd.read_file(f'{file_path}')
    print(f'maptype_selectbox: {maptype_selectbox}')
    print(osm_gdf)

    fig = {}
    match maptype_selectbox:
        case 'State':
            fig = create_state_map(osm_gdf.copy(), state_selectbox)
        case 'Counties':
            fig = create_county_map(osm_gdf.copy(), state_selectbox)
        case 'Towns':
            fig = create_town_map(osm_gdf.copy(), state_selectbox)
        # case _:
        #     st.write('Invalid selection')

    if fig:
        st.plotly_chart(fig)

# ss

