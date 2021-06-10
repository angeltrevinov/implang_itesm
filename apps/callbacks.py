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
df_inegi_av_demo = pd.read_csv("src_files/inegi_av_98.csv") #union of green areas and inegi
df_av_denue_rank = pd.read_csv("src_files/denue_ranking.csv") #union of green areas and denue with ranking

## helper file
park_name_features = json.load(open("src_files/park_names_features.json"))

##prepare inegi data
#calculate female and male data for 25 to 59 years
for col in ['P_0A2_F', 'P_3A5_F','P_6A11_F', 'P_12A14_F', 'P_15A17_F', 'P_18A24_F',  'P_60YMAS_F','POBFEM']:
    df_inegi_av_demo[col] = df_inegi_av_demo[col].fillna(0).replace("*", 0).astype(int)

for col in ['P_0A2_M', 'P_3A5_M','P_6A11_M', 'P_12A14_M', 'P_15A17_M', 'P_18A24_M',  'P_60YMAS_M','POBMAS']:
    df_inegi_av_demo[col] = df_inegi_av_demo[col].fillna(0).replace("*", 0).astype(int)

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
            color_continuous_scale=['#590E0E', '#8C1616', '#CC730E', '#D6900F', '#FFC71F', '#FFE359', '#E4F279',  "#BDB655", "#9CA653", "#6C7339"],
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
                colorscale=["#63B350", "#63B350",],
                marker_line_width=3,
                marker_line_color="white",
                showscale=False,
                name= "<br>".join(selected_park.split(" ")),
                text=selected_park,
                hoverinfo="name+text",
                hovertext= "puntuación: " + df_av_denue_rank_filter['ranking'].astype(str) + "<br>" + "Área m²: " + df_av_denue_rank_filter['SHAPE_AREA'].astype(str)  + "<br>" + "densidad poblacional: " + df_av_denue_rank_filter['densidad poblacional'].astype(str) + "<br>" + "Tipología: " + df_av_denue_rank_filter['TIPOLOGIA']
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
                    colorscale=['#590E0E', '#8C1616', '#CC730E', '#D6900F', '#FFC71F', '#FFE359', '#E4F279',  "#BDB655", "#9CA653", "#6C7339"],
                    marker_line_color='white',
                    name=radio_ranking_filter,
                    hoverinfo="text",
                    hovertext="nombre:" + df_av_denue_rank["NOMBRE_PARQUE"] + "<br>" + radio_ranking_filter + ": " + df_av_denue_rank[radio_ranking_filter].astype(str),
                ),
            )
        
        fig.update_geos(fitbounds="locations", visible=False)

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        return fig

    @app.callback(
        Output('demographic_bar', 'figure'),
        Input('select_service_by_park_demo', 'value')
        
    )
    def generate_map_services(selected_park):
        d_filter_name = df_inegi_av_demo[df_inegi_av['NOMBRE_PARQUE'] == selected_park]
        d_filter_name = d_filter_name.groupby('NOMBRE_PARQUE').sum()

        inegi_fem = d_filter_name[['P_0A2_F', 'P_3A5_F','P_6A11_F', 'P_12A14_F', 'P_15A17_F', 'P_18A24_F',  'P_60YMAS_F','POBFEM']]
        inegi_fem['P_25A59_F'] = inegi_fem['POBFEM'] - (inegi_fem["P_0A2_F"] + inegi_fem["P_3A5_F"] + inegi_fem["P_6A11_F"] + inegi_fem["P_12A14_F"] + inegi_fem["P_15A17_F"] + inegi_fem["P_18A24_F"] + inegi_fem["P_60YMAS_F"])

        inegi_Mas = d_filter_name[['P_0A2_M', 'P_3A5_M','P_6A11_M', 'P_12A14_M', 'P_15A17_M', 'P_18A24_M',  'P_60YMAS_M','POBMAS']]
        inegi_Mas['P_25A59_M'] = inegi_Mas['POBMAS'] - (inegi_Mas["P_0A2_M"] + inegi_Mas["P_3A5_M"] + inegi_Mas["P_6A11_M"] + inegi_Mas["P_12A14_M"] + inegi_Mas["P_15A17_M"] + inegi_Mas["P_18A24_M"] + inegi_Mas["P_60YMAS_M"])

        #prepare data
        women_bins = np.array(list(inegi_fem[['P_0A2_F', 'P_3A5_F','P_6A11_F', 'P_12A14_F', 'P_15A17_F', 'P_18A24_F', 'P_25A59_F', 'P_60YMAS_F']].sum() * -1))
        men_bins = np.array(list(inegi_Mas[['P_0A2_M', 'P_3A5_M','P_6A11_M', 'P_12A14_M', 'P_15A17_M', 'P_18A24_M', 'P_25A59_M', 'P_60YMAS_M']].sum()))
        y = ['0 a 2 años', '3 a 5 años', '6 a 11 años', '12 a 14 años', '15 a 17 años', '18 a 24 años', '25 a 59 años', '60+ años']

        layout = go.Layout(yaxis=go.layout.YAxis(title='Rangos de edades'),
                    xaxis=go.layout.XAxis(
                        title='Personas que viven a menos de 5 minutos de un área verde'),
                    barmode='overlay',
                    bargap=0.2,
                    annotations=[
                                    dict(xref='x', yref='y',
                                    x=women_bins[0] + men_bins[0], y='0 a 2 años',
                                    hovertext=str(women_bins[0] + men_bins[0]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[1] + men_bins[1], y='3 a 5 años',
                                    hovertext=str(women_bins[1] + men_bins[1]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[2] + men_bins[2], y='6 a 11 años',
                                    hovertext=str(women_bins[2] + men_bins[2]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[3] + men_bins[3], y='12 a 14 años',
                                    hovertext=str(women_bins[3] + men_bins[3]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[4] + men_bins[4], y='15 a 17 años',
                                    hovertext=str(women_bins[4] + men_bins[4]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[5] + men_bins[5], y='18 a 24 años',
                                    hovertext=str(women_bins[5] + men_bins[5]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[6] + men_bins[6], y='25 a 59 años',
                                    hovertext=str(women_bins[6] + men_bins[6]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False),
                                    dict(xref='x', yref='y',
                                    x=women_bins[7] + men_bins[7], y='60+ años',
                                    hovertext=str(women_bins[7] + men_bins[7]),
                                    text="|",
                                    font=dict(family='Arial', size=12,
                                            color='white'),
                                    showarrow=False)
                                    ]
                    )

        data = [go.Bar(y=y,
                x=men_bins,
                orientation='h',
                name='Hombres',
                hoverinfo='x+name',
                marker=dict(color='#1F67A6')
                ),
            go.Bar(y=y,
                x=women_bins,
                orientation='h',
                name='Mujeres',
                text=-1 * women_bins.astype('int'),
                hoverinfo='text+name',
                marker=dict(color='#8C1616')
                )]
                
        fig = go.Figure(data=data, layout=layout)
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0))

        return fig

    @app.callback(
        Output('sunburst_services', 'figure'),
        [Input('sunburst_services_top', 'value'),Input('sunburst_services_type', 'value')]
    )
    def generate_map_services(top, isTop):
        top = int(top)
        df1 = df_av_denue_rank
        if isTop:
            df2 = df1[df1["NOMBRE_PARQUE"].isin(df1.sort_values('cantidad de servicios', ascending=False)['NOMBRE_PARQUE'].unique()[:top])]
        else:
            size_parks = len(df1.sort_values('cantidad de servicios', ascending=False)['NOMBRE_PARQUE'].unique())
            df2 = df1[df1["NOMBRE_PARQUE"].isin(df1.sort_values('cantidad de servicios', ascending=False)['NOMBRE_PARQUE'].unique()[(size_parks - top):])]
        
        fig = px.sunburst(
            df2, 
            path=['TIPOLOGIA','NOMBRE_PARQUE', 'nombre_act'], 
            color=df2['NOMBRE_PARQUE'],
            hover_name=df2['NOMBRE_PARQUE'],
            hover_data={'NOMBRE_PARQUE':False},
            custom_data=['cantidad de servicios'],
            color_discrete_sequence=['#590E0E', '#8C1616', '#CC730E', '#D6900F', '#FFC71F', '#FFE359', '#E4F279',  "#BDB655", "#9CA653", "#6C7339"],
            maxdepth=2
            )

        fig.update_layout(margin = dict(t=0, l=0, r=0, b=0), height=600)
        fig.update_traces(insidetextorientation="auto", hovertemplate='%{label} <br> %{parent} <br> Servicios totales: %{value}')

        return fig
