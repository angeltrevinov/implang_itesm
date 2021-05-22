import os
from dotenv import load_dotenv
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from app import app

##### MIEMBROS
# - Julia Jimenez   A00821428
# - Angel Treviño   A01336559
# - Mildred Gil     A00820397
# - Mauricio Lozano A01194301

# loading env
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

###################### LOGIC ###############################
########### LOAD DATA
##### JSONS
sector_k1_polygon = json.load(open("src_files/sector_k1.geojson"))
sector_k1_av = json.load(open("src_files/av_k1.geojson"))
##### CSVS
df_denue_av = pd.read_csv("src_files/completo_denue_av.csv")
#df_inegi_av = pd.read_csv("src_files/")
df_av = pd.read_csv("src_files/av_k1.csv")
df_denue = pd.read_csv("src_files/denue_corregido.csv")
##### SET UP TABLES
df_av = df_av.set_index(["UNION"])
# join av with denue_av_completo using av_union
df_denue_av_join = df_denue_av.join(df_av, on="av_union", how='right')
df_denue = df_denue.set_index(["id"])
df_denue.drop(labels=["Unnamed: 0"], inplace=True, axis=1)
df_denue_av_join_join = df_denue_av_join.join(df_denue, on="denue_id", how="left")
df_denue_av_data = df_denue_av_join_join[['av_union', 'denue_id', 'distancia','SHAPE_AREA', 'US_ACT2021', 'NOMBRE', 'CATEGORIA', 'codigo_act', 'nombre_act', 'latitud', 'longitud', 'ageb']].sort_values('av_union')

### Create options for services by park
selected_services_by_park = []
for index, park in df_denue_av_data.drop_duplicates('av_union').iterrows():
    label = park['NOMBRE'] + " " + str(park['av_union'])
    value = park['av_union']
    selected_services_by_park.append({'label': label, 'value': value })


@app.callback(
    Output('map_services_by_park', 'figure'),
    Input('select_service_by_park', 'value')
)
def generate_map_services(selected_park):
    ''''
    Generates map of services by green area
    '''
    print("hello")
    selected_park_data = df_denue_av_data[df_denue_av_data['av_union'] == selected_park]
    # setting points of services
    fig = px.scatter_mapbox(
        selected_park_data,
        title="Servicios del ÁREA DEP. MANUEL J. CLOUTHIER (CORREGIDORA-CROMO)",
        lat="latitud",
        lon="longitud",
        color="nombre_act",
        size="distancia",
        size_max=15,
        zoom=10
    )
    # setting the area verde figure
    fig.add_trace(
        go.Choroplethmapbox(
            geojson=sector_k1_av,
            locations=[selected_park],
            featureidkey="properties.UNION"
        )
    )
    # building the layout
    fig.update_layout(
        mapbox = {
            'accesstoken': mapbox_token,
            'style': 'mapbox://styles/mildredgil/cknmcvkgm0tig17nttrh3qymr',
            'center': {'lon': -100.4006, 'lat': 25.67467},
            'zoom': 15,
            'layers': [
                {
                    'source': {
                        'type': 'FeatureCollection',
                        'features': [sector_k1_av['features'][0]]
                    },
                    'type': 'fill', 'below':'traces', 'color': 'green', 'opacity':1
                },
                {
                    'source': {
                        'type': "FeatureCollection",
                        'features': sector_k1_polygon['features']
                    },
                    'type': "fill", 'below': "traces", 'color': "white", "opacity": 0.2
                }
            ]
        },
        margin={'l': 0, 'r': 0, 'b': 0, 't': 0}
    )
    fig.update_layout(showlegend=False)
    return fig


def generate_bubble_graph():
    '''
    Genera una grafica de burbujas de las areas verdes donde:
        - El tamaño de la burbuja es el tamaño del area verde.
        - Su eje x es la cantidad de servicios cerca del area verde.
        - Su eje y es la cantidad de personas cerca del area verde
    '''
    num_services_park = df_denue_av_data.groupby(["av_union", 'SHAPE_AREA', 'NOMBRE']).size().reset_index(name="Cantidad de Servicios")
    fig = px.scatter(
        num_services_park,
        x="Cantidad de Servicios",
        size="SHAPE_AREA",
        color="NOMBRE",
        title="Cantidad de Servicios Por Area Verde"
    )
    return fig

############################# LAYOUT #######################
layout = html.Div([

    ####################################### COMIENZA ESPACIO DE EDICIÓN #######################################

    ## NAVBAR RADIOGRAFIA
    dbc.NavbarSimple(
        expand=True,
        brand="Proyectos",
        dark=True,
        color="black",
        sticky="top",
        children=[
            dbc.DropdownMenu(
                label="Radiografía Urbana",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("¿Qué es?", href="#QueEs"),
                    dbc.DropdownMenuItem("Descripción", href="#Description"),
                    dbc.DropdownMenuItem("Como estamos?", href="#ComoEstamos"),
                    dbc.DropdownMenuItem("Mapa"),
                    dbc.DropdownMenuItem("Datos")
                ]
            )
        ]),


    ## QUE ES? SECTION
    dbc.Row(
        children=[
            dbc.Col(children=[html.H1("Radiografía Urbana")], xs=12, sm=5),
            dbc.Col(children=[
                dbc.Row(id="QueEs", children=dbc.Col(html.H3("Que es?"))),
                dbc.Row(children=[dbc.Col(
                    "Es un apoyo que permite visualizar los espacios públicos " +
                    "usables del municipio de San Pedro Garza Garcia y también mostrar el nivel de " +
                    "accessibilidad que tienen cada uno de estos espacios."
                )])
            ], xs=12, sm=7)
        ]
    ),


    ## BANNER PRINCIPAL
    dbc.Row(
        dbc.Col([
            html.Img(src='../assets/artwall.jpg', style={'maxWidth':'100%', 'height':'auto'})
        ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'})
    ),

    ## DESCRIPTION SECTION
    dbc.Row(
        id="Description",
        children=dbc.Col(children=[html.H2("Descripción:")])
    ),

    dbc.Row(
        children=dbc.Col(
            "A traves de diferentes datos del INEGI y del DENUE, " +
            "se pudieron visualizar las diferentes actividades economicas " +
            "cerca de cada area y tambien medir el nivel de accessibilidad por parque."
        )
    ),

    ## BANNER PRINCIPAL
    dbc.Row(
        dbc.Col([
            html.Img(src='../assets/exposime-sanpedrogarza.png', style={'maxWidth': '100%', 'height': 'auto'})
        ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'})
    ),

    ## COMO ESTAMOS SECTION
    dbc.Row(
        id="ComoEstamos",
        children=dbc.Col(children=[html.H2("¿Cómo estamos?")])
    ),

    dbc.Row(
        dbc.Col(
            dcc.Graph(
                figure=generate_bubble_graph()
            )
        )
    ),

    ## Graph example
    dbc.Row(
        children=[
            dbc.Col(children=html.H3("Servicios del parque:")),
            dbc.Col(
                dbc.Select(
                    id="select_service_by_park",
                    options=selected_services_by_park,
                    placeholder="Selecciona el parque",
                    value=5
                )
            )
        ]
    ),

    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    id="map_services_by_park"
                )
            )
        ]
    ),

    ######################################## TERMINA ESPACIO DE EDICIÓN ########################################

    # Footer
    dbc.Container([
    
        dbc.Row(
            dbc.Col(
              html.H6('Envíanos un correo a implang@sanpedro.gob.mx')  
            ), className='px-1 pt-4'
        ),

        dbc.Row(
            dbc.Col([
                html.A(
                    html.Img(src='../assets/instagram.png', style={'maxWidth':'85px', 'height':'34px'}),
                    href='https://www.instagram.com/implang_spgg/', target='blank'
                ),

                html.A(
                    html.Img(src='../assets/facebook.png', style={'maxWidth':'85px', 'height':'34px'}),
                    href='https://www.facebook.com/implangspgg', target='blank', className='pl-3'
                ),

                html.A(
                    html.Img(src='../assets/twitter.png', style={'maxWidth':'85px', 'height':'34px'}),
                    href='https://twitter.com/implang_spgg', target='blank', className='pl-3'
                ),

                html.A(
                    html.Img(src='../assets/youtube.png',style={'maxWidth':'85px', 'height':'34px'}),
                    href='https://www.youtube.com/channel/UCZwYFPh0dHnKhXqzaxlaqNg', target='blank',
                    className='pl-3'
                )
            ]), className='px-1 py-4'
        )
        
    ]),

    dbc.Container([

       dbc.Row(
            dbc.Col(
                html.H6('Instituto Municipal de Planeación y Gestión Urbana')
            ), className='px-1 pt-3'
        ),

        dbc.Row(
            dbc.Col(
                html.H6('San Pedro Garza García, Nuevo León, México')
            ), className='px-1 py-3'
        )
        
    ], style={'backgroundColor': 'black','color': 'white'}
    )
])