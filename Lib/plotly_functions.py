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
import wandrer_database as wd

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

            elif name == 'TownsAwarded':
                template += "<b>Towns Awarded:</b> %{" + f"customdata[{data.columns.get_loc('TownsAwarded')}]" + "}<br>"

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


def create_choropleth_map_with_legend(state_list):
    # st.write("filename:", geojson_file)
    # ss.gdfs = {}

    data_value = ss.selected_datavalue_for_map

    gdf = gf.get_geopandas_df_for_region(state_list)
    gdf.set_crs("EPSG:4326", inplace=True)

    if 'leisure' in gdf.columns:
        # gdf_leisure = gdf.query('leisure.notna()')
        gdf_towns = gdf[(gdf['leisure'].isna()) & (gdf.geom_type.isin(['Polygon', 'MultiPolygon']))]
    else:
        gdf_towns = gdf[(gdf.geom_type.isin(['Polygon', 'MultiPolygon']))]

    # state_list = gdf_towns['State'].unique().tolist()
    wandrerer_df = wd.get_wandrer_totals_for_towns_for_state(state_list)
    if wandrerer_df['osm_id'].isnull().all():
        # old format towns without osm_id values
        # town_merged_df = dissolved_town_gdf.merge(wandrerer_df, on=['State','County', 'Town','long_name'])
        wandrerer_df['long_name'] = wandrerer_df['long_name'].str.replace('_', '-')
        gdf_towns['long_name'] = gdf_towns['long_name'].str.replace('_', '-')
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

    # min_val = 1
    # max_val = 200
    # gdf_towns[data_value] = np.random.randint(min_val, max_val + 1, size=len(gdf_towns))

    gdf_counties = town_merged_df.dissolve(by=['State','County'], aggfunc={'Town': 'count', data_value: "sum"})
    gdf_counties.reset_index(inplace=True)
    gdf_counties.rename(columns={"Town": "TotalTowns"}, inplace=True)
    gf.convert_bounds_to_linestrings(gdf_counties)
    # gdf_counties[data_value] = np.random.randint(min_val, max_val + 1, size=len(gdf_towns))

    # gdf_trails = gdf[gdf.geom_type.isin(['LineString'])]

    gdf_states = gdf_counties.dissolve(by='State', aggfunc={'County': 'count', data_value: "sum"})
    gdf_states.reset_index(inplace=True)
    gf.convert_bounds_to_linestrings(gdf_states)

    states_geojson = json.loads(gdf_states.to_json())
    gdf_states.drop('geometry', axis=1, inplace=True, errors='ignore')
    template = create_template(gdf_states, ['State','TotalTowns', data_value])

    fig = go.Figure()
    add_state_trace(fig, gdf_states, states_geojson, data_value)
    # ss.gdfs['state_gdf'] = gdf_states

    min_val = min(gdf_counties[data_value])
    max_val = max(gdf_counties[data_value])
    # gdf['value'] = np.random.randint(min_val, max_val + 1, size=len(gdf))
    counties_geojson = json.loads(gdf_counties.to_json())
    zoom, center = calculate_mapbox_zoom_center(gdf_counties.bounds)
    gdf_counties.drop('geometry', axis=1, inplace=True, errors='ignore')
    template = create_template(gdf_counties, ['County','TotalTowns', data_value])

    add_county_trace(counties_geojson, fig, gdf_counties, max_val, min_val, template, data_value)
    # ss.gdfs['county_gdf'] = gdf_counties

    # gdf_towns['value']=1
    # geojson = json.loads(gdf_towns.to_json())
    # zoom, center = calculate_mapbox_zoom_center(gdf_towns.bounds)
    # gdf_ton = json.loads(gdf_towns.to_json())
    geojson = json.loads(town_merged_df.to_json())
    zoom, center = calculate_mapbox_zoom_center(town_merged_df.bounds)
    seacoast_df = town_merged_df[town_merged_df['seacoast'] == 1]
    town_merged_df.drop('geometry', axis=1, inplace=True, errors='ignore')
    # template = create_template(gdf_towns, ['State', 'County','Town'])
    # fig = go.Figure()
    add_town_trace(fig, town_merged_df, geojson, data_value, counties_geojson)
    # ss.gdfs['town_gdf'] = town_merged_df

    seacoast_geojson = json.loads(seacoast_df.to_json())
    seacoast_df.drop('geometry', axis=1, inplace=True, errors='ignore')
    add_seacoast_trace(fig, seacoast_df, seacoast_geojson, data_value, counties_geojson)
    # ss.gdfs['seacoast_gdf'] = seacoast_df

    if 'leisure' in gdf.columns:
        gdf_leisure = gdf.query('leisure.notna()')
        gdf_leisure['value']=10
        leisure_geojson = json.loads(gdf_leisure.to_json())
        gdf_leisure.drop('geometry', axis=1, inplace=True, errors='ignore')
        ss.map_data_park_gdf = gdf
        # template = create_template(town_no_geom_gdf, ['State', 'County','Town'])
        template = create_template(gdf_leisure, ['State', 'County','Town'])
        fig.add_trace(go.Choroplethmap(
            customdata=gdf_leisure,
            geojson=leisure_geojson,
            locations=gdf_leisure['long_name'],
            featureidkey='properties.long_name',
            z=gdf_leisure['value'],
            colorscale=["green", "green"],
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
            zmin = gdf_leisure['value'].min(),
            zmax = gdf_leisure['value'].max(),
            legendgroup="legend2",  # this can be any string, not just "group"
            legendgrouptitle_text="POI Layers",
            name='Leisure Map',
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


def add_town_trace(fig, gdf_towns, geojson, data_value, counties_geojson):
    template = create_template(gdf_towns, ['State', 'County','Town', data_value])
    marker_opacity = 1.0
    ss.map_data_town_gdf = gdf_towns
    gdf_towns.sort_values(by=['State','Town'], inplace=True)
    # ss.sorted_town_gdf =
    fig.add_trace(go.Choroplethmap(
        customdata=gdf_towns,
        geojson=geojson,
        locations=gdf_towns['long_name'],
        featureidkey='properties.long_name',
        z=gdf_towns[data_value],
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
        # marker_opacity=marker_opacity,
        # 2. Define unselected style: Fade all unselected regions
        unselected=dict(marker=dict(opacity=0.2)),
        # Optional: Customize selected appearance
        selected=dict(marker=dict(opacity=1.0)),
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf_towns[data_value].min(),
        # zmax=gdf_towns[data_value].max(),
        zmax=math.ceil(gdf_towns[data_value].max() / 100) * 100,
        # legendgroup="legend",  # this can be any string, not just "group"
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


def add_seacoast_trace(fig, gdf_towns, geojson, data_value, counties_geojson):
    template = create_template(gdf_towns, ['State', 'County','Town', data_value])
    marker_opacity = 1.0
    ss.map_data_seacoast_gdf = gdf_towns

    fig.add_trace(go.Choroplethmap(
        customdata=gdf_towns,
        geojson=geojson,
        locations=gdf_towns['long_name'],
        featureidkey='properties.long_name',
        z=gdf_towns[data_value] * 100,
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
        # legendgroup="legend",  # this can be any string, not just "group"
        name='Seacoast Map',
        showlegend=True,
        visible='legendonly'
    ))


def add_state_trace(fig, gdf, geojson, data_value):
    template = create_template(gdf, ['State', 'County', data_value])
    marker_opacity = 0.5
    ss.map_data_state_gdf = gdf

    fig.add_trace(go.Choroplethmap(
        customdata=gdf,
        geojson=geojson,
        locations=gdf['State'],
        featureidkey='properties.State',
        z=gdf[data_value],
        # colorscale=["white", "white"],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        # colorbar=dict(x=-0.15, xanchor='left'),
        # colorbar=dict(x=1.15),
        colorbar=dict(x=1.0),
        colorbar_title=f'State<br>{data_value}',
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
        zmax=math.ceil(gdf[data_value].max() / 200) * 200,
        zmin=1,
        showlegend=True,
        # legendgroup='legend',  # this can be any string, not just "group"
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


def add_county_trace(counties_geojson, fig, gdf_counties, max_val, min_val, template, data_value):
    line_width = 1
    marker_opacity = 1.0
    ss.map_data_county_gdf = gdf_counties

    fig.add_trace(go.Choroplethmap(
        customdata=gdf_counties,
        geojson=counties_geojson,
        locations=gdf_counties['County'],
        featureidkey='properties.County',
        z=gdf_counties[data_value],
        colorscale=max_50_pct_color_scale,
        # colorbar_title=data_value,
        showscale=True,  # Optional: hide color scale if not needed
        marker_line_width=line_width,
        marker_line_color="black",  # Custom outline color for the GPX track
        marker_opacity=marker_opacity,
        # colorbar=dict(x=-0.15, xanchor='left'),
        colorbar_title=f'County<br>{data_value}',
        colorbar=dict(x=1.0),
        # coloraxis='coloraxis',
        hovertemplate=template,
        hoverlabel=dict(
            bgcolor="black",
            font_size=16),
        # name = 'Town Data Values',
        zmin=gdf_counties[data_value].min(),
        # zmax=gdf_counties[data_value].max(),
        zmax=math.ceil(gdf_counties[data_value].max() / 200) * 200,
        # legendgroup="legend",  # this can be any string, not just "group"
        showlegend=True,
        name='County Map',
        visible='legendonly'
    )
    )




