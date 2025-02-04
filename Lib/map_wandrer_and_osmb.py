import string
import sys
import geopandas as gpd
import plotly.graph_objects as go
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

        elif name == 'COUNTY':
            template += "<b>County:</b> %{" + f"customdata[{data.columns.get_loc('COUNTY')}]" + "}<br>"

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

    county_gdf = source_osm_df.dissolve(by='County')
    county_gdf.reset_index(inplace=True)
    county_gdf['County'] = county_gdf['County'].str.title()

    state_gdf = source_osm_df.dissolve(by='State')
    state_boundary_json = json.loads(state_gdf.to_json())

    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)

    state_list = []
    state_list.append(state)
    wandrerer_df = get_wandrer_totals_for_counties_for_states(state_list)
    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)

    # print(wandrerer_df)
    merged_df = county_gdf.merge(wandrerer_df, on=['State','County'])
    merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
    final_df = merged_df.drop(['County'], axis=1, errors='ignore')
    final_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    location_json = json.loads(merged_df.to_json())
    merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(merged_df, ['County', 'TotalTowns', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(merged_df[data_value].max()) if float(merged_df[data_value].max()) > 0 else float(merged_df['TotalMiles'].max())

    st.session_state['map_gdf'] = merged_df
    fig = go.Figure(go.Choroplethmapbox(
        customdata=merged_df,
        geojson=location_json,
        featureidkey='properties.County',
        locations=merged_df['County'],
        z=merged_df[data_value],
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

    fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
                                          source=state_boundary_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )])

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Counties in {state}', x=0.5
                            , xanchor="center")
                            )
    fig.update_geos(fitbounds="geojson", visible=True)
    return fig


def create_town_map(town_gdf, state):
    county_gdf = town_gdf.dissolve('County')
    county_gdf.reset_index(inplace=True)
    state_gdf = county_gdf.dissolve('State')
    state_gdf.reset_index(inplace=True)
    data_value = ss['selected_datavalue_for_map']


    state_list = []
    state_list.append(state)
    wandrerer_df = get_wandrer_totals_for_towns_for_state(state_list)
    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)
    # wandrerer_df['lcase_town'] = wandrerer_df['Town'].str.lower() # required for merge with Wandrer data
    #
    # wandrer_diffs = wandrerer_df[~wandrerer_df['Town'].isin(town_gdf['Town'])]
    # wandrer_diffs_no_dupes = wandrer_diffs.drop_duplicates()
    # # wandrer_diffs_no_dupes_2 = wandrer_diffs.drop_duplicates(subset=['arena_id'])
    #
    # filter_list = ['State Park', 'Appalachian Trail', 'National Park']
    # search_str = '|'.join(filter_list)
    # wandrer_diffs_filtered = wandrer_diffs[~wandrer_diffs['Town'].str.contains(search_str)]
    # if len(wandrer_diffs_filtered) > 0:
    #     wandrer_diffs_filtered['DataSource'] = 'Wandrer'
    #     selected_columns = ['DataSource', 'County', 'Town']
    #     wandrer_diffs_filtered[selected_columns].to_csv(f'{state}-Wandrer-Missing-Town.csv', index=False)
    # #
    # json_diffs = town_gdf[~town_gdf['Town'].isin(wandrerer_df['Town'])]
    # if len(json_diffs) > 0:
    #     json_diffs['DataSource'] = 'json'
    #     selected_columns = ['DataSource', 'Town']
    #     json_diffs[selected_columns].to_csv(f'{state}-json-Missing-Town.csv', index=False)

    # print(wandrerer_df)
    town_merged_df = town_gdf.merge(wandrerer_df, on=['State','County','Town','long_name'])

    location_json = json.loads(town_merged_df.to_json())
    county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    town_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # town_merged_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    template = create_template(town_merged_df, ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())

    st.session_state['map_gdf'] = town_merged_df
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

    return fig

def create_region_by_town_map(source_osm_df, region):
    county_gdf = {}
    state_gdf = {}
    # data_value = ss['selected_datavalue_for_map']

    source_osm_df.drop(['tags'], axis=1, inplace=True, errors='ignore')
    state_list = source_osm_df['State'].unique().tolist()
    for item in state_list:
        print(f'{item=}')
        # location_json = json.loads(town_merged_df.to_json())
        # with open("location.json", "w") as f:
        #     json.dump(location_json, f, indent=4)

    if column_exists_case_insensitive(source_osm_df, 'admin_level'):
        state_gdf = source_osm_df[source_osm_df['admin_level'] == 4.0]
        source_osm_df['admin_level'] = source_osm_df['admin_level'].astype(float)
        county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
        county_gdf['TotalMiles'] = 0
        county_gdf['ActualMiles'] = 0
        rename_column_case_insensitive(county_gdf, 'name', 'County')
        towns_unsorted_gdf = source_osm_df[source_osm_df['admin_level'] > 6.0]
        # rename_column_case_insensitive(towns_gdf, 'name', 'Town')
    elif column_exists_case_insensitive(source_osm_df, 'town'):
        rename_column_case_insensitive(source_osm_df, 'town', 'Town')
        towns_unsorted_gdf = source_osm_df.copy()
        county_gdf = source_osm_df.dissolve(by='County')
        county_gdf.reset_index(inplace=True)
        # county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        county_gdf['County'] += ' County'
        state_gdf = county_gdf.dissolve(by='State')
        state_gdf.reset_index(inplace=True)
    else:
        print('Unexpected condition')
        # print(towns_gdf.columns)
        return

    towns_gdf = towns_unsorted_gdf.sort_values(by='long_name')
    # Drop non columns from Vermont geojson file
    towns_gdf['lcase_town'] = towns_gdf['Town'].str.lower() # required for merge with Wandrer data
    # towns_gdf['long_name'] = towns_gdf['Town'].str.lower() # required for merge with Wandrer data
    towns_gdf.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')

    wandrerer_df = get_wandrer_totals_for_towns_for_state(state_gdf['State'].to_list())
    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)
    wandrerer_df['lcase_town'] = wandrerer_df['Town'].str.lower() # required for merge with Wandrer data

    # wandrer_diffs = wandrerer_df[~wandrerer_df['Town'].isin(towns_gdf['Town'])]
    # wandrer_diffs_no_dupes = wandrer_diffs.drop_duplicates()
    # wandrer_diffs_no_dupes_2 = wandrer_diffs.drop_duplicates(subset=['arena_id'])
    #
    # filter_list = ['State Park', 'Appalachian Trail', 'National Park']
    # search_str = '|'.join(filter_list)
    # wandrer_diffs_filtered = wandrer_diffs[~wandrer_diffs['Town'].str.contains(search_str)]
    # if len(wandrer_diffs_filtered) > 0:
    #     wandrer_diffs_filtered['DataSource'] = 'Wandrer'
    #     selected_columns = ['DataSource', 'County', 'Town']
    #     wandrer_diffs_filtered[selected_columns].to_csv(f'{state}-Wandrer-Missing-Town.csv', index=False)
    #
    # json_diffs = towns_gdf[~towns_gdf['Town'].isin(wandrerer_df['Town'])]
    # if len(json_diffs) > 0:
    #     json_diffs['DataSource'] = 'json'
    #     selected_columns = ['DataSource', 'Town']
    #     json_diffs[selected_columns].to_csv(f'{state}-json-Missing-Town.csv', index=False)

    # print(wandrerer_df)
    town_merged_df = towns_gdf.merge(wandrerer_df, on=['long_name','lcase_town','State','Town','County'])

    if column_exists_case_insensitive(town_merged_df, 'Town_x'):
        town_merged_df.rename(columns={'Town_x': 'Town'}, inplace=True)
    if column_exists_case_insensitive(town_merged_df, 'County_x'):
        town_merged_df.rename(columns={'County_x': 'County'}, inplace=True)
    if column_exists_case_insensitive(town_merged_df, 'State_x'):
        town_merged_df.rename(columns={'State_x': 'State'}, inplace=True)

    town_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'Town_y'
                            ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')

    county_gdf.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng'
                        ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')
    # location_json = json.loads(town_merged_df.to_json())
    # county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    # town_merged_df.drop(['tags', 'geometry','lcase_town','arena_id','County','COUNTY'], axis=1, inplace=True, errors='ignore')
    # town_merged_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())
    location_gdf = town_merged_df.drop(['TotalMiles','ActualPct','ActualMiles','Pct10','Pct25','Pct50','Pct75','Pct90','awarded'
                                           ,'Pct10Deficit','Pct25Deficit','Pct50Deficit','Pct75Deficit','Pct90Deficit']
                                       , axis=1, errors='ignore')
    location_json = json.loads(location_gdf.to_json())
    with open("location.json", "w") as f:
        json.dump(location_json, f, indent=4)
    county_location_json = json.loads(county_gdf.to_json())
    town_merged_df.drop(['tags','lcase_town','arena_id','COUNTY','geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(town_merged_df, ['State','County','Town','TotalMiles','ActualMiles','ActualPct','Pct10Deficit','Pct25Deficit'])

    st.session_state['map_gdf'] = town_merged_df
    fig = go.Figure(go.Choroplethmapbox(
        customdata=town_merged_df,
        geojson=location_json,
        featureidkey='properties.long_name',
        locations=town_merged_df['long_name'],
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
                            , title=dict(text=f'{data_value} for Towns in {region}', x=0.5
                                         , xanchor="center")
                            )

    return fig

def create_state_map(source_osm_df, state):
    renamed_gdf = {}
    source_osm_df['State'] = state
    data_value = ss['selected_datavalue_for_map']
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)
    # county_gdf = source_osm_df.dissolve(by='County')
    # county_gdf.reset_index(inplace=True)
    # county_gdf = create_county_gdf(source_osm_df)

    wandrerer_df = get_wandrer_totals_for_state(state)
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')
    # state_merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
    state_merged_df.drop(['County','Town'], axis=1, inplace=True, errors='ignore')
    location_json = json.loads(state_merged_df.to_json())
    # county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    template = create_template(state_merged_df, ['State', 'TotalTowns', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    data_value = data_value.replace(' > 1', '')
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())

    st.session_state['map_gdf'] = state_merged_df
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
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for State of {state}', x=0.5
                            , xanchor="center")
                            )
    return fig


def create_county_gdf(source_osm_df):
    if not column_exists_case_insensitive(source_osm_df, 'admin_level'):
        county_gdf = source_osm_df.dissolve(by='County')
        county_gdf.reset_index(inplace=True)
        # county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
        # county_gdf['long_county'] = county_gdf['County'] + ' County'
    else:
        county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
        county_gdf.rename(columns={'name': 'County'}, inplace=True)
    # if not county_gdf.County.str.endswith(' County').all():
    # if not column_exists_case_insensitive(county_gdf, 'long_county'):
    #     # county_gdf['County'] += ' County'
    #     county_gdf['long_county'] = county_gdf['County'] + ' County'
    #     state = county_gdf['State'].unique()[0]
    #     outfile = f'{state}_location.json'
    #     gdf.to_file(outfile, driver="GeoJSON")

    county_gdf['County'] = county_gdf['County'].str.title() # required for merge with Wandrer data
    return county_gdf

def create_region_map(source_osm_df, region):
    renamed_gdf = {}
    county_gdf = {}
    # source_osm_df['State'] = state
    data_value = ss['selected_datavalue_for_map']
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)

    wandrerer_df = get_wandrer_totals_for_states(state_gdf.State.to_list())
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')

    state_merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')

    location_json = json.loads(state_merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['tags', 'geometry','COUNTY','name','Town'], axis=1, inplace=True, errors='ignore')
    template = create_template(state_merged_df, ['State', 'TotalTowns', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())
    st.session_state['map_gdf'] = state_merged_df

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

    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Region of {region}', x=0.5
                            , xanchor="center")
                            )
    return fig

def create_region_by_county_map(source_osm_df, region):
    renamed_gdf = {}
    county_gdf = {}
    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)

    wandrerer_df = get_wandrer_totals_for_counties_for_states(state_gdf.State.to_list())

    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)

    merged_df = source_osm_df.merge(wandrerer_df, on=['State', 'County'])
    merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
    state_location_json = json.loads(state_gdf.to_json())
    location_json = json.loads(merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    # merged_df.drop(['tags', 'geometry','Town','County'], axis=1, inplace=True, errors='ignore')
    merged_df.drop(['tags', 'geometry'], axis=1, inplace=True, errors='ignore')
    # merged_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    template = create_template(merged_df, ['State', 'County', 'TotalTowns', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(merged_df[data_value].max()) if float(merged_df[data_value].max()) > 0 else float(merged_df['TotalMiles'].max())
    z_min =  1000 if data_value == 'TotalMiles' else 0

    st.session_state['map_gdf'] = merged_df

    fig = go.Figure(go.Choroplethmapbox(
        customdata=merged_df,
        geojson=location_json,
        featureidkey='properties.long_name',
        locations=merged_df['long_name'],
        z=merged_df[data_value],
        colorscale=max_50_pct_color_scale,
        zmin=z_min,
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
                                          source=state_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )]);
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} by County for Region of {region}', x=0.5
                            , xanchor="center")
                            )
    return fig


def filter_wandrerer_df(wandrerer_df):
    selected_data_value = ss['selected_datavalue_for_map']
    data_value = ''
    if selected_data_value == 'ActualMiles > 1':
        wandrerer_df = wandrerer_df.loc[wandrerer_df['ActualMiles'] > 1]
        data_value = 'ActualMiles'
    else:
        data_value = selected_data_value

    return data_value, wandrerer_df


def get_unneeded_column_names():
    return ['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'admin_centre_node_id'
        , 'admin_centre_node_lat', 'admin_centre_node_lng'
        , 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'
        , 'NAME', 'MCD', 'KEY', 'DCF_OFFICE', 'DCF_REGION'
        , 'FIPS6', 'TOWN', 'TOWNNAMEMC', 'TOWNGEOID', 'SqMi'
        , 'OBJECTID', 'CNTY', 'CNTYGEOID', 'LAND'
        , 'osm_id', 'boundary', 'NAME', 'MCD', 'KEY', 'DCF_OFFICE', 'DCF_REGION'
        , 'GEOCODE', 'GEOCODENUM', 'CNTYCODE', 'TAG', 'ISLAND', 'CIREG', 'LURC', 'BAXTER', 'ISLANDID', 'TYPE'
        , 'DOT_REGNUM', 'DOT_REGION', 'GlobalID', 'created_user'
        , 'created_date', 'last_edited_user', 'last_edited_date','CountyArenaId','StateArenaId'
            ]


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
    query = f'''select Region, Country, State, sum(TotalTowns) as TotalTowns, sum(TotalMiles) as TotalMiles
        , sum(ActualMiles) as 'ActualMiles', sum(ActualMiles)/sum(TotalMiles) as 'ActualPct'
        , CASE WHEN sum(Pct10Deficit) < 0 THEN 0 ELSE sum(Pct10Deficit) END as 'Pct10Deficit'
        , CASE WHEN sum(Pct25Deficit) < 0 THEN 0 ELSE sum(Pct25Deficit) END as 'Pct25Deficit'
    	from vw_county_aggregates
    	where State = "{state}"'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_counties_for_states(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select Region, Country, State, County as LongCounty
        , REPLACE(County, " County", "") as County, StateArenaId, CountyArenaId
        , TotalTowns,TotalMiles, ActualPct, ActualMiles, Pct10, Pct25, Pct50, Pct75
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , Pct50Deficit, Pct75Deficit, Pct90Deficit
		from vw_county_aggregates 
    	where State in {states_in_str}
    	order by State, County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_counties_for_state(state):
    query = f'''select Region, Country, State, County
        , REPLACE(County, " County", "") as ShortCounty, StateArenaId, CountyArenaId
        , TotalTowns,TotalMiles, ActualPct, ActualMiles, Pct10, Pct25, Pct50, Pct75
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , Pct50Deficit, Pct75Deficit, Pct90Deficit
		from vw_county_aggregates 
    	where State = "{state}"
    	order by County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def parameterize_SQL_in_statement(items):
    return f"""('{"', '".join(items)}')"""

def get_wandrer_totals_for_towns_for_state(states):
    in_statement = parameterize_SQL_in_statement(states)
    query = f'''select distinct fqtn.Region, fqtn.Country, fqtn.State, fqtn.County as LongCounty
         , REPLACE(fqtn.County, " County", "") as County, fqtn.Town, fqtn.long_name
       , round(length, 7) as TotalMiles, round(percentage, 7) as ActualPct, round(ActualLength, 7) as ActualMiles
	   , round(Pct10, 7) as Pct10, round(Pct25, 7) as Pct25, round(Pct50, 7) as Pct50
        , round(Pct75, 7) as Pct75, round(Pct90, 7) as Pct90, "awarded"
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE round(Pct10Deficit, 7) END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE round(Pct25Deficit, 7) END as Pct25Deficit
        , round(Pct50Deficit, 7) as Pct50Deficit, round(Pct75Deficit, 7) as Pct75Deficit
        , round(Pct90Deficit, 7) as Pct90Deficit, "geometries_visible", "diagonal", "user_id"
        from arena_badge town
        inner join fq_town_name fqtn on fqtn.arena_id = town.id
        where fqtn.state in {in_statement}
        order by fqtn.region, fqtn.country, fqtn.state, fqtn.county, fqtn.town'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_fq_town_name_for_state(state):
    query = f'''select State, County, Town, long_name
	        from fq_town_name
            where State = "{state}"
            order by County, Town'''
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

    try:
        conn = sqlite3.connect(db_path)
        wandrerer_df = pd.read_sql_query(query, conn)
        return wandrerer_df
    except Exception as error:
        print(f'{error=}')
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
        if (ss['selected_state'] != None or ss['selected_region'] != None)\
            and ss['selected_map_type'] != None and ss['selected_datavalue_for_map'] != None:
            make_map_disable(False)
        else:
            make_map_disable(True)

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

    # file_path = os.path.join(cwd, r'data\boundaries', file_name)
    filesize = os.path.getsize(file_path)
    return file_path

def get_geopandas_df_for_state(selected_state):
    if selected_state not in st.session_state.gdfs.keys():
        print(f'Creating geopandas df for {selected_state}')
        file_path = get_geojson_filename(selected_state)
        gdf = gpd.read_file(f'{file_path}')
        st.session_state.gdfs[selected_state] = gdf
        if not column_exists_case_insensitive(gdf, 'normalized'):
            county_gdf, gdf = normalize_geojson(selected_state, gdf)

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
        county_gdfs = gpd.GeoDataFrame()
        for index, row in wandrer_regions.iterrows():
            state = row.State
            gdf = get_geopandas_df_for_state(state)
            if not column_exists_case_insensitive(gdf, 'normalized'):
                county_gdf, gdf = normalize_geojson(state, gdf)
            else:
                county_gdf = create_county_gdf(gdf)

            # county_gdf['state_county'] = state + '_' + county_gdf['County'].str.replace(' County', '')
            # county_gdf.drop(['Town'], axis=1, inplace=True, errors='ignore')
            # if ~column_exists_case_insensitive(gdf, 'normalized'):
            #     gdf['normalized'] = 'Y'
            # outfile = f'{state}_location.json'
            # gdf.to_file(outfile, driver="GeoJSON")

            if gdfs.empty:
                # gdfs = gpd.read_file(f'{file_path}')
                gdfs = gdf
                county_gdfs = county_gdf
                # gdfs['State'] = state
            else:
                gdfs = pd.concat([gdfs, gdf])
                county_gdfs = pd.concat([county_gdfs, county_gdf])

        return gdfs, county_gdfs
    else:
        print(f'Getting geopandas df for {selected_region} from session state')
        return st.session_state.gdfs[selected_region]


def normalize_geojson(state, gdf):
    print(f'{state=}')
    # wandrer_df = get_fq_town_name_for_state(row.State)
    # file_path = get_geojson_filename(row.State)
    # gdf = gpd.read_file(f'{file_path}')
    orignal_gdf = gdf.copy()

    if not column_exists_case_insensitive(gdf, 'State'):
        gdf['State'] = state

    if not column_exists_case_insensitive(gdf, 'admin_level'):
        rename_column_case_insensitive(gdf, 'COUNTY', 'County')
        rename_column_case_insensitive(gdf, 'TOWN', 'Town')

        gdf_none = gdf[gdf['County'].isnull()]
        gdf_not_none = gdf[~gdf['County'].isnull()]
        gdf.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
        if not column_exists_case_insensitive(gdf, 'long_name'):
            gdf['long_name'] = (
                    gdf['State'] + '_' + gdf['County'] + '_County_' + gdf['Town'].str.replace(' ', '_')).str.lower()
        # else:
        #     gdf['long_name'] = (gdf['State'] + '_' + gdf['County'] + '_County').str.lower()

        if not column_exists_case_insensitive(gdf, 'long_county'):
            # county_gdf['County'] += ' County'
            gdf['long_county'] = gdf['County'] + ' County'
            # state = gdf['State'].unique()[0]

        if not column_exists_case_insensitive(gdf, 'normalized'):
            gdf['normalized'] = 'Y'

        if not gdf.equals(orignal_gdf):
            outfile = f'{state}_locations.geojson'
            gdf.to_file(outfile, driver="GeoJSON")

        county_gdf = create_county_gdf(gdf)
        county_gdf['state_county'] = state + '_' + county_gdf['County'].str.replace(' County', '')
        county_gdf.drop(['Town'], axis=1, inplace=True, errors='ignore')
    else:
        # gdf['State'] = state
        df_dict = {sale_v: gdf[gdf['admin_level'] == sale_v] for sale_v in gdf['admin_level'].unique()}
        if 9 in gdf['admin_level'].values:
            # concatenate admin_level 8 and 9 dfs
            result = pd.concat([df_dict[8], df_dict[9]])
            df_dict[8] = result

        if column_exists_case_insensitive(df_dict[8], 'CNTY'):
            df_dict = {cnty: gdf[df_dict[8]['CNTY'] == cnty] for cnty in df_dict[8]['CMTY'].unique()}
            print('Now what...')
        else:
            # need wandrer data to determine county for towns. Ex: Massachusetts
            wandrer_df = get_fq_town_name_for_state(state)
            if len(wandrer_df['County'].str.contains(' County')):
                rename_column_case_insensitive(wandrer_df, 'County', 'long_county')
                wandrer_df['County'] = wandrer_df['long_county'].str.replace(' County', '')

            rename_column_case_insensitive(df_dict[8], 'name', 'Town')
            # wandrer_df = get_fq_town_name_for_state(state)
            wandrer_df_merged = df_dict[8].merge(wandrer_df, on=['State','Town'])
            # wandrer_df['County'] = wandrer_df['County'].str.replace(' County', '')
            # rename_column_case_insensitive(wandrer_df_merged, 'State_x', 'State')

            wandrer_df_merged.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
            wandrer_df_merged.drop(['tags', 'admin_level', 'State_y'], axis=1, inplace=True, errors='ignore')
            # wandrer_df_merged.drop('admin_level', axis=1, inplace=True, errors='ignore')
            # rename_column_case_insensitive(wandrer_df_merged, 'name', 'Town')
            if ~column_exists_case_insensitive(wandrer_df_merged, 'normalized'):
                wandrer_df_merged['normalized'] = 'Y'
            outfile = f'{state}_location.json'
            wandrer_df_merged.to_file(outfile, driver="GeoJSON")
            gdf = wandrer_df_merged

        # df_dict[8]['long_name'] = (df_dict[8]['State'] + '_' + df_dict[8]['County'] + '_County_' + df_dict[8]['Town']).str.lower()
        # wandrer_df = get_fq_town_name_for_state(state)
        # wandrer_df['County'] = wandrer_df['County'].str.replace(' County', '')
        # wandrer_df = get_wandrer_totals_for_towns_for_state(state)
        # wandrer_df_merged = wandrer_df.merge(df_dict[8], on='Town')
        # wandrer_df_merged = df_dict[8].merge(wandrer_df, on='Town')
        # wandrer_df_merged.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
        # wandrer_df_merged.drop(['tags','admin_level'], axis=1, inplace=True, errors='ignore')
        # wandrer_df_merged.drop('admin_level', axis=1, inplace=True, errors='ignore')
        # location_json = orjson.loads(wandrer_df_merged.to_json())
        # outfile = f'{state}_location.json'
        # wandrer_df_merged.to_file(outfile, driver="GeoJSON")
        # with open(outfile, "w") as f:
        #     json.dump(location_json, f, indent=4)

        county_gdf = df_dict[6]
        rename_column_case_insensitive(county_gdf, 'name', 'County')
        county_gdf['State'] = state
        county_gdf['state_county'] = state + '_' + county_gdf['County'].str.replace(' County', '')
        county_gdf.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
        county_gdf.drop(['admin_level'], axis=1, inplace=True, errors='ignore')
    return county_gdf, gdf


# ss

options = ['State', 'Counties', 'Towns']
geojson_files = get_geojson_filenames()
wandrer_regions = get_wandrer_subregions()
region_list = ['All'] + (wandrer_regions.subregion_name.unique().tolist())
data_values = ['TotalMiles', 'ActualMiles', 'ActualMiles > 1', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit']

if 'gdfs' not in st.session_state:
    # Initialize geopandas df dictionary in session state.
    st.session_state.gdfs = {}

with st.sidebar:
    region_selectbox = st.selectbox('Select a region:', region_list, key='selected_region', index=None, on_change=region_selected())
    state_selectbox = st.selectbox('Select a location (US State):', geojson_files.keys(), key='selected_state', index=None)
    # preserve_map_selection = st.checkbox('Clear map type selection on state change', key='preserve_map_selection')
    maptype_selectbox = st.selectbox('Select a map type:', options, key='selected_map_type', index=None)
    datavalue_selectbox = st.selectbox('Select a data value', data_values, key='selected_datavalue_for_map', index=None, on_change=enable_make_map())
    make_map = st.button('Generate map', key='make_map_btn', disabled=st.session_state.get("make_map_disable", True))

if make_map:
    osm_gdf = {}
    fig = {}

    if region_selectbox:
        osm_state_gdf, osm_county_gdf = get_geopandas_df_for_region(region_selectbox)
        match maptype_selectbox:
            case 'State':
                fig = create_region_map(osm_state_gdf.copy(), region_selectbox)
            case 'Counties':
                fig = create_region_by_county_map(osm_county_gdf.copy(), region_selectbox)
            case 'Towns':
                fig = create_region_by_town_map(osm_state_gdf.copy(), region_selectbox)
    else:
        osm_gdf = get_geopandas_df_for_state(state_selectbox)
        match maptype_selectbox:
            case 'State':
                fig = create_state_map(osm_gdf.copy(), state_selectbox)
            case 'Counties':
                fig = create_county_map(osm_gdf.copy(), state_selectbox)
            case 'Towns':
                fig = create_town_map(osm_gdf.copy(), state_selectbox)

    if fig:
        st.plotly_chart(fig)
        st.write('Raw Data')
        # st.dataframe(osm_gdf, use_container_width=True)
        st.dataframe(st.session_state['map_gdf'], use_container_width=True)
    else:
        st.write(f'{maptype_selectbox} map unavailable for {state_selectbox}')

# ss

