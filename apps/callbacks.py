import os
from dotenv import load_dotenv
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from shapely.geometry import shape

load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")
mapbox_style = "mapbox://styles/mildredgil/cknmcvkgm0tig17nttrh3qymr"
center_k1 = { 'lon': -100.4068401068442, 'lat': 25.673275441075}

# Load files
## geojsons
sector_k1_polygon = json.load(open("src_files/sector_k1.geojson"))
sector_k1_av = json.load(open("src_files/av_k1.geojson"))
sector_k1_inegi = json.load(open("src_files/inegi_k1.geojson"))

## csv 
df_inegi_av = pd.read_csv("src_files/inegi_av_98.csv") #union of green areas and inegi
df_av_denue_rank = pd.read_csv("src_files/denue_ranking.csv") #union of green areas and denue with ranking

## helper file
park_name_features = json.load(open("src_files/park_names_features.json"))

##prepare inegi data
df_inegi_av.rename(columns={"POBTOT": "población", "POBFEM": "mujeres", "POBMAS": "hombres", "VIVTOT": "viviendas"}, inplace=True)
df_inegi_av.fillna(0, inplace=True)
df_inegi_av.replace("*", 0, inplace=True)

df_inegi_av["mujeres"] = df_inegi_av["mujeres"].astype(int)
df_inegi_av["hombres"] = df_inegi_av["hombres"].astype(int)
df_inegi_av["densidad poblacional"] = df_inegi_av["población"] / df_inegi_av["area"]

def assign_callbacks(app):
    @app.callback(
        Output('map_services_by_park', 'figure'),
        [Input('select_service_by_park', 'value'), Input('radio_filter', 'value'), Input('switches_servicios', 'value')]
        
    )
    def generate_map_services(selected_park, radio_filter, switches_servicios):
        ''''
        Generates map of green areas with inegi and denue data by GA
        '''
        #filter denue data
        df_av_denue_rank_filter = df_av_denue_rank[df_av_denue_rank["NOMBRE_PARQUE"] == selected_park]

        #filter inegi data
        df_inegi_av_filter = df_inegi_av[df_inegi_av['NOMBRE_PARQUE'] == selected_park]

        #load inegi near 400mts 
        fig = px.choropleth_mapbox(
            df_inegi_av_filter, 
            geojson=sector_k1_inegi, color=radio_filter,
            locations="inegi_cvegeo", 
            featureidkey="properties.CVEGEO", 
            color_continuous_scale=["#CCC30E", "#D6B80F", "#BF9517", "#D6900F", "#CC730E"],
            hover_data=["población","mujeres","hombres","area", "distancia", "viviendas", "densidad poblacional"],
        )
        
        #load services near 400mts
        fig.add_trace(go.Scattermapbox(
            mode = "markers+text",
            lon = df_av_denue_rank_filter['longitud'], 
            lat = df_av_denue_rank_filter['latitud'],
            marker=go.scattermapbox.Marker(
                    size=15,
                    symbol=["shop"] * len(df_av_denue_rank_filter),
                ),
            hoverlabel={"bgcolor": "#C1D0D6"},
            hoverinfo="text",
            hovertext = "servicio: " + df_av_denue_rank_filter['nombre_act'] + "<br>" + "distancia al parque: " + df_av_denue_rank_filter['distancia'].astype(str),
            textposition = "bottom right",
            textfont={"size": 16, "color": "#003952", },
            name="servicios",
            visible="services" in switches_servicios
            )
        )

        #load selected green areas
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=sector_k1_av,
                locations=df_av_denue_rank_filter['av_union'],
                featureidkey="properties.UNION",
                z=df_av_denue_rank_filter["ranking"],
                colorscale=["#6C7339", "#6C7339",],
                showscale=False,
                marker_line_width=0,
                name= "<br>".join(selected_park.split(" ")),
                hoverinfo="text",
                hovertext= "ranking: " + df_av_denue_rank_filter['ranking'].astype(str) + "<br>" + "Área m²: " + df_av_denue_rank_filter['SHAPE_AREA'].astype(str)  + "<br>" + "densidad poblacional: " + df_av_denue_rank_filter['densidad poblacional'].astype(str) + "<br>" + "Tipología: " + df_av_denue_rank_filter['TIPOLOGIA']
            )
        )

        #get center of the green area
        s = shape(park_name_features[selected_park][0]['geometry'])
        centroid = s.centroid
        center = { 'lon': centroid.x, 'lat': centroid.y}
        
        fig.update_layout(
            mapbox = {
                'accesstoken': mapbox_token,
                'style': mapbox_style, 
                'center': center, 
                'zoom': 15, 'layers': [
                    {
                    'source': {
                        'type': "FeatureCollection",
                        'features': sector_k1_inegi["features"] #show all the inegi data
                    },
                    'type': "fill", 'color': "#B8CBCC",'below': "traces",},
                    {
                    'source': {
                        'type': "FeatureCollection",
                        'features': sector_k1_av['features'] #show all the green areas
                    },
                    'type': "fill", 'color': "#85A3CA", 'below': "traces"},
                    ]
                    },
                margin = {'l':0, 'r':0, 'b':0, 't':0},
                height=600
            )

        return fig

    @app.callback(
        Output('map_ranking_park', 'figure'),
        Input('radio_ranking_filter', 'value')
        
    )
    def generate_map_services(radio_ranking_filter):
        ''''
        Generates map of all green areas
        '''
        fig = go.Figure()

        fig.add_trace(
            go.Choropleth(
                uid="inegi",
                geojson=sector_k1_inegi,
                locations=df_inegi_av["inegi_cvegeo"],
                featureidkey="properties.CVEGEO",
                z=df_inegi_av["distancia"],
                colorscale=["#85A3CA","#B8BBBF"],
                marker_line_color='white',
                marker_opacity=0.2,
                hoverinfo="none",
                showscale=False
            ),
        )
#hover_data=["POBTOT", "TIPOLOGIA", "cantidad de servicios", "VIVTOT", "densidad poblacional", "ranking"], 
        if radio_ranking_filter == "TIPOLOGIA":
            fig.add_trace(
                go.Choropleth(
                    uid="parks",
                    geojson=sector_k1_av,
                    locations=df_av_denue_rank["av_union"],
                    featureidkey="properties.UNION",
                    z=df_av_denue_rank[radio_ranking_filter].factorize()[0],
                    colorscale=[[0,"#B0B591"], [0.25,"#B0B591"], [0.25,"#B3A250"], [0.5,"#B3A250"], [0.5,"#D6B80F"], [0.75,"#D6B80F"],[0.75,"#D6900F"],[1,"#D6900F"]],
                    colorbar_ticktext=df_av_denue_rank[radio_ranking_filter].unique(),
                    colorbar_tickvals=[0.375,1.125,1.785,2.625],
                    colorbar_ticklen=1,
                    colorbar_tickmode="array",
                    marker_line_color='white',
                    name=radio_ranking_filter,
                    hoverinfo="text",
                    hovertext="nombre:" + df_av_denue_rank["NOMBRE_PARQUE"] + "<br>" + radio_ranking_filter + ": " + df_av_denue_rank[radio_ranking_filter].astype(str),
                ),
            )
            
        else:
            fig.add_trace(
                go.Choropleth(
                    uid="parks",
                    geojson=sector_k1_av,
                    locations=df_av_denue_rank["av_union"],
                    featureidkey="properties.UNION",
                    z=df_av_denue_rank[radio_ranking_filter],
                    colorscale=["#E4F279", "#CCC30E", "#D6B80F", "#BF9517", "#D6900F", "#CC730E"],
                    marker_line_color='white',
                    name=radio_ranking_filter,
                    hoverinfo="text",
                    hovertext="nombre:" + df_av_denue_rank["NOMBRE_PARQUE"] + "<br>" + radio_ranking_filter + ": " + df_av_denue_rank[radio_ranking_filter].astype(str),
                ),
            )
        
        fig.update_geos(fitbounds="locations", visible=False)

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return fig
