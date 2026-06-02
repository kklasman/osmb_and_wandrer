import logging

import pandas as pd
import streamlit as st
from streamlit import session_state as ss
import geopandas_functions as gf
from geopy import distance
import plotly.graph_objects as go
import geopandas as gpd
import json
import logging_functions as lf
import math
import numpy as np
import os
import utilities as u
import wandrer_database as wd
# from area import area

max_50_pct_color_scale = ['white', 'gold', 'red']


def create_template(data, col_names):
    template = ''
    for idx, name in enumerate(col_names):
        try:
            if name == 'awarded':
                template += "<b>Awarded:</b> %{" + f"customdata[{data.columns.get_loc('awarded')}]" + "}<br>"

            elif name == 'Award Level':
                template += "<b>Award Level:</b> %{" + f"customdata[{data.columns.get_loc('Award Level')}]" + "}<br>"

            elif name == 'Region':
                template += "<b>Region:</b> %{" + f"customdata[{data.columns.get_loc('Region')}]" + "}<br>"

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

            elif name == 'name':
                template += "<b>Name:</b> %{" + f"customdata[{data.columns.get_loc('name')}]" + "}<br>"

            elif name == 'Location':
                template += "<b>Location:</b> %{" + f"customdata[{data.columns.get_loc('Location')}]" + "}<br>"

            elif name == 'StateMiles':
                template += "<b>Total State Miles:</b> %{" + f"customdata[{data.columns.get_loc('StateMiles')}]:,.2f" + "}<br>"

            elif name == 'TotalMiles':
                template += "<b>Total Town Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalMiles')}]:,.2f" + "}<br>"

            elif name == 'TotalCountyMiles':
                template += "<b>Total County Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalCountyMiles')}]:,.2f" + "}<br>"

            elif name == 'TotalCountyMilesCycled':
                template += "<b>Total County Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('TotalCountyMilesCycled')}]:,.2f" + "}<br>"

            elif name == 'PctCountyMilesCycled':
                template += "<b>Pct County Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctCountyMilesCycled')}]:,.2%" + "}<br>"

            elif name == 'PctMilesCycled':
                template += "<b>Pct Miles Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctMilesCycled')}]:,.2%" + "}<br>"

            elif name == 'TotalTownMiles':
                template += "<b>Total Town Miles:</b> %{" + f"customdata[{data.columns.get_loc('TotalTownMiles')}]:,.2f" + "}<br>"

            elif name == 'LocationMiles':
                template += "<b>Location Miles:</b> %{" + f"customdata[{data.columns.get_loc('LocationMiles')}]:,.2f" + "}<br>"

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

            elif name == 'TownsAwarded':
                template += "<b>Towns Awarded:</b> %{" + f"customdata[{data.columns.get_loc('TownsAwarded')}]" + "}<br>"

            elif name == 'Pct10Achieved':
                template += "<b>10%+ Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('Pct10Achieved')}]" + "}<br>"

            elif name == 'Pct5_Count':
                template += "<b>5% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct5_Count')}]" + "}<br>"

            elif name == 'Pct10_Count':
                template += "<b>10% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct10_Count')}]" + "}<br>"

            elif name == 'Pct25_Count':
                template += "<b>25% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct25_Count')}]" + "}<br>"

            elif name == 'Pct50_Count':
                template += "<b>50% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct50_Count')}]" + "}<br>"

            elif name == 'Pct75_Count':
                template += "<b>75% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct75_Count')}]" + "}<br>"

            elif name == 'Pct90_Count':
                template += "<b>90% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct90_Count')}]" + "}<br>"

            elif name == 'Pct99_Count':
                template += "<b>99% Count:</b> %{" + f"customdata[{data.columns.get_loc('Pct99_Count')}]" + "}<br>"

            elif name == 'PctTownsCycled':
                template += "<b>Pct Towns Cycled:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsCycled')}]:.2%" + "}<br>"

            elif name == 'AchievedTowns':
                template += "<b>Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('AchievedTowns')}]" + "}<br>"

            elif name == 'PctTownsAchieved':
                template += "<b>Pct Towns Achieved:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsAchieved')}" + "]:.2%}<br>"

            elif name == 'PctTownsAwarded':
                template += "<b>Pct Towns Awarded:</b> %{" + f"customdata[{data.columns.get_loc('PctTownsAwarded')}" + "]:.2%}<br>"

            else:
                print(f'Column {name} not found')
        except KeyError:
            print(f'Column {name} not found')

    template += "<extra></extra>"

    return template


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


def sq_m_to_sq_miles(sq_m):
    return sq_m / 2589988.11


def create_choropleth_map_with_legend(state_list):
    # st.write("filename:", geojson_file)
    # ss.gdfs = {}

    fig = go.Figure()

    data_value = ss.selected_datavalue_for_map

    gdf = gf.get_geopandas_df_for_region(state_list)
    gdf.set_crs("EPSG:4326", inplace=True)

    nf = 'New England National Forests.geojson'
    # nf = 'GMNF-edited_split_to_file.geojson'
    nf_filename = os.path.join('POIs', nf)
    print(ss.base_dir)
    print(f'{nf_filename}')
    # nf_filename = os.path.join('POIs', 'WMNT-edited_split-2nd-feature.geojson')
    national_forests_filepath = u.get_filepath_for_filename(nf_filename)
    gdf_national_forests, nf_size = gf.get_geopandas_df_for_state(ss.selected_state, national_forests_filepath)
    gdf_national_forests['value'] = 10 # TO DO: Replace with real Wandrer value when/if available.

    if 'leisure' in gdf.columns:
        mask = (gdf['leisure'].isna()) & (gdf.geom_type.isin(['Polygon', 'MultiPolygon']))
        gdf_towns = gdf[mask]
        gdf_leisure = gdf[~mask]

        mask2 = gdf_leisure.geom_type.isin(['Polygon', 'MultiPolygon'])
        gdf_parks = gdf_leisure[mask2]
        gdf_trails = gdf_leisure[~mask2]
        # gdf_leisure = gdf.query('leisure.notna()')
        # gdf_towns = gdf[(gdf['leisure'].isna()) & (gdf.geom_type.isin(['Polygon', 'MultiPolygon']))]
    else:
        gdf_towns = gdf[(gdf.geom_type.isin(['Polygon', 'MultiPolygon']))]

    # # state_list = gdf_towns['State'].unique().tolist()
    # wandrerer_df = wd.get_wandrer_totals_for_towns_for_state(state_list)
    # if wandrerer_df['osm_id'].isnull().all():
    #     # old format towns without osm_id values
    #     # town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State','County', 'Town','long_name'])
    #     wandrerer_df['long_name'] = wandrerer_df['long_name'].str.replace('_', '-')
    #     gdf_towns['long_name'] = gdf_towns['long_name'].str.replace('_', '-')
    #     # town_merged_df = gdf_towns.merge(wandrerer_df, on=['long_name', 'State','County', 'Town'])
    #     # prefer fields from left df because right has null osm_id. Both have diagonal.
    #     town_merged_df = pd.merge(gdf_towns, wandrerer_df, on=['long_name', 'State','County', 'Town'], how='left', suffixes=(None, '_r'))
    #     town_merged_df.drop('osm_id', axis=1, inplace=True, errors='ignore')
    #     suffix_to_drop = '_r'
    #     cols_to_drop = [col for col in town_merged_df.columns if col.endswith(suffix_to_drop)]
    #     town_merged_df.drop(columns=cols_to_drop, inplace=True)
    # else:
    #     # new format towns with osm_id values
    #     wandrerer_df['osm_id'] = wandrerer_df['osm_id'].astype('Int64')
    #     gdf_towns['osm_id'] = gdf_towns['osm_id'].astype('Int64')
    #     # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on='osm_id', how='left')
    #     # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on=['osm_id', 'Town', 'County', 'State', 'long_name'],
    #     #                       how='left')
    #     town_merged_df = gdf_towns.merge(wandrerer_df, on=['State', 'County', 'Town', 'long_name', 'osm_id'])
    #

    # min_val = 1
    # max_val = 200
    # gdf_towns[data_value] = np.random.randint(min_val, max_val + 1, size=len(gdf_towns))

    # gdf_counties = town_merged_df.dissolve(by=['State','County'], aggfunc={'Town': 'count', data_value: "sum"})
    # gdf_counties = town_merged_df.dissolve(by=['State','County'])

    gdf_counties = gdf_towns.dissolve(by=['State', 'County'])
    gdf_counties.reset_index(inplace=True)
    gdf_states = gdf_counties.dissolve(by='State')
    gdf_states.reset_index(inplace=True)

    gf.convert_bounds_to_linestrings(gdf_states)
    gdf_states.drop(['County', 'long_county','diagonal'], axis=1, inplace=True, errors='ignore')
    gf.convert_bounds_to_linestrings(gdf_states)
    states_geojson = json.loads(gdf_states.to_json())
    gdf_states.drop('geometry', axis=1, inplace=True, errors='ignore')
    wandrerer_states_df = wd.get_wandrer_totals_for_states(state_list)
    gdf_states_merged = gdf_states.merge(wandrerer_states_df, on=['State'])
    gdf_states_merged.rename(columns={"TownMilesCycled": "ActualMiles"}, inplace=True)
    # state_template = create_template(gdf_states_merged, ['State','TotalTowns', data_value])
    gdf_states_merged['Pct10Achieved'] = gdf_states_merged['Pct10_Count'] + gdf_states_merged['Pct25_Count'] + \
                                         gdf_states_merged['Pct50_Count'] + gdf_states_merged['Pct75_Count'] + \
                                         gdf_states_merged['Pct90_Count'] + gdf_states_merged['Pct99_Count']

    add_state_trace(fig, gdf_states_merged, states_geojson, data_value)
    # ss.gdfs['state_gdf'] = gdf_states

    gdf_counties.drop(['wandrer_id','wandrer_parent_id','Town','long_name','leisure','county','state','name','wikipedia','diagonal'], axis=1, inplace=True, errors='ignore')
    gf.convert_bounds_to_linestrings(gdf_counties)
    # counties_geojson = json.loads(gdf_counties.to_json())
    wandrerer_county_df = wd.get_wandrer_totals_for_counties_for_states(state_list)
    gdf_counties_merged = gdf_counties.merge(wandrerer_county_df, on=['State', 'County'])
    gdf_counties_merged.rename(columns={"Town": "TotalTowns"}, inplace=True)
    min_val = min(gdf_counties_merged[data_value])
    max_val = max(gdf_counties_merged[data_value])
    # gdf['value'] = np.random.randint(min_val, max_val + 1, size=len(gdf))
    zoom, center = calculate_mapbox_zoom_center(gdf_counties.bounds)
    # gdf_counties_merged.drop('geometry', axis=1, inplace=True, errors='ignore')
    # template = create_template(gdf_counties, ['County','TotalTowns', data_value])
    # county_template = create_template(gdf_counties_merged, ['State', 'County','Town', 'TotalMiles', 'ActualMiles', 'ActualPct'])

    gdf_counties_merged['Pct10Achieved'] = gdf_counties_merged['10%'] + gdf_counties_merged['25%'] + \
                                           gdf_counties_merged['50%'] + gdf_counties_merged['75%'] + \
                                           gdf_counties_merged['90%'] + gdf_counties_merged['99%']

    add_county_trace(fig, gdf_counties_merged, max_val, min_val, data_value)
    county_intersection_gdf = gpd.overlay(gdf_national_forests, gdf_counties, how='intersection')
    min_area = 0.00001  # Define your own tolerance threshold based on your CRS units
    county_intersection_gdf = county_intersection_gdf[county_intersection_gdf.geometry.area > min_area]
    county_intersection_gdf['intersection_area'] = county_intersection_gdf.geometry.area
    county_intersection_gdf = county_intersection_gdf.drop(
        columns=[col for col in county_intersection_gdf.columns if col.endswith('_1')])
    county_intersection_gdf.reset_index(inplace=True)
    ss.county_intersection_gdf = county_intersection_gdf

    # ss.gdfs['county_gdf'] = gdf_counties

    # state_list = gdf_towns['State'].unique().tolist()
    wandrerer_df = wd.get_wandrer_totals_for_towns_for_state(state_list)
    if wandrerer_df['osm_id'].isnull().all():
        # old format towns without osm_id values
        # town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State','County', 'Town','long_name'])
        # wandrerer_df['long_name'] = wandrerer_df['long_name'].str.replace('_', '-')
        # gdf_towns['long_name'] = gdf_towns['long_name'].str.replace('_', '-')
        # town_merged_df = gdf_towns.merge(wandrerer_df, on=['long_name', 'State','County', 'Town'])
        # prefer fields from left df because right has null osm_id. Both have diagonal.
        town_merged_df = pd.merge(gdf_towns, wandrerer_df, on=['long_name', 'State','County', 'Town'], how='left', suffixes=(None, '_r'))
        town_merged_df.drop('osm_id', axis=1, inplace=True, errors='ignore')
        suffix_to_drop = '_r'
        cols_to_drop = [col for col in town_merged_df.columns if col.endswith(suffix_to_drop)]
        town_merged_df.drop(columns=cols_to_drop, inplace=True)
    else:
        # new format towns with osm_id values
        wandrerer_df['osm_id'] = wandrerer_df['osm_id'].astype('Int64')
        gdf_towns['osm_id'] = gdf_towns['osm_id'].astype('Int64')
        # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on='osm_id', how='left')
        # town_merged_df = pd.merge(wandrerer_df, dissolved_town_gdf, on=['osm_id', 'Town', 'County', 'State', 'long_name'],
        #                       how='left')
        town_merged_df = gdf_towns.merge(wandrerer_df, on=['State', 'County', 'Town', 'long_name', 'osm_id'])

    # gdf_counties[data_value] = np.random.randint(min_val, max_val + 1, size=len(gdf_towns))

    # gdf_trails = gdf[gdf.geom_type.isin(['LineString'])]

    # gdf_states = gdf_counties.dissolve(by='State', aggfunc={'County': 'count', data_value: "sum"})
    # gdf_states.reset_index(inplace=True)

    # Load nation forests trace
    add_national_forests_trace(fig, gdf_national_forests.copy())

    # gdf_towns['value']=1
    # geojson = json.loads(gdf_towns.to_json())
    # zoom, center = calculate_mapbox_zoom_center(gdf_towns.bounds)
    # gdf_ton = json.loads(gdf_towns.to_json())
    geojson = json.loads(town_merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(town_merged_df.bounds)
    seacoast_df = town_merged_df[town_merged_df['seacoast'] == 1]

    if 'Wandrer_Id' in town_merged_df.columns:
        town_merged_df_copy = town_merged_df.copy()
        gdf_towns_subset = town_merged_df_copy[['County','Town','Wandrer_Id', 'Wandrer_Parent_Id', 'geometry','diagonal']]
        gdf_national_forests_copy = gdf_national_forests.copy()
        gdf_national_forests_subset = gdf_national_forests_copy[['name', 'State', 'long_name', 'REGION', 'FORESTNUMB', 'GIS_ACRES', 'value','geometry']]
        town_intersection_gdf = gpd.overlay(gdf_national_forests_subset, gdf_towns_subset, how='intersection')
        town_intersection_gdf['intersection_area'] = town_intersection_gdf.geometry.area
        town_intersection_gdf = town_intersection_gdf[town_intersection_gdf.geometry.area > min_area]
        town_intersection_gdf = town_intersection_gdf.drop(
            columns=[col for col in town_intersection_gdf.columns if col.endswith('_1')])
        town_intersection_gdf.drop('geometry', axis=1, inplace=True, errors='ignore')
        town_intersection_gdf.reset_index(inplace=True)
        ss.town_intersection_gdf = town_intersection_gdf

    town_merged_df.drop('geometry', axis=1, inplace=True, errors='ignore')
    # template = create_template(gdf_towns, ['State', 'County','Town'])
    # fig = go.Figure()
    # add_town_trace(fig, town_merged_df, geojson, data_value, counties_geojson)
    add_town_trace(fig, town_merged_df, geojson, data_value)


    # ss.gdfs['town_gdf'] = town_merged_df

    seacoast_geojson = json.loads(seacoast_df.to_json())
    seacoast_df.drop('geometry', axis=1, inplace=True, errors='ignore')
    add_seacoast_trace(fig, seacoast_df, seacoast_geojson, data_value)
    # ss.gdfs['seacoast_gdf'] = seacoast_df

    if 'leisure' in gdf.columns:
        # gdf_leisure = gdf.query('leisure.notna()')
        wandrerer_leisure_df = wd.get_wandrer_totals_for_towns_for_state(state_list)
        parks_merged_df = pd.merge(gdf_parks, wandrerer_df, on=['long_name', 'State', 'County', 'Town'], how='left', suffixes=(None, '_r'))
        parks_merged_df.rename(columns={"Town": "Location", "TotalMiles": "LocationMiles"}, inplace=True)

        gdf_parks['value']=10
        leisure_geojson = json.loads(parks_merged_df.to_json())
        parks_merged_df.drop('geometry', axis=1, inplace=True, errors='ignore')
        ss.map_data_park_gdf = parks_merged_df
        # template = create_template(town_no_geom_gdf, ['State', 'County','Town'])
        template = create_template(parks_merged_df,
                                   ['State', 'County', 'Location', 'LocationMiles', 'ActualMiles', 'ActualPct', 'Award Level'])

        fig.add_trace(go.Choroplethmap(
            customdata=parks_merged_df,
            geojson=leisure_geojson,
            locations=parks_merged_df['long_name'],
            featureidkey='properties.long_name',
            z=parks_merged_df[data_value],
            # colorscale=["green", "green"],
            colorscale=["#B8FFB8", "#00D100"],
            # colorscale="greens",
            colorbar=dict(x=-0.15, xanchor='left'),
            # coloraxis='coloraxis',
            marker_line_width=1,
            marker_line_color="black",  # Custom outline color for the GPX track
            marker_opacity=0.5,
            showscale=False,  # Optional: hide color scale if not needed
            hovertemplate=template,
            hoverlabel=dict(
                bgcolor="black",
                font_size=16),
            # name = 'Town Data Values',
            zmin = parks_merged_df[data_value].min(),
            zmax = parks_merged_df[data_value].max(),
            legendgroup="legend2",  # this can be any string, not just "group"
            legendgrouptitle_text="POI Layers",
            name='Parks',
            # visible='legendonly'
            showlegend=True
            )
        )

    if gdf.geom_type.isin(['LineString']).any():
        gdf_trails = gdf[gdf.geom_type.isin(['LineString'])]
        gdf_trails['value']=20
        dissolved_trails_gdf = gdf_trails.dissolve(by='County')
        dissolved_trails_gdf.geometry = dissolved_trails_gdf.geometry.line_merge()
        # trails_geojson = json.loads(gdf_trails.to_json())
        trails_geojson = json.loads(dissolved_trails_gdf.to_json())
        ss.map_data_trails_gdf = gdf_trails

        for feature in trails_geojson['features']:
            coords = feature['geometry']['coordinates']
            lons, lats = zip(*coords)

            fig.add_trace(go.Scattermap(
                mode="lines",
                lon=lons,
                lat=lats,
                line=dict(width=2, color='red'),
                hoverinfo='skip',
                legendgroup="legend2",  # this can be any string, not just "group"
                name='Trails',
                showlegend=True
            ))


    # # Load nation forests trace
    # add_national_forests_trace(fig, gdf_national_forests)

    # zoom, center = calculate_mapbox_zoom_center(gdf_towns.bounds)
    # fig.update_layout(map_style="carto-positron", map_zoom=zoom, map_center=center, clickmode='event+select')
    fig.update_layout(map_style="carto-positron", map_zoom=zoom, map_center=center)

    fig.update_layout(margin={"r": 10, "t": 30, "l": 1, "b": 1})
    # Update layout to ensure legend interaction is enabled (default behavior)
    # fig.update_layout(
    #     title="Legend Toggling Example",
    #     legend=dict(
    #         itemclick="toggle",  # Single click toggles one trace
    #         itemdoubleclick="toggleothers"  # Double click isolates one trace
    #     )
    # )

    update_layout_legends(fig)

    # st.plotly_chart(fig)
    st.session_state.choropleth = fig
    st.session_state.gdf_choropleth = gdf_towns

    return fig


def add_national_forests_trace(fig, gdf):
    nf_geojson = json.loads(gdf.to_json())
    gdf.drop('geometry', axis=1, inplace=True, errors='ignore')
    nf_template = create_template(gdf, ['State', 'name'])
    fig.add_trace(go.Choroplethmap(
        customdata=gdf,
        geojson=nf_geojson,
        locations=gdf['name'],
        featureidkey='properties.name',
        z=gdf['value'],
        # colorscale=["green", "green"],
        # colorscale=["#B8FFB8", "#00D100"],
        colorscale="purples",
        colorbar=dict(x=-0.15, xanchor='left'),
        # coloraxis='coloraxis',
        marker_line_width=1,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=0.5,
        showscale=False,  # Optional: hide color scale if not needed
        hovertemplate=nf_template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf['value'].min(),
        zmax=gdf['value'].max(),
        legendgroup="legend2",  # this can be any string, not just "group"
        legendgrouptitle_text="POI Layers",
        name='National Forests',
        # visible='legendonly'
        showlegend=True
    ))


def update_layout_legends(fig):
    fig.update_layout(
        # coloraxis={'colorscale': max_50_pct_color_scale, 'title': data_value},
        legend=dict(
            title=dict(text="Admin Layers"),
            x=-0.2,
            # y=0.75,
            # xref="container",
            # yref="container",
            xanchor="left",
            yanchor="top",
            groupclick="toggleitem",
            # groupclick="togglegroup",
            # itemclick="toggle",
            # itemdoubleclick="toggleothers"
            # titleclick="toggleothers",
            # titledoubleclick="toggle",
        ),
        legend2=dict(
            # title=dict(text="POI Layers"),
            x=-0.2,
            # y=0.75,
            # xref="container",
            # yref="container",
            xanchor="left",
            yanchor="top",
            groupclick="toggleitem",
            # groupclick="togglegroup",
            # itemclick="toggle",
            # itemdoubleclick="toggleothers"
        )
    )

    # fig.update_layout(
    #     # coloraxis={'colorscale': max_50_pct_color_scale, 'title': data_value},
    #     legend=dict(
    #         title=dict(text="Admin Layers"),
    #         x=-0.2,
    #         # y=0.75,
    #         # xref="container",
    #         # yref="container",
    #         xanchor="left",
    #         yanchor="top",
    #         groupclick="toggleitem",
    #         # groupclick="togglegroup"
    #         # itemclick="toggle",
    #         itemdoubleclick="toggleothers"
    #         # titleclick="toggleothers",
    #         # titledoubleclick="toggle",
    #     # ),
    #     # legend2=dict(
    #     #     # title=dict(text="POI Layers"),
    #     #     x=-0.2,
    #     #     # y=0.75,
    #     #     # xref="container",
    #     #     # yref="container",
    #     #     xanchor="left",
    #     #     yanchor="top",
    #     #     # groupclick="toggleitem",
    #     #     # groupclick="togglegroup",
    #     #     itemclick="toggle",
    #     #     # itemdoubleclick="toggleothers"
    #     )
    # )


def add_town_trace(fig, gdf_towns, geojson, data_value):
    # template = create_template(gdf_towns, ['State', 'County','Town', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Award Level'])
    marker_opacity = 1.0
    ss.map_data_town_gdf = gdf_towns
    gdf_towns.sort_values(by=['State','Town'], inplace=True)
    template = create_template(gdf_towns, ['State', 'County','Town', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Award Level'])
    # ss.sorted_town_gdf =

    selected_marker_opacity = 0.5

    fig.add_trace(go.Choroplethmap(
        customdata=gdf_towns,
        geojson=geojson,
        locations=gdf_towns['long_name'],
        featureidkey='properties.long_name',
        z=gdf_towns[data_value] * 100 if data_value == 'ActualPct' else gdf_towns[data_value],
        # colorscale=["white", "white"],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        # colorbar=dict(x=-0.15, xanchor='left'),
        colorbar=dict(x=1.0),
        # colorbar=dict(x=1.15),
        colorbar_title=f'Town<br>{data_value}',
        # coloraxis='coloraxis',
        showscale=True,  # Optional: hide color scale if not needed
        marker_line_width=1,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=selected_marker_opacity,
        # marker_opacity=marker_opacity,
        # 2. Define unselected style: Fade all unselected regions
        unselected=dict(marker=dict(opacity=0.2)),
        # Optional: Customize selected appearance
        selected=dict(marker=dict(opacity=selected_marker_opacity)),
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf_towns[data_value].min(),
        # zmax=gdf_towns[data_value].max(),
        zmax=math.ceil(gdf_towns[data_value].max() / 100) * 100,
        legendgroup="legend",  # this can be any string, not just "group"
        name='Town Map',
        showlegend=True,
        visible='legendonly'
    ))

    # count_line_width = 2
    # fig.update_layout(map_layers=[dict(sourcetype='geojson',
    #                                       source=counties_geojson,
    #                                       color='#303030',
    #                                       type='line',
    #                                       line=dict(width=count_line_width)
    #                                       # hovertemplate=template
    #                                       )]);


def add_seacoast_trace(fig, gdf_towns, geojson, data_value):
    template = create_template(gdf_towns, ['State', 'County','Town', data_value])
    marker_opacity = 1.0
    ss.map_data_seacoast_gdf = gdf_towns
    template = create_template(gdf_towns, ['State', 'County','Town', 'TotalMiles', 'ActualMiles', 'ActualPct', 'Award Level'])

    fig.add_trace(go.Choroplethmap(
        customdata=gdf_towns,
        geojson=geojson,
        locations=gdf_towns['long_name'],
        featureidkey='properties.long_name',
        z=gdf_towns[data_value] * 100 if data_value == 'ActualPct' else gdf_towns[data_value],
        # colorscale=["white", "white"],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        # colorbar=dict(x=-0.15, xanchor='left'),
        colorbar=dict(x=1.0),
        # colorbar=dict(x=1.15),
        colorbar_title=f'Town<br>{data_value}',
        # coloraxis='coloraxis',
        showscale=True,  # Optional: hide color scale if not needed
        marker_line_width=1,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=marker_opacity,
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf_towns[data_value].min(),
        # zmax=gdf_towns[data_value].max(),
        # zmax=math.ceil(gdf_towns[data_value].max() / 100) * 100,
        zmax=gdf_towns[data_value].max() * 100,
        legendgroup="legend",  # this can be any string, not just "group"
        name='Seacoast Map',
        showlegend=True,
        visible='legendonly'
    ))


def add_state_trace(fig, gdf, geojson, data_value):
    template = create_template(gdf, ['State', 'TotalTowns', 'TownsCycled','PctTownsCycled', 'TownsAwarded','PctTownsAwarded',
                                     'Pct10Achieved', 'StateMiles', 'ActualMiles', 'PctMilesCycled'])
    marker_opacity = 0.5
    colorbar_x = 1.2
    d_v = 'PctMilesCycled' if data_value == 'ActualPct' else data_value
    z_max = math.ceil(gdf[d_v].max() / 100) * 100
    ss.map_data_state_gdf = gdf

    fig.add_trace(go.Choroplethmap(
        customdata=gdf,
        geojson=geojson,
        locations=gdf['State'],
        featureidkey='properties.State',
        z=gdf[d_v] * 100 if data_value == 'ActualPct' else gdf[d_v],
        # colorscale=["white", "white"],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        # colorbar=dict(x=-0.15, xanchor='left'),
        # colorbar=dict(x=1.15),
        colorbar=dict(x=colorbar_x),
        colorbar_title=f'State<br>{d_v}',
        # coloraxis='coloraxis',
        showscale=True,  # Optional: hide color scale if not needed
        marker_line_width=1,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=marker_opacity,
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        # zmin=gdf[data_value].min(),
        # zmax=gdf_towns[data_value].max(),
        zmax=z_max,
        zmin=1,
        showlegend=True,
        legendgroup='legend',  # this can be any string, not just "group"
        # legendgrouptitle_text='Admin Layers',
        # legend_groupclick='toggleothers',
        name='State Map'
        # visible='legendonly'
    ))

    # count_line_width = 2
    # fig.update_layout(map_layers=[dict(sourcetype='geojson',
    #                                       source=counties_geojson,
    #                                       color='#303030',
    #                                       type='line',
    #                                       line=dict(width=count_line_width)
    #                                       # hovertemplate=template
    #                                       )]);


def add_county_trace(fig, gdf, max_val, min_val, data_value):
    line_width = 1
    marker_opacity = 1.0
    # d_v = 'PctMilesCycled' if data_value == 'ActualPct' else data_value
    # z_max = math.ceil(gdf[data_value].max() / 100) * 100
    z_max = math.ceil(gdf[data_value].max() * 2) / 2
    ss.map_data_county_gdf = gdf
    counties_geojson = json.loads(gdf.to_json())
    gdf.drop('geometry', axis=1, inplace=True, errors='ignore')
    template = create_template(gdf, ['State', 'County', 'TotalTowns', 'CycledTowns', 'PctTownsCycled', 'AchievedTowns',
                                     'PctTownsAchieved', 'Pct10Achieved', 'TotalCountyMiles', 'ActualMiles', 'ActualPct'])
    colorbar_x = 1.2
    fig.add_trace(go.Choroplethmap(
        customdata=gdf,
        geojson=counties_geojson,
        locations=gdf['County'],
        featureidkey='properties.County',
        z=gdf[data_value],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        showscale=True,  # Optional: hide color scale if not needed
        marker_line_width=line_width,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=marker_opacity,
        # colorbar=dict(x=-0.15, xanchor='left'),
        colorbar_title=f'County<br>{data_value}',
        colorbar=dict(x=colorbar_x),
        # coloraxis='coloraxis',
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf[data_value].min(),
        # zmax=gdf_counties[data_value].max(),
        zmax=z_max,
        legendgroup="legend",  # this can be any string, not just "group"
        showlegend=True,
        name='County Map',
        visible='legendonly'
    )
    )




