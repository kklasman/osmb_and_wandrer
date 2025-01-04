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
from geopy import distance
import numpy as np

st.set_page_config(layout='wide')

max_50_pct_color_scale = ['white', 'gold', 'red']

def create_template(data, col_names):
    template = ''
    for idx, name in enumerate(col_names):
        if name == 'State':
            template += "<b>State:</b> %{" + f"customdata[{data.columns.get_loc('State')}]" + "}<br>"

        elif name == 'County':
            template += "<b>County:</b> %{" + f"customdata[{data.columns.get_loc('County')}]" + "}<br>"

        elif name == 'ShortCounty':
            template += "<b>County:</b> %{" + f"customdata[{data.columns.get_loc('ShortCounty')}]" + "}<br>"

        elif name == 'Town':
            template += "<b>Town:</b> %{" + f"customdata[{data.columns.get_loc('Town')}]" + "}<br>"

        elif name == 'TotalMiles':
            template += "<b>Total Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalMiles')}]:,.2f" + "}<br>"

        elif name == 'ActualMiles':
            template += "<b>Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('ActualMiles')}]:,.2f" + "}<br>"

        elif name == 'MilesRidden':
            template += "<b>Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('MilesRidden')}]:,.2f" + "}<br>"

        elif name == 'ActualPct':
            template += "<b>Pct Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('ActualPct')}]:.2%" + "}<br>"

        elif name == 'Pct10':
            template += "<b>10% Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct10')}]:,.2f" + "}<br>"

        elif name == 'Pct25':
            template += "<b>25% Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct25')}]:,.2f" + "}<br>"

        elif name == 'Pct10Deficit':
            template += "<b>10% Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct10Deficit')}]:,.2f" + "}<br>"

        elif name == 'Pct25Deficit':
            template += "<b>25% Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct25Deficit')}]:,.2f" + "}<br>"

        elif name == 'TotalTowns':
            template += "<b>Total Towns:</b> %{" + f"customdata[{data.columns.get_loc('TotalTowns')}]" + "}<br>"

        elif name == 'TownsCycled':
            template += "<b>Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TownsCycled')}]" + "}<br>"

        elif name == 'TownsNotCycled':
            template += "<b>Towns Not Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TownsNotCycled')}]" + "}<br>"

        elif name == 'PctTownsCycled':
            template += "<b>Pct Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsCycled')}]:.2%" + "}"

        elif name == 'TownsAwarded':
            template += "<b>Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('TownsAwarded')}]" + "}<br>"

        elif name == 'PctTownsAwarded':
            template += "<b>Pct Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsAwarded')}" + "]:.2%}"

        else:
            print(f'Column {name} not found')

    template += "<extra></extra>"

    return template


def column_exists_case_insensitive(df, col_name):
    return col_name.lower() in [col.lower() for col in df.columns]

def rename_column_case_insensitive(df, old_col, new_col):
    """Rename a column in a DataFrame, ignoring case."""

    col_names = df.columns
    for col in col_names:
        if col.lower() == old_col.lower():
            df.rename(columns={col: new_col}, inplace=True)
            break


def calculate_mapbox_zoom_center(bounds) -> (float, dict):
    """calc zoom and center for plotly mapbox functions

    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434
    """

    # because we stick None to make separate lines...
    # lons = []
    # lats = []
    # lons.append(float(bounds.minx))
    # lons.append(float(bounds.maxx))
    # lats.append(float(bounds.miny))
    # lats.append(float(bounds.maxy))
    #
    # min_lat = min([l for l in lats if l])
    # max_lat = max([l for l in lats if l])
    # min_lon = min([l for l in lons if l])
    # max_lon = max([l for l in lons if l])

    min_lon = min(bounds.minx)
    max_lon = max(bounds.maxx)
    min_lat = min(bounds.miny)
    max_lat = max(bounds.maxy)

    y_range = distance.geodesic((min_lat, min_lon), (max_lat, min_lon)).kilometers
    x_range = distance.geodesic((min_lat, min_lon), (min_lat, max_lon)).kilometers

    # does this work across the international date line?
    center = dict(lat=(min_lat + max_lat) / 2, lon=(min_lon + max_lon) / 2)

    # figure out zoom
    bound_by_y = y_range > x_range
    if bound_by_y:
        # in mercator the world's height is ~20,000 km
        zoom = np.log2(20_000 / y_range)
    else:
        # in mercator the world's "width" is ~40,000km at the equator but shrinks as you near the poles
        circumference_at_latitude = 40_000 * np.cos(np.abs(center['lat']) * np.pi / 180)
        zoom = np.log2(circumference_at_latitude / x_range)

    return zoom, center

def create_county_map(source_osm_df, state):
    renamed_gdf = {}
    counties_gdf = {}
    state_gdf = {}
    data_value = ss['selected_datavalue_for_map']

    if column_exists_case_insensitive(source_osm_df, 'admin_level'):
        state_gdf = source_osm_df[osm_gdf['admin_level'] == 4.0]

        counties_gdf = source_osm_df[osm_gdf['admin_level'] == 6.0]
        counties_gdf.rename(columns={'name': 'County'}, inplace=True)
        if not counties_gdf.County.str.endswith(' County').all():
            counties_gdf['County'] += ' County'
    else:
        counties_gdf = source_osm_df.dissolve(by='COUNTY')
        counties_gdf.reset_index(inplace=True)
        counties_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        counties_gdf['County'] += ' County'
        state_gdf = counties_gdf.dissolve()

    renamed_gdf = counties_gdf.copy()

    wandrerer_df = get_wandrer_totals_for_counties_for_state(state)
    # print(wandrerer_df)
    merged_df = renamed_gdf.merge(wandrerer_df, on='County')
    merged_df.drop(['name_en', 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'
                    ,'label_node_id', 'label_node_lat','label_node_lng']
                   , axis=1, inplace=True, errors='ignore')

    final_df = merged_df.dropna()
    location_json = json.loads(final_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    final_df.drop(['tags', 'geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(final_df, ['ShortCounty', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(final_df[data_value].max()) if float(final_df[data_value].max()) > 0 else float(final_df['TotalMiles'].max())

    fig = go.Figure(go.Choroplethmapbox(
        customdata=final_df,
        geojson=location_json,
        featureidkey='properties.County',
        locations=final_df['County'],
        z=final_df[data_value],
        colorscale=max_50_pct_color_scale,
        zmin=0,
        zmax=z_max,
        hovertemplate=template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        marker_opacity=0.5,
        visible=True,
        colorbar_title=data_value
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Counties in {state}', x=0.5
                            , xanchor="center")
                            )
    fig.update_geos(fitbounds="geojson", visible=True)
    # st.plotly_chart(fig, use_container_width=True)
    return fig


def create_town_map(source_osm_df, state):
    county_gdf = {}
    state_gdf = {}
    data_value = ss['selected_datavalue_for_map']

    if column_exists_case_insensitive(source_osm_df, 'admin_level'):
        state_gdf = source_osm_df[osm_gdf['admin_level'] == 4.0]
        source_osm_df['admin_level'] = source_osm_df['admin_level'].astype(float)
        county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
        county_gdf['TotalMiles'] = 0
        county_gdf['ActualMiles'] = 0
        rename_column_case_insensitive(county_gdf, 'name', 'County')
        towns_gdf = source_osm_df[source_osm_df['admin_level'] > 6.0]
        rename_column_case_insensitive(towns_gdf, 'name', 'Town')
    elif column_exists_case_insensitive(source_osm_df, 'town'):
        rename_column_case_insensitive(source_osm_df, 'town', 'Town')
        towns_gdf = source_osm_df.copy()
        county_gdf = source_osm_df.dissolve(by='COUNTY')
        county_gdf.reset_index(inplace=True)
        county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        county_gdf['County'] += ' County'
        state_gdf = county_gdf.dissolve()
    else:
        print('Unexpected condition')
        print(towns_gdf.columns)

    wandrerer_df = get_wandrer_totals_for_towns_for_state(state)
    # print(wandrerer_df)
    town_merged_df = towns_gdf.merge(wandrerer_df, on='Town')
    town_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng'
                         ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')
    county_gdf.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng'
                         ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')
    location_json = json.loads(town_merged_df.to_json())
    county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    town_merged_df.drop(['tags', 'geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(town_merged_df, ['Town', 'ShortCounty', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())

    fig = go.Figure(go.Choroplethmapbox(
        customdata=town_merged_df,
        geojson=location_json,
        featureidkey='properties.Town',
        locations=town_merged_df['Town'],
        z=town_merged_df[data_value],
        # colorscale='ylorrd',
        colorscale=max_50_pct_color_scale,
        zmin=0,
        zmax=z_max,
        hovertemplate=template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        marker_opacity=0.5,
        # marker_line_width=2,
        visible=True,
        colorbar_title=data_value
    ))
    fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
                                          source=county_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )]);

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Towns in {state}', x=0.5
                            , xanchor="center")
                            )
    # fig.update_geos(fitbounds="locations", visible=True)
    # fig.update_geos(fitbounds="geojson", visible=True)
    # fig.show()
    # print(town_merged_df)
    return fig


def create_state_map(source_osm_df, state):
    renamed_gdf = {}
    county_gdf = {}
    source_osm_df['State'] = state
    data_value = ss['selected_datavalue_for_map']
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)
    if not column_exists_case_insensitive(source_osm_df, 'admin_level'):
        county_gdf = source_osm_df.dissolve(by='COUNTY')
        county_gdf.reset_index(inplace=True)
        county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        county_gdf['County'] += ' County'
    else:
        county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
        county_gdf.rename(columns={'name': 'County'}, inplace=True)

    if not county_gdf.County.str.endswith(' County').all():
        county_gdf['County'] += ' County'
    # county_gdf = counties_gdf.dissolve(by='County')
    # county_gdf.reset_index(inplace=True)

    wandrerer_df = get_wandrer_totals_for_state(state)
    # print(wandrerer_df)
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')
    state_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'admin_centre_node_id'
                         , 'admin_centre_node_lat', 'admin_centre_node_lng'
                         , 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng']
                         , axis=1, inplace=True, errors='ignore')
    location_json = json.loads(state_merged_df.to_json())
    county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['tags', 'geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(state_merged_df, ['State', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())

    fig = go.Figure(go.Choroplethmapbox(
        customdata=state_merged_df,
        geojson=location_json,
        featureidkey='properties.State',
        locations=state_merged_df['State'],
        z=state_merged_df[data_value],
        colorscale=max_50_pct_color_scale,
        zmin=0,
        zmax=z_max,
        marker_opacity=0.5,
        hovertemplate=template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # marker_line_width=2,
        visible=True,
        colorbar_title=data_value
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center=center)
    fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
                                          source=county_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )]);
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for State of {state}', x=0.5
                            , xanchor="center")
                            )
    return fig

def create_region_map(source_osm_df, region):
    renamed_gdf = {}
    county_gdf = {}
    # source_osm_df['State'] = state
    data_value = ss['selected_datavalue_for_map']
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)
    # if not column_exists_case_insensitive(source_osm_df, 'admin_level'):
    #     county_gdf = source_osm_df.dissolve(by='COUNTY')
    #     county_gdf.reset_index(inplace=True)
    #     county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
    #     county_gdf['County'] += ' County'
    # else:
    #     county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
    #     county_gdf.rename(columns={'name': 'County'}, inplace=True)
    #
    # if not county_gdf.County.str.endswith(' County').all():
    #     county_gdf['County'] += ' County'
    # # county_gdf = counties_gdf.dissolve(by='County')
    # # county_gdf.reset_index(inplace=True)

    wandrerer_df = get_wandrer_totals_for_states(state_gdf.State.to_list())
    # print(wandrerer_df)
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')
    state_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'admin_centre_node_id'
                         , 'admin_centre_node_lat', 'admin_centre_node_lng'
                         , 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng']
                         , axis=1, inplace=True, errors='ignore')
    location_json = json.loads(state_merged_df.to_json())
    # county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['tags', 'geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(state_merged_df, ['State', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())

    fig = go.Figure(go.Choroplethmapbox(
        customdata=state_merged_df,
        geojson=location_json,
        featureidkey='properties.State',
        locations=state_merged_df['State'],
        z=state_merged_df[data_value],
        colorscale=max_50_pct_color_scale,
        zmin=0,
        zmax=z_max,
        marker_opacity=0.5,
        hovertemplate=template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # marker_line_width=2,
        visible=True,
        colorbar_title=data_value
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center=center)
    # fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
    #                                       source=county_location_json,
    #                                       color='#303030',
    #                                       type='line',
    #                                       line=dict(width=1.5)
    #                                       )]);
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Region of {region}', x=0.5
                            , xanchor="center")
                            )
    return fig

def get_geojson_filenames():
    if 'geojson_files_dict' not in st.session_state:
        print("Getting geojson filenames from db.")
        query = f'''select State, geojson_filename from vw_state_geo_data
        where geojson_filename is not NULL
        order by State'''
        # print(query)
        df = execute_query(query)
        result = df.set_index('State')['geojson_filename'].to_dict()
        st.session_state.geojson_files_dict = result
        return result
    else:
        print("Getting geojson filenames from session_state.")
        return st.session_state.geojson_files_dict

def get_geojson_filenames_for_region(selected_region):
    if 'geojson_files_dict' not in st.session_state:
        print("Getting geojson filenames from db.")
        query = f'''select sm.subregion_name, st.arena_name as State, agd.geojson_filename 
            from subregion_mapping sm
            inner join arena st on st.arena_id = sm.child_arena_id
            inner join arena_geo_data agd on agd.arena_id = st.arena_id
            where agd.geojson_filename is not null
            and sm.subregion_name = {selected_region}
            order by State'''
        # print(query)
        df = execute_query(query)
        result = df.set_index('State')['geojson_filename'].to_dict()
        st.session_state.geojson_files_dict = result
        return result
    else:
        print("Getting geojson filenames from session_state.")
        return st.session_state.geojson_files_dict

def get_wandrer_totals_for_states(states):
    dfs = pd.DataFrame()

    for state in states:
        if dfs.empty:
            dfs = get_wandrer_totals_for_state(state)
        else:
            dfs = pd.concat([dfs, get_wandrer_totals_for_state(state)])

    return dfs

def get_wandrer_totals_for_state(state):
    query = f'''select Region, Country, State, sum(TotalMiles) as TotalMiles, sum(ActualMiles) as 'ActualMiles'
        , sum(ActualMiles)/sum(TotalMiles) as 'ActualPct'
        , CASE WHEN sum(Pct10Deficit) < 0 THEN 0 ELSE sum(Pct10Deficit) END as 'Pct10Deficit'
        , CASE WHEN sum(Pct25Deficit) < 0 THEN 0 ELSE sum(Pct25Deficit) END as 'Pct25Deficit'
    	from vw_county_aggregates
    	where State = "{state}"'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_counties_for_state(state):
    query = f'''select Region, Country, State, County
        , REPLACE(County, " County", "") as ShortCounty, StateArenaId, CountyArenaId
        ,TotalMiles, ActualPct, ActualMiles, "Pct10", "Pct25", "Pct50"
        , "Pct75", "Pct90", "awarded"
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , "Pct50Deficit", "Pct75Deficit"
        , "Pct90Deficit", "geometries_visible", "diagonal", "user_id"
		from vw_county_aggregates 
    	where State = "{state}"
    	order by County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_towns_for_state(state):
    query = f'''select fqtn.*
         , REPLACE(fqtn.County, " County", "") as ShortCounty
       , length as TotalMiles, "percentage" as ActualPct, "ActualLength" as ActualMiles, "Pct10", "Pct25", "Pct50"
        , "Pct75", "Pct90", "awarded"
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , "Pct50Deficit", "Pct75Deficit"
        , "Pct90Deficit", "geometries_visible", "diagonal", "user_id"
        from arena_badge town
        inner join fq_town_name fqtn on fqtn.arena_id = town.id
        where fqtn.state = "{state}"
        order by fqtn.region, fqtn.country, fqtn.state, fqtn.county, fqtn.town'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_subregions():
    query = f'''select sm.subregion_name, st.arena_name as State, agd.geojson_filename 
	from subregion_mapping sm
	inner join arena st on st.arena_id = sm.child_arena_id
	inner join arena_geo_data agd on agd.arena_id = st.arena_id
	where agd.geojson_filename is not null'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def execute_query(query):
    cwd = os.getcwd()
    # print(f'cwd = {cwd}')
    db_path = os.path.join(cwd, 'Lib', 'data', 'wandrer_2.0.db')
    # print(f'db_path {db_path} exists {os.path.exists(db_path)}')
    if not os.path.exists(db_path):
        # file lives in different location in development
        db_path = os.path.join(cwd, r'data', 'wandrer_2.0.db')
        # print(f'db_path {db_path} exists {os.path.exists(db_path)}')

    # filesize = os.path.getsize(db_path)
    # print(f'file size: {filesize}')
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

def make_state_selectbox_disable(b):
    st.session_state['state_selectbox'] = b

def enable_make_map():
    if 'selected_map_type' in st.session_state:
        # print(f"enable_make_map: {ss['select_map']}")
        if (ss['selected_state'] != None or ss['selected_region'] != None)\
            and ss['selected_map_type'] != None and ss['selected_datavalue_for_map'] != None:
            make_map_disable(False)
        else:
            make_map_disable(True)
            # st.session_state['make_map_disable'] = False
            # st.button('make_map_btn').disabled = Fale

def region_selected():
    if 'selected_region' not in st.session_state or ss['selected_region'] == 'All'  or ss['selected_region'] == None:
        make_state_selectbox_disable(False)
        return

    print(f"region_selected: {ss['selected_region']}")
    make_state_selectbox_disable(True)

def get_geojson_filename(selected_state):
    cwd = os.getcwd()
    file_name = geojson_files[selected_state]
    # file_path = os.path.join(cwd, r'data\10150\boundaries', file_name)
    file_path = os.path.join(cwd, 'Lib', 'data', 'boundaries', file_name)
    # print(f'file_path {file_path} exists {os.path.exists(file_path)}')
    if not os.path.exists(file_path):
        # file lives in a different folder in development
        file_path = os.path.join(cwd, r'data\boundaries', file_name)
        # print(f'file_path {file_path} exists {os.path.exists(file_path)}')

    # file_path = os.path.join(cwd, r'data\boundaries', file_name)
    # print(f'filepath = {file_path}')
    filesize = os.path.getsize(file_path)
    # print(f'file size: {filesize}')
    return file_path

def get_geopandas_df_for_state(selected_state):
    if selected_state not in st.session_state.gdfs.keys():
        print(f'Creating geopandas df for {selected_state}')
        file_path = get_geojson_filename(state_selectbox)
        gdf = gpd.read_file(f'{file_path}')
        # print(f'maptype_selectbox: {maptype_selectbox}')
        # print(gdf)
        st.session_state.gdfs[selected_state] = gdf
        return gdf
    else:
        print(f'Getting geopandas df for {selected_state} from session state')
        return st.session_state.gdfs[selected_state]

def get_geopandas_df_for_region(selected_region):
    if selected_region not in st.session_state.gdfs.keys():
        print(f'Creating geopandas df for {selected_region}')
        # file_path = get_geojson_filename(state_selectbox)
        # file_paths = wandrer_regions.geojson_filename.to_list()
        gdfs = gpd.GeoDataFrame()
        for index, row in wandrer_regions.iterrows():
            file_path = get_geojson_filename(row.State)
            if gdfs.empty:
                gdfs = gpd.read_file(f'{file_path}')
                gdfs['State'] = row.State
            else:
                gdf = gpd.read_file(f'{file_path}')
                gdf['State'] = row.State
                gdfs = pd.concat([gdfs, gdf])

        # print(f'maptype_selectbox: {maptype_selectbox}')
        # print(gdf)
        # st.session_state.gdfs[selected_state] = gdf
        # state_gdf = source_osm_df[osm_gdf['admin_level'] == 4.0]
        # state_gdfs = gdfs[gdfs['admin_level'] == 4.0]
        # print(state_gdfs)
        return gdfs
    else:
        print(f'Getting geopandas df for {selected_state} from session state')
        return st.session_state.gdfs[selected_state]

# ss

options = ['State', 'Counties', 'Towns']
geojson_files = get_geojson_filenames()
wandrer_regions = get_wandrer_subregions()
region_list = ['All'] + (wandrer_regions.subregion_name.unique().tolist())
data_values = ['TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit']
# geojson_files = get_geojson_files()

if 'gdfs' not in st.session_state:
    # Initialize geopandas df dictionary in session state.
    st.session_state.gdfs = {}

# exit_app = st.button('Exit', key='exit_btn')
# if exit_app:
#     time.sleep(5)
#     keyboard.press_and_release('ctrl+w')
#     # sys.exit()
#     pid = os.getpid()
#     p = psutil.Process(pid)
#     p.terminate()

# state_selectbox = st.selectbox('Select a location (US State):', geojson_files.keys(), key='select_state', index=None
#                                , on_change=update, args=('select_map',))

with st.sidebar:
    region_selectbox = st.selectbox('Select a region:', region_list, key='selected_region', index=None, on_change=region_selected())
    state_selectbox = st.selectbox('Select a location (US State):', geojson_files.keys(), key='selected_state', index=None)
    # preserve_map_selection = st.checkbox('Clear map type selection on state change', key='preserve_map_selection')
    maptype_selectbox = st.selectbox('Select a map type:', options, key='selected_map_type', index=None)
    datavalue_selectbox = st.selectbox('Select a data value', data_values, key='selected_datavalue_for_map', index=None, on_change=enable_make_map())
    make_map = st.button('Generate map', key='make_map_btn', disabled=st.session_state.get("make_map_disable", True))





if make_map:
    # print(f'os.getcwd = {os.getcwd()}')
    osm_gdf = {}
    fig = {}

    if region_selectbox:
        osm_gdf = get_geopandas_df_for_region(region_selectbox)
        fig = create_region_map(osm_gdf.copy(), region_selectbox)
    else:
        osm_gdf = get_geopandas_df_for_state(state_selectbox)
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

