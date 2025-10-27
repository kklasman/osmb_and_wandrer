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
from shapely.geometry import LineString
# from auth_utils import check_password
import requests
from io import StringIO
from datetime import datetime
import database as db
import logging
# import uuid
# from pympler import asizeof

# Configure the root logger
logging.basicConfig(level=logging.INFO)

# Get a logger for the current module
logger = logging.getLogger(__name__)

logger.info(f'python version: {sys.version}')
logger.info(f'python version_info: {sys.version_info}')

os.environ['PYOGRIO_USE_ARROW'] = '1'

st.set_page_config(layout='wide')

max_50_pct_color_scale = ['white', 'gold', 'red']


award_levels_color_map = {
    '0%': 'rgb(211,211,211)',
    '< 1 mile': 'rgb(192,192,192)',
    '< 5%': 'rgb(169,169,169)',
    '5%': 'rgb(128,128,128)',
    '10%': 'rgb(255,250,205)',
    '25%': 'rgb(255,215,0)',
    '50%': 'darkorange',
    '75%': 'crimson',
    '90%': 'magenta',
    '99%': 'blue'
}

# award_levels_color_map = {
#     '0.0': 'gray',
#     '0.10': 'white',
#     '0.25': 'almond',
#     '0.50': 'yellow',
#     '0.75': 'orange',
#     '0.90': 'red',
#     '0.99': 'magenta',
#     '1.00': 'blue'
# }

# color_discrete_map = {
#     'High': 'red',
#     'Moderate': 'blue',
#     'Low': 'green'
# }

# color_schemes = [
#     ['#890000'],['#890000'],['#5c0000'],
#     ['#2a6b28'],['#0b4c07'],['#003206'],
#     ['#fff4b1']
# ]
color_schemes = ['#890000','#890000','#5c0000','#2a6b28','#0b4c07','#003206','#fff4b1']

# award_levels_color_map = {
#     0: 'gray',
#     1: 'white',
#     2: 'rgb(255, 255, 200)',
#     3: 'yellow',
#     4: 'orange',
#     5: 'red',
#     6: 'magenta',
#     7: 'blue'
# }


def create_template(data, col_names):
    template = ''
    for idx, name in enumerate(col_names):
        try:
            if name == 'awarded':
                template += "<b>Awarded:</b> %{" + f"customdata[{data.columns.get_loc('awarded')}]" + "}<br>"

            elif name == 'Award Level':
                template += "<b>Award Level:</b> %{" + f"customdata[{data.columns.get_loc('Award Level')}]" + "}<br>"

            elif name == 'State':
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
                template += "<b>Total Town Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalMiles')}]:,.2f" + "}<br>"

            elif name == 'TotalCountyMiles':
                template += "<b>Total County Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalCountyMiles')}]:,.2f" + "}<br>"

            elif name == 'TotalCountyMilesCycled':
                template += "<b>Total County Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TotalCountyMilesCycled')}]:,.2f" + "}<br>"

            elif name == 'PctCountyMilesCycled':
                template += "<b>Pct County Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctCountyMilesCycled')}]:,.2%" + "}<br>"

            elif name == 'TotalTownMiles':
                template += "<b>Total Town Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalTownMiles')}]:,.2f" + "}<br>"

            elif name == 'UnincorporatedMiles':
                template += "<b>Unincorporated Miles:</b> %{" + f"customdata[{data.columns.get_loc('UnincorporatedMiles')}]:,.2f" + "}<br>"

            elif name == 'UnincorporatedMilesCycled':
                template += "<b>Unincorporated Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('UnincorporatedMilesCycled')}]:,.2f" + "}<br>"

            elif name == 'PctUnincorporatedMilesCycled':
                template += "<b>Pct Unincorporated Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctUnincorporatedMilesCycled')}]:.2%" + "}<br>"

            elif name == 'Pct10Unincorporated':
                template += "<b>10% Unincorporated Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct10Unincorporated')}]:,.2f" + "}<br>"

            elif name == 'Pct25Unincorporated':
                template += "<b>25% Unincorporated Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct25Unincorporated')}]:,.2f" + "}<br>"

            elif name == 'ActualMiles':
                template += "<b>Town Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('ActualMiles')}]:,.2f" + "}<br>"

            elif name == 'MilesRidden':
                template += "<b>Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('MilesRidden')}]:,.2f" + "}<br>"

            elif name == 'ActualPct':
                template += "<b>Pct Town Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('ActualPct')}]:.2%" + "}<br>"

            elif name == 'Pct10':
                template += "<b>10% Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct10')}]:,.2f" + "}<br>"

            elif name == 'Pct25':
                template += "<b>25% Miles Target</b> %{" + f"customdata[{data.columns.get_loc('Pct25')}]:,.2f" + "}<br>"

            elif name == 'Pct10Deficit':
                template += "<b>10% Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct10Deficit')}]:,.2f" + "}<br>"

            elif name == 'Pct25UnincorporatedDeficit':
                template += "<b>25% Unincorporated Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct25UnincorporatedDeficit')}]:,.2f" + "}<br>"

            elif name == 'Pct10UnincorporatedDeficit':
                template += "<b>10% Unincorporated Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct10UnincorporatedDeficit')}]:,.2f" + "}<br>"

            elif name == 'Pct25Deficit':
                template += "<b>25% Miles Deficit</b> %{" + f"customdata[{data.columns.get_loc('Pct25Deficit')}]:,.2f" + "}<br>"

            elif name == 'TotalTowns':
                template += "<b>Total Towns:</b> %{" + f"customdata[{data.columns.get_loc('TotalTowns')}]" + "}<br>"

            elif name == 'TownsCycled':
                template += "<b>Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TownsCycled')}]" + "}<br>"

            elif name == 'CycledTowns':
                template += "<b>Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('CycledTowns')}]" + "}<br>"

            elif name == 'TownsNotCycled':
                template += "<b>Towns Not Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TownsNotCycled')}]" + "}<br>"

            elif name == 'PctTownsCycled':
                template += "<b>Pct Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsCycled')}]:.2%" + "}<br>"

            elif name == 'AchievedTowns':
                template += "<b>Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('AchievedTowns')}]" + "}<br>"

            elif name == 'PctTownsAchieved':
                template += "<b>Pct Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsAchieved')}" + "]:.2%}<br>"

            else:
                print(f'Column {name} not found')
        except KeyError:
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

def calculate_mapbox_zoom_center_from_diagonal(diagonal) -> (float, dict):
    """calc zoom and center for plotly mapbox functions

    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434
    """

    diagonal_json = json.loads(diagonal)
    point1 = diagonal_json['coordinates'][0]
    point2 = diagonal_json['coordinates'][1]
    x1, y1 = point1
    x2, y2 = point2
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    center = dict(lat=y_center, lon=x_center)

    min_lon = min(x1, x2)
    max_lon = max(x1, x2)
    min_lat = min(y1, y2)
    max_lat = max(y1, y2)

    # zoom = 10
    y_range = distance.geodesic((min_lat, min_lon), (max_lat, min_lon)).kilometers
    x_range = distance.geodesic((min_lat, min_lon), (min_lat, max_lon)).kilometers
    #
    # # does this work across the international date line?
    # center = dict(lat=(min_lat + max_lat) / 2, lon=(min_lon + max_lon) / 2)
    #
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

def create_county_map_v2(source_osm_df, state):
    renamed_gdf = {}
    counties_gdf = {}
    state_gdf = {}

    county_gdf = source_osm_df.dissolve(by='County')
    county_gdf.reset_index(inplace=True)
    county_gdf['County'] = county_gdf['County'].str.title()
    county_gdf = clean_county_gdf(county_gdf)

    convert_bounds_to_linestrings(county_gdf)

    # source_osm_df.drop(list(source_osm_df.filter(regex='NHD:')), axis=1, inplace=True)

    state_gdf = source_osm_df.dissolve(by='State')
    columns_to_drop = state_gdf.select_dtypes(include=['datetime64']).columns
    state_gdf.drop(columns=columns_to_drop, axis=1, inplace=True)
    state_boundary_json = json.loads(state_gdf.to_json())

    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)

    state_list = []
    state_list.append(state)
    wandrerer_df = get_wandrer_totals_for_counties_for_states_v2(state_list)
    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)

    # # unincorporated_df = get_wandrer_unincorporated_totals_for_counties_for_states(state_list)
    # unincorporated_df = get_wandrer_unincorporated_aggregates_for_counties_for_states(state_list)
    # unincorporated_df['County'] = unincorporated_df['County'].str.replace(' County', '')
    #
    # # wandrerer_and_uninc_df = wandrerer_df.merge(unincorporated_df, on=['Region', 'Country', 'State', 'County'])
    #
    # # print(wandrerer_df)
    # merged_df = county_gdf.merge(unincorporated_df, on=['State','County'])
    # wandrerer_df.rename(columns={'County': 'long_county'}, inplace=True)
    # wandrerer_df['County'] = wandrerer_df['long_county'].str.replace(' County', '')
    merged_df = county_gdf.merge(wandrerer_df, on=['State','County', 'long_county'])
    merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
    # merged_df.drop(list(merged_df.filter(regex='NHD:')), axis=1, inplace=True)
    # columns_to_drop = merged_df.select_dtypes(include=['datetime64']).columns
    # merged_df.drop(columns=columns_to_drop, axis=1, inplace=True)
    # final_df = merged_df.drop(['County'], axis=1, errors='ignore')
    # final_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    location_json = json.loads(merged_df.to_json())
    merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # template = create_template(merged_df, ['County', 'TotalTowns', 'TotalCountyMiles', 'TotalTownMiles', 'CountyUnincorporatedMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    template_fields = get_template_field_list_for_county_scope_map(merged_df)

    template = create_template(merged_df, template_fields)

    if data_value == 'TotalMiles':
        data_value = 'TotalCountyMiles'

    z_max = float(merged_df[data_value].max()) if float(merged_df[data_value].max()) > 0 else float(merged_df[data_value].max())
    z_data_value = 'TotalCountyMilesCycled' if data_value.startswith('ActualMiles') else data_value

    st.session_state['map_gdf'] = merged_df
    fig = go.Figure(go.Choroplethmap(
        customdata=merged_df,
        geojson=location_json,
        featureidkey='properties.County',
        locations=merged_df['County'],
        z=merged_df[z_data_value],
        zmin=0,
        zmax=z_max,
        colorscale=max_50_pct_color_scale,
        hovertemplate=template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        marker_opacity=0.5,
        visible=True,
        colorbar_title=z_data_value
    ))

    fig.update_layout(map_layers=[dict(sourcetype='geojson',
                                          source=state_boundary_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )])

    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Counties in {state}', x=0.5
                            , xanchor="center")
                            )
    fig.update_geos(fitbounds="geojson", visible=True)
    return fig


# def create_county_map(source_osm_df, state):
#     renamed_gdf = {}
#     counties_gdf = {}
#     state_gdf = {}
#
#     county_gdf = source_osm_df.dissolve(by='County')
#     county_gdf.reset_index(inplace=True)
#     county_gdf['County'] = county_gdf['County'].str.title()
#     county_gdf = clean_county_gdf(county_gdf)
#
#     convert_bounds_to_linestrings(county_gdf)
#
#     source_osm_df.drop(list(source_osm_df.filter(regex='NHD:')), axis=1, inplace=True)
#
#     state_gdf = source_osm_df.dissolve(by='State')
#     columns_to_drop = state_gdf.select_dtypes(include=['datetime64']).columns
#     state_gdf.drop(columns=columns_to_drop, axis=1, inplace=True)
#     state_boundary_json = json.loads(state_gdf.to_json())
#
#     zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
#
#     state_list = []
#     state_list.append(state)
#     wandrerer_df = get_wandrer_totals_for_counties_for_states(state_list)
#     data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)
#
#     # unincorporated_df = get_wandrer_unincorporated_totals_for_counties_for_states(state_list)
#     unincorporated_df = get_wandrer_unincorporated_aggregates_for_counties_for_states(state_list)
#     unincorporated_df['County'] = unincorporated_df['County'].str.replace(' County', '')
#
#     # wandrerer_and_uninc_df = wandrerer_df.merge(unincorporated_df, on=['Region', 'Country', 'State', 'County'])
#
#     # print(wandrerer_df)
#     merged_df = county_gdf.merge(unincorporated_df, on=['State','County'])
#     # merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
#     merged_df.drop(list(merged_df.filter(regex='NHD:')), axis=1, inplace=True)
#     columns_to_drop = merged_df.select_dtypes(include=['datetime64']).columns
#     merged_df.drop(columns=columns_to_drop, axis=1, inplace=True)
#     final_df = merged_df.drop(['County'], axis=1, errors='ignore')
#     final_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
#     location_json = json.loads(merged_df.to_json())
#     merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
#     # template = create_template(merged_df, ['County', 'TotalTowns', 'TotalCountyMiles', 'TotalTownMiles', 'CountyUnincorporatedMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
#     template_fields = get_template_field_list_for_county_scope_map(merged_df)
#
#     template = create_template(merged_df, template_fields)
#
#     if data_value == 'TotalMiles':
#         data_value = 'TotalTownMiles'
#
#     z_max = float(merged_df[data_value].max()) if float(merged_df[data_value].max()) > 0 else float(merged_df[data_value].max())
#     z_data_value = 'TotalCountyMilesCycled' if data_value.startswith('ActualMiles') else 'TotalCountyMiles'
#
#     st.session_state['map_gdf'] = merged_df
#     fig = go.Figure(go.Choroplethmapbox(
#         customdata=merged_df,
#         geojson=location_json,
#         featureidkey='properties.County',
#         locations=merged_df['County'],
#         z=merged_df[z_data_value],
#         zmin=0,
#         zmax=z_max,
#         colorscale=max_50_pct_color_scale,
#         hovertemplate=template,
#         # hoverlabel_bgcolor='white',
#         hoverlabel=dict(
#             bgcolor="black",
#             font_size=16),
#         marker_opacity=0.5,
#         visible=True,
#         colorbar_title=z_data_value
#     ))
#
#     fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
#                                           source=state_boundary_json,
#                                           color='#303030',
#                                           type='line',
#                                           line=dict(width=1.5)
#                                           )])
#
#     fig.update_layout(mapbox_style="carto-positron",
#                       mapbox_zoom=zoom, mapbox_center=center)
#     fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
#                             , title=dict(text=f'{data_value} for Counties in {state}', x=0.5
#                             , xanchor="center")
#                             )
#     fig.update_geos(fitbounds="geojson", visible=True)
#     return fig


def get_template_field_list_for_county_scope_map(merged_df):
    template_fields = ['State','County', 'TotalTowns', 'CycledTowns', 'PctTownsCycled', 'AchievedTowns', 'PctTownsAchieved',
                       'TotalTownMiles', 'ActualMiles', 'ActualPct']
    # if any(merged_df['UnincorporatedMiles'] > 0):
    #     template_fields.extend(['TotalCountyMiles', 'TotalCountyMilesCycled', 'PctCountyMilesCycled'])
    # template_fields.extend(['TotalTowns', 'CycledTowns', 'PctTownsCycled', 'AchievedTowns', 'PctTownsAchieved',
    #                         'TotalTownMiles', 'ActualMiles', 'ActualPct'])
    if any(merged_df['UnincorporatedMiles'] > 0):
        template_fields.extend(['TotalCountyMiles', 'TotalCountyMilesCycled', 'PctCountyMilesCycled',
                                'UnincorporatedMiles', 'UnincorporatedMilesCycled', 'PctUnincorporatedMilesCycled'])
    return template_fields


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


def create_town_map(town_gdf, state, maptype):
    town_gdf = clean_gdf(town_gdf)
    # county_gdf = town_gdf.dissolve(by='County')

    # # Save the GeoDataFrame to a GeoJSON file
    # output_filename = f'{state}_locations_filtered.geojson'
    # town_gdf.to_file(output_filename, driver='GeoJSON')

    county_gdf = town_gdf.dissolve(by='long_county')
    county_gdf.reset_index(inplace=True)
    convert_bounds_to_linestrings(county_gdf)

    state_gdf = county_gdf.dissolve('State')
    state_gdf.reset_index(inplace=True)
    data_value = ss['selected_datavalue_for_map']

    dissolved_town_gdf = town_gdf.dissolve('Town')
    dissolved_town_gdf.reset_index(inplace=True)
    dissolved_town_gdf = dissolved_town_gdf.dropna(axis=1, how='all')
    dissolved_town_gdf = dissolved_town_gdf[dissolved_town_gdf.columns.drop(list(dissolved_town_gdf.filter(regex='name:')))]

    state_list = []
    state_list.append(state)
    wandrerer_county_df = get_wandrer_totals_for_counties_for_states(state_list)
    if data_value == 'ActualMiles > 1':
        data_value =  'ActualMiles'
    merged_county_df = county_gdf.merge(wandrerer_county_df, on=['State','County'])
    merged_county_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
    columns_to_drop = merged_county_df.select_dtypes(include=['datetime64']).columns
    merged_county_df.drop(columns=columns_to_drop, axis=1, inplace=True)
    county_location_json = json.loads(merged_county_df.to_json())
    merged_county_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    merged_county_df['always_zero'] = 0
    template_fields = ['County', 'TotalTownMiles', 'ActualMiles', 'ActualPct']
    if any(merged_county_df['UnincorporatedMiles'] > 0):
        template_fields.extend(['UnincorporatedMiles', 'UnincorporatedMilesCycled', 'PctUnincorporatedMilesCycled'])
        if data_value == 'Pct10Deficit':
            template_fields.extend(['Pct10Unincorporated', 'Pct10UnincorporatedDeficit'])

        if data_value == 'Pct25Deficit':
            template_fields.extend(['Pct25Unincorporated', 'Pct25UnincorporatedDeficit'])

    county_template = create_template(merged_county_df, template_fields)

    # else:
    #     county_template = create_template(merged_county_df, ['County', 'TotalTownMiles', 'ActualMiles', 'ActualPct'])
    # if any(merged_county_df['UnincorporatedMiles'] > 0):
    #     unincorporated_fields = ['County', 'UnincorporatedMiles', 'PctUnincorporatedMilesCycled',
    #    'UnincorporatedMilesCycled']
    #     if data_value == 'Pct10Deficit':
    #         unincorporated_fields.extend(['Pct10Unincorporated', 'Pct10UnincorporatedDeficit'])
    #
    #     if data_value == 'Pct25Deficit':
    #         unincorporated_fields.extend(['Pct25Unincorporated', 'Pct25UnincorporatedDeficit'])
    #
    #     county_template = create_template(merged_county_df, unincorporated_fields)
    #
    # else:
    #     county_template = create_template(merged_county_df, ['County', 'TotalTownMiles', 'ActualMiles', 'ActualPct'])

    wandrerer_df = get_wandrer_totals_for_towns_for_state(state_list)
    if (maptype == 'Seacoast Towns'):
        wandrerer_df = wandrerer_df[wandrerer_df['seacoast'] == 1]

    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)

    if sys.gettrace() is not None:
        dump_town_misses_and_matches(state, town_gdf, wandrerer_df)

    # town_merged_df = town_gdf.merge(wandrerer_df, on=['State','County','Town','long_name'])
    # town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State','County','Town','long_name'])
    if wandrerer_df['osm_id'].isnull().all():
        # old format towns without osm_id values
        town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State','County', 'Town','long_name'])
        town_merged_df.drop('osm_id', axis=1, inplace=True, errors='ignore')
    else:
        # new format towns with osm_id values
        wandrerer_df['osm_id'] = wandrerer_df['osm_id'].astype('Int64')
        dissolved_town_gdf['osm_id'] = dissolved_town_gdf['osm_id'].astype('Int64')
        # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on='osm_id', how='left')
        # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on=['osm_id', 'Town', 'County', 'State', 'long_name'],
        #                       how='left')
        town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State', 'County', 'Town', 'long_name', 'osm_id'])

    # rename_column_case_insensitive(town_merged_df, 'Town_x', 'Town')
    # rename_column_case_insensitive(town_merged_df, 'diagonal_x', 'diagonal')

    # # unincorporated_df = wandrerer_df[wandrerer_df['Town'] == 'Unincorporated']
    # unincorporated_df = wandrerer_df[wandrerer_df['Town'].str.startswith('Unincorporated')]
    # unincorporated_df.drop(['diagonal', 'osm_id'], axis=1, inplace=True, errors='ignore')
    # county_filtered_gdf = county_gdf.copy()
    # county_filtered_gdf.drop(['Town', 'long_name'], axis=1, inplace=True, errors='ignore')
    #
    # # town_unincorporated_merged_df = town_merged_df.merge(unincorporated_merged_df, on=['State','County'])
    # # unincorporated_merged_df = unincorporated_df.merge(county_filtered_gdf, on=['State','County'])
    # unincorporated_merged_df = unincorporated_df.merge(county_filtered_gdf, on=['State', 'County'])
    # # unincorporated_merged_df.drop(['diagonal_x'], axis=1, inplace=True, errors='ignore')
    # # rename_column_case_insensitive(unincorporated_merged_df, 'diagonal_y', 'diagonal')
    #
    # # town_unincorporated_appended_df = pd.concat([town_merged_df, unincorporated_merged_df])
    # town_unincorporated_appended_df = town_merged_df.copy() # fake not adding unincorporated towns
    # # county_z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())
    # # if len(unincorporated_merged_df) > 0:
    # #     county_location_json = json.loads(unincorporated_merged_df.to_json())
    # #     unincorporated_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # #     unincorporated_merged_df['always_zero'] = 0
    # #     merged_county_df = unincorporated_merged_df
    # #     county_template = create_template(merged_county_df, ['County', 'Town', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])

    marker_opacity = 0.5
    if bool(merged_county_df['UnincorporatedMiles'].max() > 0):
        z_column = 'UnincorporatedMiles'
        colorscale = 'Blues'
        county_z_min = 400
        show_color_bar = True
    else:
        z_column = 'always_zero'
        if ss['selected_datavalue_for_map'] != 'ActualMiles >= 1' and ss['selected_datavalue_for_map'] != 'ActualMiles < 1':
            colorscale = max_50_pct_color_scale
        else:
            colorscale = 'Greys'
        county_z_min = 0
        show_color_bar = False

    county_z_max = int(round(merged_county_df[z_column].max() + 500, -3))
    fig = go.Figure()
    fig.add_trace(
        go.Choroplethmap(
            customdata=merged_county_df,
        geojson=county_location_json,
        featureidkey='properties.County',
        locations=merged_county_df['County'],
        z=merged_county_df[z_column],
        # z=1,
        # colorscale='ylorrd',
        colorscale=colorscale,
        # colorbar=dict(title='County', x=0.01, y=0.0), legend_xanchor='left',
        colorbar_x=-0.2,
        colorbar_title='Unincorporated<br>Miles',
        showscale=show_color_bar,
        # showlegend=True,
        zmin=county_z_min,
        # zmax=z_max,
        zmax=county_z_max,
        hovertemplate=county_template,
        # hoverlabel_bgcolor='white',
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        marker_opacity=marker_opacity,
        marker_line_width=1.5,
        visible=True
        # colorbar_title=data_value
    ))

    # # location_json = json.loads(town_merged_df.to_json())
    # columns_to_drop = town_unincorporated_appended_df.select_dtypes(include=['datetime64']).columns
    # town_unincorporated_appended_df.drop(columns=columns_to_drop, axis=1, inplace=True)
    # town_unincorporated_appended_df.reset_index(drop=True, inplace=True)
    location_json = json.loads(town_merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    town_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # town_unincorporated_appended_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # # z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())
    # # z_max_raw = float(town_unincorporated_appended_df[data_value].max()) \
    # #     if float(town_unincorporated_appended_df[data_value].max()) > 0 \
    # #     else float(town_unincorporated_appended_df['TotalMiles'].max())

    if data_value == 'Award Level':
        # fig = create_town_map_discrete_color(center, county_location_json, data_value, fig, location_json, state,
        #                                        town_merged_df, zoom)
        fig = create_town_map_discrete_color(center, county_location_json, data_value, merged_county_df, location_json, state,
                                               town_merged_df, zoom)
    else:
        fig = create_town_map_continuous_color(center, county_location_json, data_value, fig, location_json, state,
                                                       town_merged_df, zoom)

    return fig


def create_town_map_continuous_color(center, county_location_json, data_value, fig, location_json, state,
                                     town_merged_df, zoom):
    z_max_raw = town_merged_df[data_value].max() if town_merged_df[data_value].max() > 0 else 0
    z_max = int(round(z_max_raw + 250, -3))
    z_min = 0
    # st.session_state['map_gdf'] = town_merged_df
    # st.session_state['map_gdf'] = town_unincorporated_appended_df
    st.session_state['map_gdf'] = town_merged_df
    # town_template = create_template(town_merged_df, ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    town_template = create_template(town_merged_df,
                                    ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit',
                                     'Pct25Deficit'])
    town_color_scale = award_levels_color_map if data_value == 'Award Level' else max_50_pct_color_scale
    fig.add_trace(
        go.Choroplethmap(
            customdata=town_merged_df,
            geojson=location_json,
            featureidkey='properties.Town',
            locations=town_merged_df['Town'],
            # locations=town_unincorporated_appended_df['long_name'],
            # z=filtered_df[z_col_name] * 100,
            z=town_merged_df[data_value],
            colorscale=town_color_scale,
            colorbar_title=data_value,
            # hovertemplate="County: %{customdata[2]}<br>Actual Pct: %{customdata[4]}<extra></extra>",
            hovertemplate=town_template,
            # hoverlabel_bgcolor='white',
            hoverlabel=dict(
                bgcolor="black",
                font_size=16),
            marker_opacity=1,
            name='Town Data Values',
            # visible=map_feature_selected == 'Town Boundaries',
            zmin=z_min,
            zmax=z_max
        )
    )

    fig.update_layout(map_layers=[dict(sourcetype='geojson',
                                          source=county_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          # hovertemplate=template
                                          )]);
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Towns in {state}', x=0.5
                                         , xanchor="center")
                            )
    return fig

def generateDiscreteColourScale(colour_set):
    #colour set is a list of lists
    # colour_output = []
    # num_colours = len(colour_set)
    # divisions = 1./num_colours
    divisions = [0,.10, .25, .50, .75, .90, .99]
    # divisions = ['0','.10', '.25', '.50', '.75', '.90', '.99']
    colour_output = [list(t) for t in zip(divisions, colour_set)]
    # c_index = int(0)
    # # Loop over the colour set
    # for cset in colour_set:
    #     colour_output.append((divisions[c_index], cset))
    #     c_index += 1

    #
    #     num_subs = len(cset)
    #     sub_divisions = divisions/num_subs
    #     # Loop over the sub colours in this set
    #     for subcset in cset:
    #         colour_output.append((c_index,subcset))
    #         colour_output.append((c_index + sub_divisions-
    #             .001,subcset))
    #         c_index = c_index + sub_divisions
    # colour_output[-1]=(1,colour_output[-1][1])
    return colour_output


def create_town_map_discrete_color(center, county_location_json, data_value, merged_county_df, location_json, state,
                                     town_merged_df, zoom):
    # z_max_raw = town_merged_df[data_value].max() if town_merged_df[data_value].max() > 0 else 0
    # z_max = int(round(z_max_raw + 250, -3))
    z_max = 1.0
    z_min = 0
    # st.session_state['map_gdf'] = town_merged_df
    # st.session_state['map_gdf'] = town_unincorporated_appended_df
    st.session_state['map_gdf'] = town_merged_df
    # town_template = create_template(town_merged_df, ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    town_template = create_template(town_merged_df,
                                    ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit',
                                     'Pct25Deficit', 'awarded', 'Award Level'])
    # town_color_scale = award_levels_color_map if data_value == 'Award Level' else max_50_pct_color_scale
    # town_color_scale = ((0.00, 'rgb(247,251,255)'), (0.125, 'rgb(222,235,247)'), (0.25, 'rgb(198,219,239)'), (0.375, 'rgb(158,202,225)'), (0.5, 'rgb(107,174,214)'), (0.625, 'rgb(66,146,198)'), (0.75, 'rgb(33,113,181)'), (0.875, 'rgb(8,81,156)'), (1.0, 'rgb(8,48,107)'))
    # colorscale = generateDiscreteColourScale(color_schemes)

    # filtered_df = town_merged_df[['Town', 'Award Level']]
    fig = px.choropleth_map(
        town_merged_df,
         geojson=location_json,
        locations='Town',
        color='Award Level',  # Use the categorical column for discrete colors
        featureidkey='properties.Town',
        # color_discrete_map=award_levels_color_map,
        # scope='usa',
        zoom=8,
        # center={"lat": 43.80471, "lon": -71.57059}, # Center of the map
        color_discrete_map=award_levels_color_map,
        category_orders={'Award Level': ['0%','< 1 mile','< 5%','5%','10%','25%','50%','75%','90%','99%']}
    )

    # Add template for each trace, filtering the data on 'Award Level'.
    for trace in fig.data:
        trace.customdata=town_merged_df[town_merged_df['Award Level'] == trace.name]
        trace.hovertemplate = town_template
        trace.ids = [trace.name]

    # county_template = create_template(merged_county_df, ['State', 'County'])
    #
    # fig.add_trace(go.Choroplethmapbox(
    # # fig=px.choropleth_mapbox(merged_county_df,
    #     customdata=merged_county_df,
    #     geojson=county_location_json,
    #     featureidkey='properties.County',
    #     locations=merged_county_df['County'],
    #     below=fig.data[0]['ids'][0],
    #     # z=merged_county_df[z_column],
    #     # z=1,
    #     # colorscale='ylorrd',
    #     # colorscale=colorscale,
    #     # colorbar=dict(title='County', x=0.01, y=0.0), legend_xanchor='left',
    #     # colorbar_x=-0.2,
    #     # colorbar_title='Unincorporated<br>Miles',
    #     # showscale=show_color_bar,
    #     # showlegend=True,
    #     # zmin=county_z_min,
    #     # zmax=z_max,
    #     # zmax=county_z_max,
    #     hovertemplate=county_template,
    #     # hover_name='County Award Levels by Town',
    #     # hover_data=['State', 'County', '0%', '< 1 mile', '< 5%', '5%',
    #    # '10%', '25%', '50%', '75%', '90%', '99%'],
    #    #  labels={'0%': '0% Town Count'},
    #     # hover_name='County'
    #     # hoverlabel_bgcolor='white',
    #     # hoverlabel=dict(
    #     #     bgcolor="black",
    #     #     font_size=16),
    #     # marker_opacity=marker_opacity,
    #     # marker_line_width=1.5,
    #     # visible=True
    #     # colorbar_title=data_value
    # ))
    #
    # # fig.add_trace(county_fig)

    fig.update_layout(map_layers=[dict(sourcetype='geojson',
                                          source=county_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5),
                                          # hovertemplate=county_template
                                          )])
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for Towns in {state}', x=0.5
                                         , xanchor="center")
                            )
    return fig


def clean_gdf(town_gdf):
    if column_exists_case_insensitive(town_gdf, 'osm_id'):
        columns_to_keep = ['osm_id', 'Town', 'State', 'long_county', 'long_name', 'County', 'normalized', 'geometry']
    else:
        columns_to_keep = ['Town', 'State', 'long_county', 'long_name', 'County', 'normalized', 'geometry']

    filtered_gdf = town_gdf[columns_to_keep]
    return filtered_gdf


def clean_county_gdf(town_gdf):
    if column_exists_case_insensitive(town_gdf, 'osm_id'):
        columns_to_keep = ['osm_id', 'State', 'long_county', 'long_name', 'County', 'normalized', 'geometry']
    else:
        columns_to_keep = ['State', 'long_county', 'long_name', 'County', 'normalized', 'geometry']

    filtered_gdf = town_gdf[columns_to_keep]
    return filtered_gdf


def dump_town_misses_and_matches(state, town_gdf, wandrerer_df):
    json_matches = town_gdf[town_gdf['Town'].isin(wandrerer_df['Town'])]
    if len(json_matches) > 0:
        json_matches['DataSource'] = 'json'
        json_matches_no_dupes = json_matches.drop_duplicates()
        selected_columns = ['DataSource', 'County', 'Town']
        try:
            json_matches_no_dupes[selected_columns].to_csv(f'{state}-Matching-Towns.csv', index=False)
        except Exception as e:
            st.write(f"An unexpected error occurred: {e}")

    json_diffs = wandrerer_df[~wandrerer_df['Town'].isin(town_gdf['Town'])]
    if len(json_diffs) > 0:
        json_diffs['DataSource'] = 'json'
        json_diffs_no_dupes = json_diffs.drop_duplicates()
        selected_columns = ['DataSource', 'County', 'Town']
        try:
            json_diffs_no_dupes[selected_columns].to_csv(f'{state}-Missing-Towns.csv', index=False)
        except Exception as e:
            st.write(f"An unexpected error occurred: {e}")


# def create_town_map_old(town_gdf, state):
#     county_gdf = town_gdf.dissolve('County')
#     county_gdf.reset_index(inplace=True)
#     state_gdf = county_gdf.dissolve('State')
#     state_gdf.reset_index(inplace=True)
#     data_value = ss['selected_datavalue_for_map']
#
#
#     state_list = []
#     state_list.append(state)
#     wandrerer_county_df = get_wandrer_totals_for_counties_for_states(state_list)
#     data_value, wandrerer_county_df = filter_wandrerer_df(wandrerer_county_df)
#     merged_county_df = county_gdf.merge(wandrerer_county_df, on=['State','County'])
#     merged_county_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
#     county_location_json = json.loads(merged_county_df.to_json())
#     merged_county_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
#     merged_county_df['always_zero'] = 0
#     # county_template = create_template(merged_county_df, ['County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
#     if any(merged_county_df['UnincorporatedMiles'] > 0):
#         county_template = create_template(merged_county_df, ['County', 'UnincorporatedMiles', 'PctUnincorporatedMilesCycled',
#        'UnincorporatedMilesCycled'])
#     else:
#         county_template = create_template(merged_county_df, ['County', 'TotalMiles', 'ActualMiles', 'ActualPct'])
#
#     # if (merged_county_df['CountyUnincorporatedMiles'] > 0).any():
#     #     county_template = create_template(merged_county_df, ['County', 'CountyUnincorporatedMiles', 'ActualMiles', 'ActualPct'])
#     # else:
#     #     county_template = create_template(merged_county_df, ['County', 'TotalCountyMiles', 'ActualMiles', 'ActualPct'])
#     # merged_county_df['TotalMiles'] = 0
#
#     # print(wandrerer_df)
#     # merged_df = county_gdf.merge(wandrerer_df, on=['State','County'])
#     wandrerer_df = get_wandrer_totals_for_towns_for_state(state_list)
#     data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)
#     wandrerer_df['lcase_town'] = wandrerer_df['Town'].str.lower() # required for merge with Wandrer data
#
#     wandrer_diffs = wandrerer_df[~wandrerer_df['Town'].isin(town_gdf['Town'])]
#     wandrer_diffs_no_dupes = wandrer_diffs.drop_duplicates()
#     # wandrer_diffs_no_dupes_2 = wandrer_diffs.drop_duplicates(subset=['arena_id'])
#
#     # filter_list = ['State Park', 'Appalachian Trail', 'National Park']
#     filter_list = ['Appalachian Trail']
#     search_str = '|'.join(filter_list)
#     wandrer_diffs_filtered = wandrer_diffs[~wandrer_diffs['Town'].str.contains(search_str)]
#     if len(wandrer_diffs_filtered) > 0:
#         wandrer_diffs_filtered['DataSource'] = 'Wandrer'
#         selected_columns = ['DataSource', 'County', 'Town']
#         wandrer_diffs_filtered[selected_columns].to_csv(f'{state}-Wandrer-Missing-Town.csv', index=False)
#     # #
#     # json_diffs = town_gdf[~town_gdf['Town'].isin(wandrerer_df['Town'])]
#     # if len(json_diffs) > 0:
#     #     json_diffs['DataSource'] = 'json'
#     #     selected_columns = ['DataSource', 'Town']
#     #     json_diffs[selected_columns].to_csv(f'{state}-json-Missing-Town.csv', index=False)
#
#     # print(wandrerer_df)
#     town_merged_df = town_gdf.merge(wandrerer_df, on=['State','County','Town','long_name'])
#
#     # wandrerer_df['state_county'] = wandrerer_df['State'].str.replace(' ', '_').str.lower() + '_' + wandrerer_df['County'].str.lower()
#     # unincorporated_df = county_gdf.merge(wandrerer_df, on={'State', 'County'})
#     unincorporated_df = wandrerer_df[wandrerer_df['Town'] == 'Unincorporated']
#     # county_filtered_gdf = county_gdf[county_gdf['state_county'] == 'south_carolina_georgetown']
#     county_filtered_gdf = county_gdf.copy()
#     county_filtered_gdf.drop(['Town', 'long_name'], axis=1, inplace=True, errors='ignore')
#     # county_filtered_gdf.reset_index(inplace=True)
#     # unincorporated_df.reset_index(inplace=True)
#     # unincorporated_merged_df = county_filtered_gdf.merge(unincorporated_df, on=['State','County','Town','long_name'])
#     unincorporated_merged_df = county_filtered_gdf.merge(unincorporated_df, on=['State','County'])
#     if len(unincorporated_merged_df) > 0:
#         county_location_json = json.loads(unincorporated_merged_df.to_json())
#         unincorporated_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
#         unincorporated_merged_df['always_zero'] = 0
#         merged_county_df = unincorporated_merged_df
#         county_template = create_template(merged_county_df, ['County', 'Town', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
#
#     location_json = json.loads(town_merged_df.to_json())
#     # county_location_json = json.loads(county_gdf.to_json())
#     # county_gdf.drop(['geometry'], axis=1, inplace=True, errors='ignore')
#     zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
#     town_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
#     # town_merged_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
#     # county_template = create_template(county_gdf, ['County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
#     # county_gdf['TotalMiles'] = 0
#     # county_template = create_template(county_gdf, ['County', 'TotalMiles'])
#     z_max = float(town_merged_df[data_value].max()) if float(town_merged_df[data_value].max()) > 0 else float(town_merged_df['TotalMiles'].max())
#
#     st.session_state['map_gdf'] = town_merged_df
#     fig = go.Figure()
#     # fig = go.Figure(go.Choroplethmapbox(
#     fig.add_trace(
#         go.Choroplethmapbox(
#             customdata=merged_county_df,
#         geojson=county_location_json,
#         featureidkey='properties.County',
#         locations=merged_county_df['County'],
#         z=merged_county_df['always_zero'],
#         # z=1,
#         # colorscale='ylorrd',
#         colorscale=max_50_pct_color_scale,
#         zmin=0,
#         zmax=z_max,
#         hovertemplate=county_template,
#         # hoverlabel_bgcolor='white',
#         hoverlabel=dict(
#             bgcolor="black",
#             font_size=16),
#         marker_opacity=0.5,
#         marker_line_width=1.5,
#         visible=True
#         # colorbar_title=data_value
#     ))
#
#     town_template = create_template(town_merged_df, ['Town', 'County', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
#     fig.add_trace(
#         go.Choroplethmapbox(
#             customdata=town_merged_df,
#             geojson=location_json,
#             featureidkey='properties.Town',
#             locations=town_merged_df['Town'],
#             # z=filtered_df[z_col_name] * 100,
#             z=town_merged_df[data_value],
#             colorscale=max_50_pct_color_scale,
#             # hovertemplate="County: %{customdata[2]}<br>Actual Pct: %{customdata[4]}<extra></extra>",
#             hovertemplate=town_template,
#             # hoverlabel_bgcolor='white',
#             hoverlabel=dict(
#                 bgcolor="black",
#                 font_size=16),
#             marker_opacity=0.5,
#             name='Town Data Values',
#             # visible=map_feature_selected == 'Town Boundaries',
#             zmin=0,
#             zmax=z_max))
#
#     fig.update_layout(mapbox_layers=[dict(sourcetype='geojson',
#                                           source=county_location_json,
#                                           color='#303030',
#                                           type='line',
#                                           line=dict(width=1.5)
#                                           # hovertemplate=template
#                                           )]);
#
#     fig.update_layout(mapbox_style="carto-positron",
#                       mapbox_zoom=zoom, mapbox_center=center)
#     fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
#                             , title=dict(text=f'{data_value} for Towns in {state}', x=0.5
#                             , xanchor="center")
#                             )
#
#     return fig

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
    if column_exists_case_insensitive(town_merged_df, 'diagonal_x'):
        town_merged_df.rename(columns={'diagonal_x': 'diagonal'}, inplace=True)

    town_merged_df.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'Town_y', 'diagonal_y'
                            ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')

    county_gdf.drop(['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng'
                        ,'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'], axis=1, inplace=True, errors='ignore')
    # location_json = json.loads(town_merged_df.to_json())
    # county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    # town_merged_df.drop(['tags', 'geometry','lcase_town','arena_id','County','COUNTY'], axis=1, inplace=True, errors='ignore')
    # town_merged_df.rename(columns={'ShortCounty': 'County'}, inplace=True)
    if data_value == 'Award Level':
        z_max = 1
    else:
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
    fig = go.Figure(go.Choroplethmap(
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
    fig.update_layout(map_layers=[dict(sourcetype='geojson',
                                          source=county_location_json,
                                          color='#303030',
                                          type='line',
                                          line=dict(width=1.5)
                                          )]);

    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
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
    state_merged_df.drop(list(state_merged_df.filter(regex='NHD:')), axis=1, inplace=True)
    columns_to_drop = state_merged_df.select_dtypes(include=['datetime64']).columns
    state_merged_df.drop(columns=columns_to_drop, axis=1, inplace=True)
    location_json = json.loads(state_merged_df.to_json())
    # county_location_json = json.loads(county_gdf.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['geometry'], axis=1, inplace=True, errors='ignore')
    # template = create_template(state_merged_df, ['State', 'TotalTowns', 'TotalTownMiles', 'ActualTownMiles', 'ActualTownPct', 'Pct10Deficit', 'Pct25Deficit'])

    template_fields = ['State', 'TotalTowns', 'CycledTowns', 'PctTownsCycled',
                                                 'AchievedTowns', 'PctTownsAchieved',
                                                 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit']
    if any(state_merged_df['UnincorporatedMiles'] > 0):
        template_fields.extend(['TotalCountyMiles', 'TotalCountyMilesCycled', 'PctCountyMilesCycled',
                                'UnincorporatedMiles', 'UnincorporatedMilesCycled', 'PctUnincorporatedMilesCycled'])
    template = create_template(state_merged_df,template_fields)

    data_value = data_value.replace(' > 1', '')
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())

    st.session_state['map_gdf'] = state_merged_df
    fig = go.Figure(go.Choroplethmap(
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
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
    fig = fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1}
                            , title=dict(text=f'{data_value} for State of {state}', x=0.5
                            , xanchor="center")
                            )
    return fig


def create_county_gdf(source_osm_df):
    source_osm_df = source_osm_df.dropna(axis=1, how='all')
    county_gdf = source_osm_df.dissolve(by='County')
    county_gdf.reset_index(inplace=True)
    # if not column_exists_case_insensitive(source_osm_df, 'admin_level'):
    #     county_gdf = source_osm_df.dissolve(by='County')
    #     county_gdf.reset_index(inplace=True)
    #     # county_gdf.rename(columns={'COUNTY': 'County'}, inplace=True)
    #     # county_gdf['long_county'] = county_gdf['County'] + ' County'
    # else:
    #     county_gdf = source_osm_df[source_osm_df['admin_level'] == 6.0]
    #     county_gdf.rename(columns={'name': 'County'}, inplace=True)
    # # if not county_gdf.County.str.endswith(' County').all():
    # # if not column_exists_case_insensitive(county_gdf, 'long_county'):
    # #     # county_gdf['County'] += ' County'
    # #     county_gdf['long_county'] = county_gdf['County'] + ' County'
    # #     state = county_gdf['State'].unique()[0]
    # #     outfile = f'{state}_location.json'
    # #     gdf.to_file(outfile, driver="GeoJSON")

    convert_bounds_to_linestrings(county_gdf)

    county_gdf['County'] = county_gdf['County'].str.title() # required for merge with Wandrer data
    return county_gdf

def create_region_map(source_osm_df, region):
    renamed_gdf = {}
    county_gdf = {}
    # source_osm_df['State'] = state

    state_gdf = source_osm_df.dissolve(by='State')
    state_gdf.reset_index(inplace=True)
    convert_bounds_to_linestrings(state_gdf)

    wandrerer_df = get_wandrer_totals_for_states(state_gdf.State.to_list())
    data_value, wandrerer_df = filter_wandrerer_df(wandrerer_df)
    state_merged_df = state_gdf.merge(wandrerer_df, on='State')

    state_merged_df.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')

    location_json = json.loads(state_merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(state_gdf.bounds)
    state_merged_df.drop(['tags', 'geometry','COUNTY','name','Town'], axis=1, inplace=True, errors='ignore')
    template = create_template(state_merged_df, ['State', 'TotalTowns', 'CycledTowns', 'PctTownsCycled', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    z_max = float(state_merged_df[data_value].max()) if float(state_merged_df[data_value].max()) > 0 else float(state_merged_df['TotalMiles'].max())
    st.session_state['map_gdf'] = state_merged_df

    fig = go.Figure(go.Choroplethmap(
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
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)

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
    template_fields = get_template_field_list_for_county_scope_map(merged_df)

    template = create_template(merged_df, template_fields)
    # template = create_template(merged_df, ['State', 'County', 'TotalTowns', 'TotalTownMiles', 'ActualMiles', 'ActualPct', 'Pct10Deficit', 'Pct25Deficit'])
    if data_value == 'TotalMiles':
        data_value = 'TotalCountyMiles'

    z_max = float(merged_df[data_value].max()) if float(merged_df[data_value].max()) > 0 else float(merged_df['TotalCountyMiles'].max())
    z_min =  1000 if data_value == 'TotalMiles' else 0

    st.session_state['map_gdf'] = merged_df

    fig = go.Figure(go.Choroplethmap(
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
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)
    fig.update_layout(map_layers=[dict(sourcetype='geojson',
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
    threshold = 1
    selected_data_value = ss['selected_datavalue_for_map']
    data_value = ''
    if selected_data_value == 'ActualMiles >= 1':
        miles_cycled_column_name = 'TotalCountyMilesCycled' if wandrerer_df.columns.__contains__('TotalCountyMilesCycled') else 'ActualMiles'
        wandrerer_df = wandrerer_df.loc[wandrerer_df[miles_cycled_column_name] >= threshold]
        data_value = 'ActualMiles'
    elif selected_data_value == 'ActualMiles < 1':
        wandrerer_df = wandrerer_df[wandrerer_df['ActualMiles'] < 1]
        miles_cycled_column_name = 'TotalCountyMilesCycled' if wandrerer_df.columns.__contains__('TotalCountyMilesCycled') else 'ActualMiles'
        data_value = 'ActualMiles'
    else:
        data_value = selected_data_value

    return data_value, wandrerer_df


def get_unneeded_column_names():
    # unneeded_column_names =  ['name_en', 'label_node_id', 'label_node_lat', 'label_node_lng', 'admin_centre_node_id'
    #     , 'admin_centre_node_lat', 'admin_centre_node_lng'
    #     , 'admin_centre_node_id', 'admin_centre_node_lat', 'admin_centre_node_lng'
    #     , 'NAME', 'MCD', 'KEY', 'DCF_OFFICE', 'DCF_REGION'
    #     , 'FIPS6', 'TOWN', 'TOWNNAMEMC', 'TOWNGEOID', 'SqMi'
    #     , 'OBJECTID', 'CNTY', 'CNTYGEOID', 'LAND'
    #     , 'osm_id', 'boundary', 'NAME', 'MCD', 'KEY', 'DCF_OFFICE', 'DCF_REGION'
    #     , 'GEOCODE', 'GEOCODENUM', 'CNTYCODE', 'TAG', 'ISLAND', 'CIREG', 'LURC', 'BAXTER', 'ISLANDID', 'TYPE'
    #     , 'DOT_REGNUM', 'DOT_REGION', 'GlobalID', 'created_user'
    #     , 'created_date', 'last_edited_user', 'last_edited_date','CountyArenaId','StateArenaId'
    #     ]

    unneeded_column_names = []
    return unneeded_column_names


def get_geojson_filenames():
    filter = ''
    if st.session_state.selected_region != 'All':
        filter = f'''and subregion_name = "{st.session_state.selected_region}"'''

    query = f'''select State, geojson_filename from vw_state_geo_data
    where geojson_filename is not NULL
    {filter}
    order by State'''
    # print(query)
    df = execute_query(query)
    result = df.set_index('State')['geojson_filename'].to_dict()
    st.session_state.geojson_files_dict = result
    return result

def get_geojson_filenames_for_region():
    # if 'geojson_files_dict' not in st.session_state:
    filter = ''
    if st.session_state.selected_region != 'All':
        filter = f'''and subregion_name = "{st.session_state.selected_region}"'''

    print("Getting geojson filenames from db.")
    query = f'''select sm.subregion_name, st.arena_name as State, agd.geojson_filename 
        from subregion_mapping sm
        inner join arena st on st.arena_id = sm.child_arena_id
        inner join arena_geo_data agd on agd.arena_id = st.arena_id
        where agd.geojson_filename is not null
        {filter}
        order by State'''

    print(query)
    df = execute_query(query)
    result =  df.set_index('State')['geojson_filename'].to_dict()
    st.session_state.geojson_files_dict = result
    return result

def get_wandrer_totals_for_states(states):
    dfs = pd.DataFrame()

    for state in states:
        if dfs.empty:
            dfs = get_wandrer_totals_for_state(state)
        else:
            dfs = pd.concat([dfs, get_wandrer_totals_for_state(state)])

    return dfs

def get_wandrer_totals_for_state(state):
    query = f'''select Region, Country, State, sum(TotalTowns) as TotalTowns
		, sum(CycledTowns) as 'CycledTowns', sum(cast(CycledTowns as real))/sum(cast(TotalTowns as real)) as 'PctTownsCycled'
		, sum(AchievedTowns) as 'AchievedTowns', sum(cast(AchievedTowns as real))/sum(cast(TotalTowns as real)) as 'PctTownsAchieved'
		, sum(TotalTownMiles) as TotalMiles
        , sum(ActualMiles) as 'ActualMiles', sum(ActualMiles)/sum(TotalTownMiles) as 'ActualPct'
        , CASE WHEN sum(Pct10Deficit) < 0 THEN 0 ELSE sum(Pct10Deficit) END as 'Pct10Deficit'
        , CASE WHEN sum(Pct25Deficit) < 0 THEN 0 ELSE sum(Pct25Deficit) END as 'Pct25Deficit'
		, sum(UnincorporatedMiles) as UnincorporatedMiles
		, sum(UnincorporatedMilesCycled) as UnincorporatedMilesCycled
		, sum(UnincorporatedMilesCycled) / sum(UnincorporatedMiles) as PctUnincorporatedMilesCycled
    	from vw_county_aggregates
    	where State = "{state}"'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_totals_for_counties_for_states(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select Region, Country, State, long_county as LongCounty
		, County
		, StateArenaId, CountyArenaId, arena_short_name
        , TotalTowns, CycledTowns, PctTownsCycled, TotalTownMiles, ActualPct, ActualMiles, AchievedTowns
        , PctTownsAchieved
 		, Pct0_Count as '0%', LT_1_Mile_Count as '< 1 mile', LT_5Pct_Count as '< 5%', Pct5_Count as '5%', Pct10_Count as '10%'
 		, Pct25_Count as '25%', Pct50_Count as '50%', Pct75_Count as '75%', Pct90_Count as '90%', Pct99_Count as '99%'
        , Pct10, Pct25, Pct50, Pct75
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , Pct50Deficit, Pct75Deficit, Pct90Deficit
        , UnincorporatedMiles, PctUnincorporatedMilesCycled, UnincorporatedMilesCycled
        , TotalCountyMiles
-- 		, TotalCountyMilesCycled, PctCountyMilesCycled
		from vw_county_aggregates 
    	where State in {states_in_str}
    	order by region, country, State, County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df


def get_wandrer_totals_for_counties_for_states_v2(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select *
		from vw_county_aggregates 
    	where State in {states_in_str}
    	order by region, country, State, County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_unincorporated_totals_for_counties_for_states(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select Region, Country, State, County
	, length as 'UnincorporatedMiles'
	, percentage as 'PctUnincorporatedMilesCycled'
	, ActualLength as 'UnincorporatedMilesCycled'
	from vw_current_town_data
	where name = 'Unincorporated'
	and State in {states_in_str}
	order by region, country, State, County'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def get_wandrer_unincorporated_aggregates_for_counties_for_states(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select Region, Country, State, County
	, StateArenaId, CountyArenaId
	, TotalTowns, CycledTowns, AchievedTowns, TotalTownMiles, PctTownsCycled, PctTownsAchieved
	, ActualPct, ActualMiles, Pct10, Pct25, Pct50, Pct75
	, CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
	, CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
	, Pct50Deficit, Pct75Deficit, Pct90Deficit
    , UnincorporatedMiles, PctUnincorporatedMilesCycled, UnincorporatedMilesCycled
    , TotalCountyMiles, TotalCountyMilesCycled, PctCountyMilesCycled
	from vw_unincorporated_aggregates
	where State in {states_in_str}
	order by region, country, State, County'''
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
    query = f'''select distinct fqtn.Region, fqtn.Country, fqtn.State, REPLACE(fqtn.County, ' County', '') as County
        , CASE WHEN fqtn.name = "Unincorporated" THEN fqtn.name || " " || fqtn.County ELSE fqtn.name END as Town
		, fqtn.County as LongCounty, fqtn.long_name, fqtn.CountyLongName, town.parent_arena_id as CountyParentArenaId
		, round(fqtn.length, 7) as TotalMiles
		, round(fqtn.percentage, 7) as ActualPct, round(fqtn.ActualLength, 7) as ActualMiles
		, round(fqtn.Pct10, 7) as Pct10, round(fqtn.Pct25, 7) as Pct25, round(fqtn.Pct50, 7) as Pct50
        , round(fqtn.Pct75, 7) as Pct75, round(fqtn.Pct90, 7) as Pct90, fqtn.awarded
 		, CASE 
			WHEN fqtn.percentage <= 0 then '0%' 
	-- 		WHEN fqtn.percentage > 0 and fqtn.percentage <= .10 then '0%' 
			WHEN fqtn.percentage > 0 and fqtn.ActualLength < 1 then '< 1 mile'
			WHEN fqtn.percentage < .05 and fqtn.ActualLength > 1 then '< 5%'
			WHEN fqtn.percentage <= .10 and fqtn.ActualLength >= 1 then '5%' 
			WHEN fqtn.percentage > .10 and fqtn.percentage < .25 then '10%'
			WHEN fqtn.percentage >= .25 and fqtn.percentage < .50 then '25%'
			WHEN fqtn.percentage >= .50 and fqtn.percentage < .75 then '50%'
			WHEN fqtn.percentage >= .75 and fqtn.percentage < .90 then '75%'
			WHEN fqtn.percentage >= .90 and fqtn.percentage < .99 then '90%'
			WHEN fqtn.percentage >= .99 then '99%'
--			ELSE '0%'
		END as 'Award Level'
        , CASE WHEN fqtn.Pct10Deficit < 0 THEN 0 ELSE round(fqtn.Pct10Deficit, 7) END as Pct10Deficit
        , CASE WHEN fqtn.Pct25Deficit < 0 THEN 0 ELSE round(fqtn.Pct25Deficit, 7) END as Pct25Deficit
        , round(fqtn.Pct50Deficit, 7) as Pct50Deficit, round(fqtn.Pct75Deficit, 7) as Pct75Deficit
        , round(fqtn.Pct90Deficit, 7) as Pct90Deficit
		, fqtn.geometries_visible, fqtn.diagonal, fqtn.user_id, town.seacoast, town.osm_id
        from arena_badge town
		inner join vw_current_town_data fqtn on fqtn.id = town.id 
        where fqtn.state in {in_statement}
        order by 'Award Level', fqtn.region, fqtn.country, fqtn.state, fqtn.county, fqtn.name'''
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


def get_wandrer_regions():
    query = f'''select sm.subregion_name, st.arena_name as State, agd.geojson_filename 
	from subregion_mapping sm
	inner join arena st on st.arena_id = sm.child_arena_id
	inner join arena_geo_data agd on agd.arena_id = st.arena_id
	where agd.geojson_filename is not null'''
    # print(query)
    wandrerer_df = execute_query(query)
    return wandrerer_df

def execute_query(query):
    db_path = db.get_db_path()

    try:
        conn = sqlite3.connect(db_path)
        wandrerer_df = pd.read_sql_query(query, conn)
        return wandrerer_df
    except Exception as error:
        print(f'{error=}')
        print(f'Unable to open {db_path}')



# def update(key, ):
#     # print(f'update: ss[{key}] = {ss.select_state}')
#     # print(f'update: preserve_map_selection = {ss.preserve_map_selection}')
#     if key == 'select_map' and ss.preserve_map_selection:
#         value = None
#         ss[key] = value

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
    file_name = st.session_state.geojson_files_dict[selected_state]
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
        convert_bounds_to_linestrings(gdf)
        st.session_state.gdfs[selected_state] = gdf
        if not column_exists_case_insensitive(gdf, 'normalized'):
            county_gdf, gdf = normalize_geojson(selected_state, gdf)

        columns_to_drop = gdf.select_dtypes(include=['datetime64']).columns
        gdf.drop(columns=columns_to_drop, axis=1, inplace=True)
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
        for state in st.session_state.geojson_files_dict.keys():
            gdf = get_geopandas_df_for_state(state)
            gdf = clean_gdf(gdf)
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

def to_jaden_case(sentence):
    if sentence is None:
        return sentence

    return " ".join(word.capitalize() for word in sentence.split())


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
        gdf['Town'] = gdf.apply(lambda x: to_jaden_case(x['Town']), axis=1)
        gdf['County'] = gdf.apply(lambda x: to_jaden_case(x['County']), axis=1)
        # gdf['Town'] = gdf['Town'].apply(to_jaden_case(gdf['Town']))
        # gdf['County'] = gdf['County'].apply(to_jaden_case(gdf['County']))

        gdf_none = gdf[gdf['County'].isnull()]
        gdf_not_none = gdf[~gdf['County'].isnull()]

        gdf.drop(get_unneeded_column_names(), axis=1, inplace=True, errors='ignore')
        # if not column_exists_case_insensitive(gdf, 'long_name'):
        # It's OK ot overwrite long_name as we've changed the inputs to it.

        if len(gdf_none) > 0:
            wandrer_df = get_wandrer_data_for_county_merge(state)
            wandrer_df_merged = gdf_none.merge(wandrer_df, on=['State','Town'])
            wandrer_df_merged.drop(['County_x', 'long_name_x', 'long_county_x', 'long_county_y'], axis=1, inplace=True,
                                   errors='ignore')
            rename_column_case_insensitive(wandrer_df_merged, 'County_y', 'County')
            rename_column_case_insensitive(wandrer_df_merged, 'long_name_y', 'long_name')
            wandrer_df_merged['long_county'] = wandrer_df_merged['County'] + ' County'
            gdf = wandrer_df_merged
        else:
            gdf['long_name'] = (
                gdf['State'] + '_' + gdf['County'] + '_County_' + gdf['Town'].str.replace(' ', '_')).str.lower()
            gdf['long_county'] = gdf['County'] + ' County'

        # else:
        #     gdf['long_name'] = (gdf['State'] + '_' + gdf['County'] + '_County').str.lower()

        # if not column_exists_case_insensitive(gdf, 'long_county'):
        # It's OK ot overwrite long_name as we've changed the inputs to it.
        # county_gdf['County'] += ' County'
        # gdf['long_county'] = gdf['County'] + ' County'
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
            wandrer_df = get_wandrer_data_for_county_merge(state)

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


def get_wandrer_data_for_county_merge(state):
    wandrer_df = get_fq_town_name_for_state(state)
    if len(wandrer_df['County'].str.contains(' County')):
        rename_column_case_insensitive(wandrer_df, 'County', 'long_county')
        wandrer_df['County'] = wandrer_df['long_county'].str.replace(' County', '')
    return wandrer_df

def center_point_diagonal(diagonal):
    """
    Calculates the center point of a line segment defined by two points.

    Args:
        point1: A tuple representing the coordinates of the first point (x1, y1).
        point2: A tuple representing the coordinates of the second point (x2, y2).

    Returns:
        A tuple representing the coordinates of the center point (x_center, y_center).
    """
    diagonal_json = json.loads(diagonal)
    point1 = diagonal_json['coordinates'][0]
    point2 = diagonal_json['coordinates'][1]
    x1, y1 = point1
    x2, y2 = point2
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    return (x_center, y_center)


def town_selected():
    # st.plotly_chart(st.session_state.current_fig, config=config)
    fig = st.session_state.current_fig
    if len(st.session_state.map_data['selection']['rows']) == 0:
        st.plotly_chart(fig)
        st.dataframe(st.session_state['map_gdf'], use_container_width=True, selection_mode='single-row'
                     , key='map_data', on_select=town_selected)
        return

    diagonal = st.session_state['map_gdf'].iloc[st.session_state.map_data['selection']['rows'][0]]['diagonal']
    # x_center, y_center = center_point_diagonal(diagonal)
    zoom, center = calculate_mapbox_zoom_center_from_diagonal(diagonal)
    # st.write(f'{diagonal=}')
    # st.write(f'{zoom=}')
    # st.write(f'{center=}')
    # center = dict(lat=(min_lat + max_lat) / 2, lon=(min_lon + max_lon) / 2)
    fig.update_layout(map_style="carto-positron",
                      map_zoom=zoom, map_center=center)

    # fig.update_layout(mapbox_style="carto-positron",
    #                   mapbox_zoom=zoom, mapbox_center=center,
    #                   config={'mapbox_scrollZoom':True})

    fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1})
    # fig.conf = dict(scrollZoom=True)

    st.plotly_chart(fig)

    if st.session_state.logged_in:
        st.session_state.update_county = st.session_state['map_gdf'].iloc[st.session_state.map_data['selection']['rows'][0]]['County']
        st.session_state.show_update_county_btn = True
        # st.sidebar.button(f'Update {county} County Miles', key="update_county_btn")
        #     # st.write('Update button clicked')

    st.dataframe(st.session_state['map_gdf'], use_container_width=True, selection_mode='single-row'
                 , key='map_data', on_select=town_selected)
    # town = st.session_state['map_gdf'].iloc[st.session_state.map_data['selection']['rows'][0]]['Town']
    # st.write(f'{town=}')
    # st.write(st.session_state.map_data)

# ss

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#
# if not st.session_state.logged_in:
# #     # Render widgets that should be visible when logged in
# #     st.write("This is visible when logged in")
# #     st.button("Click me (logged in)")
# # else:
#     # Render login form or other content for non-logged-in users
#     st.write("Please log in")
#     if st.button("Login"):
#         # Simulate login success
#         st.session_state.logged_in = True
#         st.exp

st.html(
    '''
        <style>
            div[aria-label="dialog"]>button[aria-label="Close"] {
                display: none;
            }
        </style>
    '''
)

@st.dialog("Login")
def login():
    st.write("Login for full access or Cancel to for normal access.")
    password = st.text_input('password', autocomplete="off", type='password', )
    col1, col2 = st.columns(2)

    with col1:
        button1 = st.button('Submit', key='submit')

    with col2:
        button2 = st.button('Cancel', key= 'cancel')

    st.write('About:')
    st.write(f'python version: {sys.version}')
    if button1:
        if password == st.secrets["password"]:
            logged_in()
        else:
            st.write('Invalid password')

    if button2:
        st.session_state.login_dismissed = True
        st.rerun()


def logged_in():
    st.session_state.logged_in = True
    st.rerun()

def main():
    # ss

    if 'show_update_county_btn' not in st.session_state:
        st.session_state.show_update_county_btn = False

    if 'gdfs' not in st.session_state:
        # Initialize geopandas df dictionary in session state.
        st.session_state.gdfs = {}

    if 'current_fig' not in st.session_state:
        st.session_state.current_fig = {}

    options = ['State', 'Counties', 'Towns', 'Seacoast Towns']

    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'All'

    if 'wandrer_regions' not in st.session_state:
        st.session_state.wandrer_regions = get_wandrer_regions()

    region_list = ['All'] + (st.session_state.wandrer_regions.subregion_name.unique().tolist())
    geojson_files = get_geojson_filenames_for_region()
    data_values = ['TotalMiles', 'ActualMiles', 'ActualMiles < 1', 'ActualMiles >= 1', 'ActualPct', 'Award Level', 'Pct10Deficit', 'Pct25Deficit']

    if 'gdfs' not in st.session_state:
        # Initialize geopandas df dictionary in session state.
        st.session_state.gdfs = {}

    if 'current_fig' not in st.session_state:
        st.session_state.current_fig = {}

    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'All'

    if 'update_county_btn' not in st.session_state:
        st.session_state.update_county_btn = False

    if st.session_state.update_county_btn:
        update_county_data()

    with st.sidebar:
        region_selectbox = st.selectbox('Select a region:', region_list, key='selected_region', index=0, on_change=region_selected())
        state_selectbox = st.selectbox('Select a location (US State):', get_geojson_filenames_for_region().keys(), key='selected_state', index=None)
        # preserve_map_selection = st.checkbox('Clear map type selection on state change', key='preserve_map_selection')
        maptype_selectbox = st.selectbox('Select a map type:', options, key='selected_map_type', index=None)
        datavalue_selectbox = st.selectbox('Select a data value', data_values, key='selected_datavalue_for_map', index=None, on_change=enable_make_map())
        make_map = st.button('Generate map', key='make_map_btn', disabled=st.session_state.get("make_map_disable", True))
        if st.session_state.show_update_county_btn:
            county = st.session_state.update_county
            if st.button(f'Update {county} County Miles', key="update_county_btn"):
                st.session_state.show_update_county_btn = False

    if make_map:
        st.session_state.show_update_county_btn = False
        osm_gdf = {}
        fig = {}

        if state_selectbox:
            osm_gdf = get_geopandas_df_for_state(state_selectbox)
            match maptype_selectbox:
                case 'State':
                    fig = create_state_map(osm_gdf.copy(), state_selectbox)
                case 'Counties':
                    # fig = create_county_map(osm_gdf.copy(), state_selectbox)
                    fig = create_county_map_v2(osm_gdf.copy(), state_selectbox)
                case 'Towns' |'Seacoast Towns':
                    fig = create_town_map(osm_gdf.copy(), state_selectbox, maptype_selectbox)
        else:
            osm_state_gdf, osm_county_gdf = get_geopandas_df_for_region(region_selectbox)
            match maptype_selectbox:
                case 'State':
                    fig = create_region_map(osm_state_gdf.copy(), region_selectbox)
                case 'Counties':
                    fig = create_region_by_county_map(osm_county_gdf.copy(), region_selectbox)
                case 'Towns':
                    fig = create_region_by_town_map(osm_state_gdf.copy(), region_selectbox)

        if fig:
            config = {"scrollZoom": True}
            st.session_state.current_fig = fig
            st.plotly_chart(fig, config=config)
            st.write('Raw Data')
            # st.dataframe(osm_gdf, use_container_width=True)
            st.dataframe(st.session_state['map_gdf'], use_container_width=True, selection_mode='single-row'
                     ,key='map_data', on_select=town_selected)
        else:
            st.write(f'{maptype_selectbox} map unavailable for {state_selectbox}')


def add_arena_mileage_to_df(url, username, password, update_datetime, user_id, df_children_arena_summaries):
    for index, row in df_children_arena_summaries.iterrows():
        print(f"Index: {index}, Row: {row['arena_short_name']}")
        separator = '/'
        url_elements = url.split(separator)
        parent_arena = url_elements[4]
        url_elements[4] = row['arena_short_name']
        child_url = separator.join(url_elements)
        # if url.count(parent_arena) > 1:
        #     child_url = url.replace(parent_arena, row['arena_short_name'])
        # else:
        #     child_url = url.replace(parent_arena, row['arena_short_name'])
        print(f'{child_url}=')
        response = requests.get(child_url, auth=(username, password))
        arena_mileage = response.json()['arena_mileage']
        df_children_arena_summaries.loc[index,('arena_mileage')] = arena_mileage


def get_data_from_url(url, username, password, update_datetime, parent_arena_id, arena_type, user_id):
    response = requests.get(url, auth=(username, password))
    total = response.json()['total']
    awarded = response.json()['awarded']
    # TODO: enable this line if arena_mileage is ever returned from this call.
    arena_mileage = response.json()['arena_mileage']
    response_json = response.json()
    arena_badges = response_json['arena_badges']
    children_arena_summaries = response_json['children_arena_summaries']
    print(f'{arena_type=}, {len(arena_badges)=}, {len(children_arena_summaries)=}')

    results = {}
    if len(arena_badges)>0:
        df_arena_badges = pd.json_normalize(response_json['arena_badges'])
        df_arena_badges['update_datetime'] = str(update_datetime)
        df_arena_badges['arena_type'] = 'town'
        df_arena_badges['user_id'] = user_id
        if (parent_arena_id):
            df_arena_badges['parent_arena_id'] = parent_arena_id
        if df_arena_badges.duplicated().to_list().count(True) > 0:
            print(df_arena_badges.duplicated())
        results['arena_badges'] = df_arena_badges.to_json()


    if len(children_arena_summaries)>0:
        df_children_arena_summaries = pd.json_normalize(response_json['children_arena_summaries'])
        df_children_arena_summaries['update_datetime'] = str(update_datetime)
        df_children_arena_summaries['arena_type'] = arena_type
        df_children_arena_summaries['user_id'] = user_id
        if (parent_arena_id):
            df_children_arena_summaries['parent_arena_id'] = parent_arena_id
        if df_children_arena_summaries.duplicated().to_list().count(True) > 0:
            print(df_children_arena_summaries.duplicated())
        if 'arena_mileage' not in df_children_arena_summaries.columns:
            add_arena_mileage_to_df(url, username, password, update_datetime, user_id, df_children_arena_summaries)
        results['children_arena_summaries'] = df_children_arena_summaries.to_json()

    return results, total, awarded, arena_mileage


def get_child_df(url, arena_type, athlete_id):
    # if 'selected_region' not in st.session_state or ss['selected_region'] == None:
    #     # ss['selected_region'] = region_select_box
    #     print('selected_region not in st.session_state')
    #     return
    #
    # print(ss['selected_region'])

    # add these fields to secrets.toml
    username = 'kk4sites@hotmail.com'
    password = 'A11Wh0Wand3r'

    update_datetime = datetime.now()
    results, total, awarded, arena_mileage = get_data_from_url(url, username, password,
                                 update_datetime, None, arena_type,
                                 athlete_id)
    return results, total, awarded, arena_mileage


def update_county_data():
    st.session_state.show_update_county_btn = False
    county_row = st.session_state['map_gdf'].iloc[st.session_state.map_data['selection']['rows'][0]]

    # county = county_row['County']
    # county = county_row['long_name'].replace(county_row['Town'].lower(), '')[:-1]
    county = county_row['CountyLongName']
    county_parent_arena_id = county_row['CountyParentArenaId']
    # print(f'\n{county} URL')

    # don't hardcode these variables...
    achievement_type = 'bike'
    user_id = int(county_row['user_id'])

    url = f'https://wandrer.earth/a/{county}/explorer_achievements?athlete_id={user_id}&at={achievement_type}'
    results, total, awarded, arena_mileage = get_child_df(url, 'county', user_id)
    # county_data = {'arena_id': [county_parent_arena_id],
    #                'total': [total],
    #                'awarded': [awarded],
    #                'arena_mileage': [arena_mileage],
    #                'arena_short_name': county_row['CountyLongName'],
    #                'user_id': county_row['user_id'],
    #                'distance_mi': 0,
    #                'update_datetime': datetime.now()}
    # county_df = pd.DataFrame(county_data)

    update_county_query = f'''update arena 
        set total = {total}, awarded = {awarded}, arena_mileage = {arena_mileage}, update_datetime = "{datetime.now()}" 
 	    where arena_id = {county_parent_arena_id} and user_id = {user_id}
	    and (total <> {total} or awarded <> {awarded} or arena_mileage <> {arena_mileage})
    '''

    county_message = f'Upserting data for {county_row["County"]} County'

    town_df = pd.read_json(StringIO(results['arena_badges']))
    # county_total, county_awarded, county_arena_badges, town_df = get_county_data_from_url(county_url, username,
    #                                                                                       password,
    #                                                                                       update_datetime,
    #                                                                                       county_parent_arena_id,
    #                                                                                       'town', athlete_id)
    # town_df.drop_duplicates()
    town_df.drop('icon', axis=1, inplace=True)
    town_df['parent_arena_id'] = county_parent_arena_id
    town_message = f'Upserting towns for {county_row["County"]} County'

    conn = None
    try:
        db_path = db.get_db_path()
        conn = db.create_connection(db_path)
        cursor = conn.cursor()
        db.save_dataframe(conn, town_df, 'arena_badge', town_message)
        print(f'Completed {town_message}')
        # db.save_dataframe(conn, county_df, 'arena_xx', county_message)
        db.execute_update_query(conn, update_county_query)
        print(f'Completed {county_message}')
        st.write(f'{county} Wandrer data updated. Click Generate Map to regenerate the map')
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error updating {county}: {e}')
        conn.rollback()
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        if conn:
            conn.rollback()
    finally:
        # Close connection
        if conn:
            conn.close()
            print('Database connection closed.')



# ss


# startup code
if "startup_msg_displayed" not in st.session_state:
    st.session_state.startup_msg_displayed = False

if "logged_in" not in st.session_state and "login_dismissed" not in st.session_state:
    st.session_state.logged_in = False
    login()
# else:
#     f"You voted for {st.session_state.vote['item']} because {st.session_state.vote['reason']}"

# if "logged_in" in st.session_state and "login_dismissed" in st.session_state:
if not st.session_state.startup_msg_displayed:
    if ("login_dismissed" in st.session_state and "login_dismissed" in st.session_state):
        st.write("Continuing to app as normal user...")
        st.session_state.startup_msg_displayed = True
        main()
    elif "logged_in" in st.session_state and st.session_state.logged_in:
            st.write("Continuing to app as privileged user...")
            st.session_state.startup_msg_displayed = True
            main()
elif st.session_state.startup_msg_displayed:
    main()



