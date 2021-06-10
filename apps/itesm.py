import os
from dotenv import load_dotenv
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import base64
import numpy as np
import plotly.graph_objects as go

# loading env
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

# JSONS
sector_k1_polygon = json.load(open("src_files/sector_k1.geojson"))
sector_k1_av = json.load(open("src_files/av_k1.geojson"))

# CSVS
df_denue_ranking = pd.read_csv("src_files/denue_ranking.csv") #denue with green areas data
df_denue_av = pd.read_csv("src_files/completo_denue_av.csv") #denue with green areas data
df_av = pd.read_csv("src_files/av_k1.csv") #green areas
df_denue = pd.read_csv("src_files/denue_corregido.csv")  #denue
df_av_inegi = pd.read_csv("src_files/inegi_av_98.csv") #inegi

##### SET UP TABLES
df_av = df_av.set_index(["UNION"])
# join av with denue_av_completo using av_union
df_denue_av_join = df_denue_av.join(df_av, on="av_union", how='right')
df_denue = df_denue.set_index(["id"])
df_denue.drop(labels=["Unnamed: 0"], inplace=True, axis=1)
df_denue_av_join_join = df_denue_av_join.join(df_denue, on="denue_id", how="left")
df_denue_av_data = df_denue_av_join_join[['av_union', 'denue_id', 'distancia','SHAPE_AREA', 'US_ACT2021', 'NOMBRE', 'CATEGORIA', 'codigo_act', 'nombre_act', 'latitud', 'longitud', 'ageb']].sort_values('av_union')

# Create options for services by park
selected_services_by_park = []
for index, park in df_denue_av_data.drop_duplicates('NOMBRE').iterrows():
    label = park['NOMBRE']
    value = park['NOMBRE']
    selected_services_by_park.append({'label': label, 'value': value })

ranking_services = []
for park_name_services in df_denue_ranking.groupby("NOMBRE_PARQUE").count().sort_values("cantidad de servicios", ascending=False)[["cantidad de servicios"]].head(3).iterrows():
    services = df_denue_ranking[df_denue_ranking['NOMBRE_PARQUE'] == park_name_services[0]].groupby("nombre_act").count().sort_values("av_union",ascending=False).head(3)
    ranking_services.append({"park_name": park_name_services[0], "count": park_name_services[1]["cantidad de servicios"], "services": list(services.index)})

ranking_population = []
for park_name_inegi in df_denue_ranking.groupby("NOMBRE_PARQUE").first().sort_values("POBTOT", ascending=False)[["VIVTOT","POBTOT", "densidad poblacional", "area"]].head(3).iterrows():
    ranking_population.append({
        "park_name": park_name_inegi[0], 
        "poblacion": park_name_inegi[1]["POBTOT"],
        "viviendas": park_name_inegi[1]["VIVTOT"],
        "densidad": 1 / park_name_inegi[1]["densidad poblacional"],
        "area": park_name_inegi[1]["area"]
        })

def generate_bubble_graph():
    '''
    Genera una grafica de burbujas de las areas verdes donde:
        - El tamaño de la burbuja es el tamaño del area verde.
        - Su eje x es la cantidad de servicios cerca del area verde.
        - Su eje y es la cantidad de personas cerca del area verde
    '''
    num_serv_pob_by_park = df_denue_ranking[["NOMBRE_PARQUE", "cantidad de servicios", "POBTOT", "distancia promedio a los servicios", "tamano_mts"]]
    num_serv_pob_by_park = num_serv_pob_by_park[num_serv_pob_by_park['NOMBRE_PARQUE'] != "ÁREA DEP. MANUEL J. CLOUTHIER (CORREGIDORA-CROMO)"]
    num_serv_pob_by_park = num_serv_pob_by_park.drop_duplicates()
    num_serv_pob_by_park['tamano_mts'] = num_serv_pob_by_park['tamano_mts'].div(1000000).round(4)
    num_serv_pob_by_park["distancia promedio a los servicios"] = num_serv_pob_by_park["distancia promedio a los servicios"].round(0)
    num_serv_pob_by_park.rename(columns={'NOMBRE_PARQUE': 'Nombre del parque', 'POBTOT': 'Población con accesso al parque', 'tamano_mts': 'tamaño en km2'}, inplace=True)

    fig = px.scatter(
        num_serv_pob_by_park,
        hover_name='Nombre del parque',
        x="cantidad de servicios",
        y="Población con accesso al parque",
        color="distancia promedio a los servicios",
        size="tamaño en km2",
        color_continuous_scale=['#590E0E', '#8C1616', '#CC730E', '#D6900F', '#FFC71F', "#BDB655", "#9CA653", "#6C7339"]
    )
    fig.update_layout(margin=dict(t=28,b=0,l=0,r=0), height=400)

    return fig

def generate_donut_graph():
    '''
    Genera grafica de donut con los datos poblacionales
    '''
    
    #prepare inegi data
    df_ages = df_av_inegi[["POBTOT", 'P_0A2', 'P_3A5', 'P_6A11', 'P_8A14', 'P_15A17', 'P_18A24', 'P_60YMAS']].fillna(0).replace("*", 0).astype(int)
    df_ages["P_25A59"] =  df_ages["POBTOT"] - (df_ages["P_0A2"] + df_ages["P_3A5"] + df_ages["P_6A11"] + df_ages["P_8A14"] + df_ages["P_15A17"] + df_ages["P_18A24"] + df_ages["P_60YMAS"])
    df_ages_sum = df_ages.agg(
        {
            'P_0A2': ['sum'], 
            'P_3A5': ['sum'], 
            'P_6A11': ['sum'],
            'P_8A14': ['sum'],
            'P_15A17': ['sum'],
            'P_18A24': ['sum'],
            'P_25A59': ['sum'],
            'P_60YMAS': ['sum'],
            'POBTOT': ['sum'],
        }
        ) 

    df_ages_sum.rename(columns={
            'P_0A2': '0 a 2 años',
            'P_3A5': '3 a 5 años',
            'P_6A11': '6 a 11 años',
            'P_8A14': '8 a 14 años',
            'P_15A17': '15 a 17 años',
            'P_18A24': '18 a 24 años',
            'P_25A59': '25 a 59 años',
            'P_60YMAS': '60+ años',
            'POBTOT': 'total',
        }, inplace=True)

    df_ages_sum = df_ages_sum.melt(
            var_name="edad", 
            value_name="personas")

    fig = px.pie(df_ages_sum[df_ages_sum['edad'] != "total"], values='personas', names='edad', color='edad', hole=.35,
             color_discrete_map={
                '0 a 2 años': "#B0B591",
                '3 a 5 años': "#9CA653",
                '6 a 11 años': "#A68114",
                '8 a 14 años': "#BF9517",
                '15 a 17 años': "#EDF2C2",
                '18 a 24 años': '#E0AF1B',
                '25 a 59 años': '#FFE359',
                '60+ años': '#FFC71F'
                })
                
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=350)

    return fig

############################# LAYOUT #######################
layout = html.Div([

    ## NAVBAR RADIOGRAFIA
    dbc.NavbarSimple(
        expand=True,
        brand="Proyectos",
        dark=True,
        color="black",
        sticky="top",
        children=[
            html.P(className="navbar-brand mb-0", children=["Radiografía Urbana"])
        ]),

    ## Conoce lo verde de tu ciudad SECTION
    html.Div(
        id="QueEs",
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(children=[html.Img(src='../assets/nature_circle.png', style={'width':'80%','height':'auto'})], xs=4),
                            dbc.Col(
                                xs=8,
                                children=[
                                    dbc.Row(children=[
                                        dbc.Col(children=[
                                            html.H1(children=["¡Échale un vistazo a los parques de San Pedro Garza García!"], style={'font-size': '48px'})
                                        ], xs=8),
                                        dbc.Col(children=[
                                            dbc.Row(
                                                dbc.Col(
                                                    className="d-flex",
                                                    children=[
                                                html.Span(style={ "background": "#1F67A6", "transform": "rotate(-45deg)", "width": "8px", "height": "8px", "margin": "15px",}),
                                                html.H3("Radiografía urbana"), 
                                                ]),
                                            ),
                                            dbc.Row(
                                                className="mt-3",
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            html.P(children=[
                                                                "Conoce nuestra plataforma interactiva que te permitirá explorar San Pedro a un clic de distancia.",
                                                                " Aprende sobre sus parques, ubicaciones, población, servicios y más…",
                                                                html.Br(),
                                                                "El objetivo es que las preguntas que tengas acerca de las áreas verdes del municipio las puedas resolver descubriendo los mapas y gráficos que encontraras aquí. "
                                                            ], 
                                                            style={"font-size": "20px"}),
                                                        ]
                                                    )
                                                ]
                                            )
                                        ], xs=12)
                                    ])
                                ]
                            )
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center'}
                    ),
                ],
                style={'position': 'relative', 'z-index': '1', 'top': "180px", 'width': '100%'}
            ),
        ]
    ),
    
    
    ## BANNER PRINCIPAL
    dbc.Row(
        children=[
            dbc.Col([
                html.Img(src='../assets/radiografia_urbana.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
    ),

    # KPI Principales
    dbc.Container(
        children=[
            dbc.Row(
                className="d-flex mb-5",
                children=[
                    html.H1(children=["Sabías que",html.H3(
                        children=["hasta el año 2020 se tiene registro que hay..."],
                        className="ml-3 text-center"
                    )], style={'font-size': '64px', 'display': 'flex', 'align-items': 'baseline'}),
                ]
            ),
            
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            dbc.Card(
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["68"],
                                                style={'color':"#BF9517", "font-size": "3rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.Img(src='../assets/nature_2.png', style={'height': '100px'}),
                                            html.P(
                                                children=["Áreas verdes"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=3,
                    ),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["275K"],
                                                style={'color':"#BF9517", "font-size": "3rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.Img(src='../assets/green_area.png', style={'height': '100px'}),
                                            html.P(
                                                children=["Personas viviendo a 5 minutos"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=3,
                    ),

                    dbc.Col(
                        children=[
                            dbc.Card(
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["~79"],
                                                style={'color':"#BF9517", "font-size": "3rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.Img(src='../assets/bussiness.png', style={'height': '100px'}),
                                            html.P(
                                                children=["Negocios alrededor de cada área verde"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=3,
                    ),
                    
                    dbc.Col(
                        children=[
                            dbc.Card(
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["392K"],
                                                style={'color':"#BF9517", "font-size": "3rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.Img(src='../assets/park.png', style={'height': '100px'}),
                                            html.P(
                                                children=["m² de solo área verde"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=3,
                    )
                ],
            ),
            dbc.Row(
                className="mt-5",
                children=[
                dbc.Col(
                    html.H3(
                        children=["¿Cuántas áreas verdes conoces tú?"],
                        className="mb-5 text-center"
                    )
                )]
            ),

            dbc.Row(
                className="mt-3",
                children=[
                dbc.Col(
                    html.P(
                        children=["Cada uno de estos parques tiene negocios que los rodean. Así como las viviendas tienen amenidades, los parques tienen servicios. Además de disfrutar de una bonita vista y un paseo relajante, también puedes visitar tiendas de abarrotes, papelerías, restaurantes, cafeterías y demás. Lo que sea que necesites, lo tienes a tu alcance."],
                        className="mb-5"
                    )
                )]
            ),

            dbc.Row(
                children=[
                dbc.Col(
                    html.P(
                        children=["¿Te has preguntado cuántos servicios tiene tu parque favorito? ¿Cuáles servicios consideras más importantes? Ya sea que te guste ir al parque y después consentirte con algún antojito de algún restaurante, o quizás tomar un café, de seguro vas al parque también por aquellos lugares que te gusta visitar a unos cuantos pasos de distancia."],
                        className="mb-5"
                    )
                )]
            ),
        ],
    ),

    ## Areas Verdes SECTION
    html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(children=[html.Img(src='../assets/park_transparent.png', style={'width':'80%','height':'auto'})], xs=4),
                            dbc.Col(
                                xs=8,
                                children=[
                                    dbc.Row(children=[
                                        dbc.Col(children=[
                                            html.H1(children=["Áreas verdes"], style={'font-size': '64px'})
                                        ], xs=8),
                                        dbc.Col(children=[
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Uno de los atractivos de San Pedro Garza García son sus áreas verdes. Adelante, comienza a buscar las que conoces. ¿Qué tal el parque que está al lado de tu casa, del trabajo, dónde paseas a tu perro? Él que quieras. Comienza con aquellos lugares que te resulten familiares. Aunque los conozcas como la palma de tu mano, de seguro vas a aprender algo nuevo. "
                                                ], style={"font-size": "20px"})]
                                            )])
                                        ], xs=12),
                                    ])
                                ],
                                style={"border-left": "5px solid #1F67A6", "padding-left": "20px"}
                            ),
                            
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center'}
                    ),
                ],
                style={'position': 'relative', 'z-index': '1', 'top': "210px", 'width': '100%'}
            ),
        ]
    ),

    

    ## IMAGEN
    dbc.Row(
        children=[
            dbc.Col([
                html.Img(src='../assets/parque_san_pedro.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
    ),


## Green areas map
    dbc.Container(
        children=[
            dbc.Row(
                children=[
                    dbc.Col(children=html.H3("¡Explora!")),
                ]
            ),

            dbc.Row(
                children=[
                    dbc.Col(children=html.P("Aquí tienes un mapa con las áreas verdes del municipio. "\
                        + "¿Te haz preguntado cómo se ven por categorías? ¿Cuál es el más grande, el más poblado?"\
                        + "¿Cuantas casas hay por cada uno? y ¿servicios cercanos? Usa los filtros para verlos a más detalle."
                        )),
                ]
            ),

            dbc.Row(
                className="mb-3",
                children=[
                    dbc.Col(children=html.P("Con esto en mente, déjate llevar por tu curiosidad… ")),
                ]
            ),

            dbc.Row(
                className="mb-2",
                children=[
                    dbc.Col(
                        dbc.RadioItems(
                            className="d-flex justify-content-between",
                            options=[
                                {"label": "Población", "value": "POBTOT"},
                                {"label": "Viviendas", "value": "VIVTOT"},
                                {"label": "Densidad Poblacional", "value": "densidad poblacional"},
                                {"label": "Cantidad de servicios", "value": "cantidad de servicios"},
                                {"label": "Tipología", "value": "TIPOLOGIA"},
                                {"label": "* Puntuación", "value": "ranking"},
                            ],
                            value="ranking",
                            id="radio_ranking_filter",
                            inline=True,
                            labelCheckedStyle={"color": "#8C1616"},
                        )
                    ),
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="map_ranking_park"
                        )
                    )
                ]
            ),

            dbc.Row(
                className="mt-1",
                children=[
                    dbc.Col(
                        children=
                    html.Span(
                        style={"font-size": "12px"},
                        children=["* La puntuación está calculada tomando en cuenta la cantidad de servicios, población, viviendas y densidad poblacional."]
                        )
                    ),
                ]
            ),


            dbc.Row(
                className="mt-5",
                children=[
                    dbc.Col(children=html.H3("¿Buscas un área en específico?")),
                ]
            ),

            dbc.Row(
                className="mt-1 mb-3",
                children=[
                    dbc.Col(children=html.P("Aquí puedes buscar tu parque favorito o el más cercano a tu casa, ¡el que gustes! Puedes observar la cantidad de hombres o mujeres que hay en el área, las viviendas, la densidad poblacional y el tamaño del área. Puedes buscar el parque más grande, el más chico, el que tiene mayor tamaño, donde hay más gente, etc. Busca la respuesta cada una de tus preguntas con este mapa interactivo.")),
                ]
            ),

            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            dbc.Label("Área verde"),
                            dbc.Select(
                                id="select_service_by_park",
                                options=selected_services_by_park,
                                placeholder="Selecciona el parque",
                                value='PARQUE VERDE LIMON'
                            )
                        ]
                    ),

                    dbc.Col(
                        children=[
                            dbc.Label("Filtros"),
                            dbc.RadioItems(
                            className="d-flex justify-content-between mb-3",
                            options=[
                                {"label": "Viviendas", "value": "viviendas"},
                                {"label": "Población", "value": "población"},
                                {"label": "Mujeres", "value": "mujeres"},
                                {"label": "Hombres", "value": "hombres"},
                                {"label": "Área", "value": "area"},
                                {"label": "Densidad", "value": "densidad poblacional"},
                            ],
                            value="viviendas",
                            id="radio_filter",
                            inline=True,
                        ),]
                    )
                ]
            ),
            
            
            dbc.Row(
                    className="my-3",
                    children=[dbc.Col(
                        children=[
                            dbc.Checklist(
                                options=[
                                    {"label": "Visualizar servicios", "value": "services"},
                                ],
                                value=["services"],
                                id="switches_servicios",
                            )
                        ]
                    )]
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
            
        ]
    ),

    ## DESCRIPTION SECTION
    html.Div(
        id="Description",
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                xs=8,
                                children=[
                                    dbc.Row(
                                        children=[
                                        dbc.Col(children=[
                                            html.H1(children=["Servicios"], style={'font-size': '64px'})
                                        ], xs=8),
                                        dbc.Col(children=[
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "¿Los parques son más populares por los negocios que los rodean o los negocios son más exitosos como las áreas verdes que hay a su alrededor? Los parques suelen ser un punto de reunión muy común. Quizás después de estar un rato al aire libre gustes ir a un restaurante, por nieve o tal vez un café. ¿A cuál irías? Si vas seguido, es probable que sea el más cercano, por la comodidad de tenerlo al alcance.",
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Los servicios que se pueden apreciar en los mapas también son escuelas, papelerías, hospitales y muchos más. En total, hay ",
                                                    html.Strong(children=["688 negocios"], style={"color": "#1F67A6"}),
                                                    " diferentes en la zona.", 
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "¿Sabías que alrededor de cada área verde hay un promedio de ", 
                                                    html.Strong(children=["79 negocios a 5 minutos caminando?"], style={"color": "#1F67A6"}),
                                                    " Ahora lo sabes."
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    " Los comercios más populares son ", 
                                                    html.Strong(children=[" las tiendas de abarrotes, comercio de cervezas, papelerías, escuelas preescolares y restaurantes de tacos y tortas."], style={"color": "#1F67A6"}),
                                                ], style={"font-size": "20px"})]
                                            )])
                                        ], xs=12)
                                    ])
                                ]
                            ),
                            dbc.Col(children=[html.Img(src='../assets/bussiness_transparent.png', style={'width':'80%','height':'auto'})], xs=4)
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center', "border-left": "5px solid #1F67A6", "padding-left": "20px"}
                    ),
                ],
                style={'position': 'relative', 'z-index': '1', 'top': "210px", 'width': '100%'}
            ),
        ]
    ),
    
    
    ## BANNER SERVICIOS
    dbc.Row(
        children=[
            dbc.Col([
                html.Img(src='../assets/servicios.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
    ),

    ## COMO ESTAMOS SECTION
    dbc.Container(
        children=[
            dbc.Row(
                className="my-5",
                children=[
                    html.H2("Top 3: Áreas verdes con más servicios a su alrededor"),
                ]
            ),
            
            dbc.Row(
                className="d-flex align-items-end",
                #style={"background": "linear-gradient(1deg, #e0af1b, transparent)", "padding": "20px"},
                children=[
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["2"],
                                                style={'color':"#BF9517", "font-size": "4rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_services[1]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str(ranking_services[1]["count"]) + " servicios"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["Principales Servicios:"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[", ".join(ranking_services[1]["services"])],
                                                style={"font-size": "12px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["1"],
                                                style={'color':"#BF9517", "font-size": "4.5rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_services[0]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str(ranking_services[0]["count"]) + " servicios"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["Principales Servicios:"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[", ".join(ranking_services[0]["services"])],
                                                style={"font-size": "12px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["3"],
                                                style={'color':"#BF9517", "font-size": "2.5rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_services[2]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str(ranking_services[2]["count"]) + " servicios"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["Principales Servicios:"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[", ".join(ranking_services[2]["services"])],
                                                style={"font-size": "12px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            ),

            dbc.Row(
                id="ComoEstamos",
                className="my-5",
                children=dbc.Col(children=[html.H2("¿Cuántos servicios hay por área verde?")])
            ),

            dbc.Row(
                children=[
                    dbc.Col(
                        html.P("En la siguente gráfica se puede ver la cantidad de servicio y la población que tiene acceso a los parques. Cada círculo representa un parque. Como puedes ver, algunos círculos son más grandes que otros. El tamaño representa el área del parque. ¿Cuántos servicios hay en tu parque favorito?")
                    )
                ]
            ),

            
            dbc.Row(
                className="mt-1",
                children=[
                    dbc.Col(
                        children=
                    html.Span(
                        style={"font-size": "12px"},
                        children=["*El tamaño de los círculos representa el área en km cuadrados"]
                        )
                    ),
                ]
            ),
            
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        figure=generate_bubble_graph()
                    )
                )
            ),

            dbc.Row(
                className="my-5",
                children=dbc.Col(children=[html.H2("Descubre los servicios que rodean a tu parque")])
            ),

            dbc.Row(
                className="my-5",
                children=[
                    dbc.Col(
                        children=[
                            dbc.FormGroup(
                                [
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Áreas verdes con mayor cantidad de servicios", "value": True},
                                            {"label": "Áreas verdes con menor cantidad de servicios", "value": False},
                                        ],
                                        value=True,
                                        id="sunburst_services_type",
                                    ),
                                ]
                            )
                        ],
                        xs=6,
                        xl=6
                    ),
                    dbc.Col(
                        children=[
                            dbc.Label("¿Cuántas áreas quieres explorar?"),
                            dbc.Select(
                                id="sunburst_services_top",
                                options=[
                                    {'label': '3', 'value': 3},
                                    {'label': '5', 'value': 5},
                                    {'label': '10', 'value': 10},
                                    {'label': '15', 'value': 15},
                                    {'label': '20', 'value': 20}
                                ],
                                placeholder="Selecciona...",
                                value=5
                            )
                        ],
                        xs=6,
                        xl=6
                    )
                ]
            ),
            
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="sunburst_services"
                    )
                )
            ),
        ]
    ),

    ## Datos demograficos SECTION
    html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                xs=8,
                                children=[
                                    dbc.Row(children=[
                                        dbc.Col(children=[
                                            html.H1(children=["Datos Demográficos"], style={'font-size': '64px'})
                                        ], xs=8),
                                        dbc.Col(children=[
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "¿Qué sabes acerca de la comunidad que visita estos parques? " 
                                                ], style={"font-size": "20px"})]
                                            )]),

                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "En total hay "
                                                    , html.Strong(children=["275,920 personas"], style={"color": "#1F67A6"})
                                                    ," que viven a menos de "
                                                    , html.Strong(children=["5 minutos "], style={"color": "#1F67A6"})
                                                    ,"caminando de un parque. "
                                                    , "El tamaño de las áreas verdes en conjunto es de"
                                                    , html.Strong(children=[" 392,820 m², "], style={"color": "#1F67A6"})
                                                    ,"¿puedes creerlo? Si se distribuye esa área en la cantidad de gente que hay en el municipio habría"
                                                    , html.Strong(children=[" 1 persona "], style={"color": "#1F67A6"})
                                                    , "por cada"
                                                    , html.Strong(children=["  1.42m². "], style={"color": "#1F67A6"})
                                                ], style={"font-size": "20px"})]
                                            )]),

                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                     "¿Se te hace más o menos de lo que esperabas? " 
                                                    , "En estos gráficos tienes acceso a la información y podrás tener la certeza de que conoces tu comunidad."
                                                ], style={"font-size": "20px"})]
                                            )]),
                                        ], xs=12)
                                    ])
                                ]
                            ),
                            dbc.Col(children=[html.Img(src='../assets/nature_people_circle.png', style={'width':'80%','height':'auto'})], xs=4),
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center', "border-left": "5px solid #1F67A6", "padding-left": "20px"}
                    ),
                ],
                style={'position': 'relative', 'z-index': '1', 'top': "210px", 'width': '100%'}
            ),
        ]
    ),


    ## IMAGEN
    dbc.Row(
        children=[
            dbc.Col([
                html.Img(src='../assets/Rectangle 5.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
    ),

    
    ## COMO ESTAMOS SECTION
    dbc.Container(
        children=[
            dbc.Row(
                className="my-5",
                children=[
                    html.H2("Top 3: Áreas verdes con mayor población a su alrededor"),
                ]
            ),
            
            dbc.Row(
                className="d-flex align-items-end",
                #style={"background": "linear-gradient(1deg, #e0af1b, transparent)", "padding": "20px"},
                children=[
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["2"],
                                                style={'color':"#BF9517", "font-size": "4rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_population[1]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[1]["poblacion"], 0))) + " Personas a menos de 5 minutos"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["La densidad poblacional equivala a 1 persona por cada ", str(round(ranking_population[1]["densidad"], 0)), " metros cuadrados"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[1]["area"], 0))), " m² de área de alcance total de personas a 5 minutos",],
                                                style={"font-size": "16px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["1"],
                                                style={'color':"#BF9517", "font-size": "4.5rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_population[0]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[0]["poblacion"], 0))) + " Personas a menos de 5 minutos"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["La densidad poblacional equivala a 1 persona por cada ", str(round(ranking_population[0]["densidad"], 0)), " metros cuadrados"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[0]["area"], 0))), " m² de área de alcance total de personas a 5 minutos",],
                                                style={"font-size": "16px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                    dbc.Col(
                        xs=4,
                        children=[
                            dbc.Card(
                                style={"box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["3"],
                                                style={'color':"#BF9517", "font-size": "2.5rem"},
                                                className="mx-2 my-3"
                                            ),
                                            html.P(
                                                children=[ranking_population[2]["park_name"]],
                                                style={"font-size": "24px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[2]["poblacion"], 0))) + " Personas a menos de 5 minutos"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=["La densidad poblacional equivala a 1 persona por cada ", str(round(ranking_population[2]["densidad"], 0)), " metros cuadrados"],
                                                style={"font-size": "16px"}
                                            ),
                                            html.P(
                                                children=[str("{:,}".format(round(ranking_population[2]["area"], 0))), " m² de área de alcance total de personas a 5 minutos",],
                                                style={"font-size": "16px"}
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            ),

            dbc.Row(
                className="mt-5",
                children=[
                    dbc.Col(
                        children=[
                            html.H2("¿Quién vive a solo 5 minutos caminando?")
                        ]
                    ),
                ]
            ),

            dbc.Row(
                id="ComoEstamos",
                children=
                [
                    dbc.Col(
                        children=[
                            dbc.Card(
                                className="my-3",
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                children=["Género"],
                                                style={'color':"#BF9517", "font-size": "3rem"},
                                                className="mx-2 my-3"
                                            ),
                                            dbc.Row(
                                                className="d-flex justify-content-center ",
                                                style={"align-items": "flex-end"},
                                                children=[
                                                    html.Div(
                                                        style={"margin-right": "4px","background-color": "#1F67A6", "height": "336px", "flex-direction": "column", "justify-content": "space-evenly", "display": "flex"},
                                                        children=[
                                                            html.P(style={"font-size": "16px",},className="text-white",children=["136,255", html.Br(), "hombres"]),
                                                            html.Img(
                                                                width=200,
                                                                src='data:image/svg+xml;base64,{}'.format(
                                                                base64.b64encode(open("assets/male.svg", 'rb').read()).decode() 
                                                            )),
                                                            html.P(style={"font-size": "32px", "font-weight": "bold"},className="text-white",children=["49%"])
                                                        ]
                                                    ),
                                                    html.Div(
                                                        style={"background-color": "#8C1616", "height": "350px", "flex-direction": "column", "justify-content": "space-evenly", "display": "flex"},
                                                        children=[
                                                            html.P(style={"font-size": "16px",},className="text-white",children=["139,552", html.Br(), " mujeres"]),
                                                            html.Img(
                                                                width=200,
                                                                src='data:image/svg+xml;base64,{}'.format(
                                                                base64.b64encode(open("assets/female.svg", 'rb').read()).decode() 
                                                            )),
                                                            html.P(style={"font-size": "32px", "font-weight": "bold"},className="text-white",children=["51%"])
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=6,
                    ),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                className="my-3",
                                style={'min-height': '350px', "box-sizing": "border-box", "box-shadow": "0px 1px 4px rgba(0, 0, 0, 0.2)", "border-radius": "6px"},
                                children=[
                                    dbc.CardBody(
                                        children=[
                                            html.H2(
                                                    children=["Por edad"],
                                                    style={'color':"#BF9517", "font-size": "3rem"},
                                                    className="mx-2 my-3"
                                            ),
                                            dcc.Graph(
                                                figure=generate_donut_graph()
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=12,
                        xl=6,
                    ),
                ]
            ),

            dbc.Row(
                className="my-5",
                children=[
                    dbc.Col(
                        children=[
                            html.H2("Distribución demográfica por área verde")
                        ]
                    ),
                ]
            ),

            dbc.Row(
                dbc.Col(
                        [
                            dbc.Label("Selecciona un área verde"),
                            dbc.Select(
                                id="select_service_by_park_demo",
                                options=selected_services_by_park,
                                placeholder="Selecciona el parque",
                                value='PARQUE VERDE LIMON'
                            )
                        ]
                    ),
            ),

            dbc.Row(
                className="mt-5",
                children=[
                    dbc.Col(
                        dcc.Graph(
                            id="demographic_bar"
                        )
                    )
                ]
            ),
        ]
    ),
    

    
    ######################################## TERMINA ESPACIO DE EDICIÓN ########################################

    ## REDES SOCIALES SECTION
    html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                xs=12,
                                children=[
                                    dbc.Row(children=[
                                        dbc.Col(children=[
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.A(
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
                                                    ),
                                                    ])
                                            ]),
                                        ], xs=4),
                                        dbc.Col(
                                            html.H6('Instituto Municipal de Planeación y Gestión Urbana')
                                        ),
                                        dbc.Col(
                                            html.H6('Envíanos un correo a implang@sanpedro.gob.mx')  
                                        )
                                    ])
                                ]
                            ),
                            
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center'}
                    ),
                ],
                style={'position': 'relative', 'z-index': '1', 'top': "210px", 'width': '100%'}
            ),
        ]
    ),

    ## FOOTER
    dbc.Row(
        children=[
            dbc.Col([
                html.Img(src='../assets/Rectangle 5.png', style={'maxWidth':'100%', 'height':'180px', 'width': '100%', "object-fit": "cover"})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '0px'}
    ),
    
])