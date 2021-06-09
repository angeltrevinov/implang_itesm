import os
from dotenv import load_dotenv
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json

# loading env
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

# JSONS
sector_k1_polygon = json.load(open("src_files/sector_k1.geojson"))
sector_k1_av = json.load(open("src_files/av_k1.geojson"))

# CSVS
df_denue_av = pd.read_csv("src_files/completo_denue_av.csv") #denue with green areas data
df_av = pd.read_csv("src_files/av_k1.csv") #green areas
df_denue = pd.read_csv("src_files/denue_corregido.csv")  #denue

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
for index, park in df_denue_av_data.drop_duplicates('NOMBRE').iterrows():
    label = park['NOMBRE']
    value = park['NOMBRE']
    selected_services_by_park.append({'label': label, 'value': value })

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
        title=""
    )
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
                                            html.H1(children=["Titulo chidorris"], style={'font-size': '48px'})
                                        ], xs=8),
                                        dbc.Col(children=[
                                            dbc.Row(
                                                dbc.Col(
                                                    className="d-flex",
                                                    children=[
                                                html.H3("Radiografía urbana"), 
                                                html.Span(style={ "background": "#8C1616", "transform": "rotate(-45deg)", "width": "8px", "height": "8px", "margin": "15px",}),
                                                html.H3("San Pedro Garza García")]),
                                            ),
                                            dbc.Row(
                                                className="mt-3",
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            html.P(children=[
                                                                "Conoce nuestra plataforma interactiva que te permite explorar San Pedro a un clic de distancia."
                                                            ], 
                                                            style={"font-size": "20px"}),
                                                            html.P(children=[
                                                                "Aprende sobre sus parques, ubicaciones, población, servicios y más…"
                                                            ], 
                                                            style={"font-size": "20px"}),
                                                            html.P(children=[
                                                                "El objetivo es que las preguntas que tengas acerca del municipio las puedas resolver jugando con los mapas que encuentras aquí. "
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
                dbc.Col(
                    className="mb-5",
                    children=[
                        html.H1(children=["Sabías que..."], style={'font-size': '64px'})
                    ], xs=8),
            ),
            dbc.Row(
                dbc.Col(
                    html.H3(
                        children=["Durante el año 2020 se tuvieron los siguientes datos"],
                        className="mb-5 text-center"
                    )
                )
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
                        xs=3
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
                                                children=["Negocios por área verde"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=3
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
                                                children=["Personas con acceso"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=3
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
                                                children=["m² de area verde"],
                                                style={"font-size": "24px"}
                                            )
                                        ],
                                        className="text-center"
                                    )
                                ]
                            ),
                        ],
                        xs=3
                    )
                ],
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
                                                    "Uno de los atractivos de San Pedro Garza García son sus áreas verdes. Adelante, comienza a buscar las que conoces. ¿Qué tal el parque que está al lado de tu casa, del trabajo, dónde paseas a tu perro? El que quieras. Comienza con aquellos lugares que te resulten familiares. Aunque los conozcas como la palma de tu mano, de seguro vas a aprender algo nuevo. "
                                                ], style={"font-size": "20px"})]
                                            )])
                                        ], xs=12),
                                    ])
                                ],
                                style={"border-left": "5px solid #8C1616", "padding-left": "20px"}
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
                    dbc.Col(children=html.H3("Ánalisis General")),
                ]
            ),

             dbc.Row(
                className="mb-2",
                children=[
                    dbc.Col(
                        dbc.RadioItems(
                            options=[
                                {"label": "Ranking", "value": "ranking"},
                                {"label": "Cantidad de servicios", "value": "cantidad de servicios"},
                                {"label": "Tipología", "value": "TIPOLOGIA"},
                                {"label": "Población", "value": "POBTOT"},
                                {"label": "Viviendas", "value": "VIVTOT"},
                                {"label": "Densidad Poblacional", "value": "densidad poblacional"},
                            ],
                            value="ranking",
                            id="radio_ranking_filter",
                            inline=True,
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
                className="mt-5",
                children=[
                    dbc.Col(children=html.H3("Servicios y demografía por área verde")),
                ]
            ),

             dbc.Row(
                className="mb-2",
                children=[
                    dbc.Col(
                        dbc.Select(
                            id="select_service_by_park",
                            options=selected_services_by_park,
                            placeholder="Selecciona el parque",
                            value='PARQUE VERDE LIMON'
                        )
                    ),
                    
                    dbc.RadioItems(
                        options=[
                            {"label": "Viviendas", "value": "viviendas"},
                            {"label": "Población", "value": "población"},
                            {"label": "Mujeres", "value": "mujeres"},
                            {"label": "Hombres", "value": "hombres"},
                            {"label": "Área", "value": "area"},
                            {"label": "Densidad poblacional", "value": "densidad poblacional"},
                        ],
                        value="viviendas",
                        id="radio_filter",
                        inline=True,
                    ),

                    dbc.Checklist(
                        options=[
                            {"label": "Servicios", "value": "services"},
                        ],
                        value=["services"],
                        id="switches_servicios",
                        switch=True,
                    ),
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
                                                    "Sabemos que un área verde es un punto de reunión muy concurrido para todos y los negocios son beneficiados al encontrarse cerca.",
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "En total hay ",
                                                    html.Strong(children=["688 negocios"], style={"color": "#8C1616"}),
                                                    " diferentes dentro del Sector K1", 
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Alrededor de cada area verde hay en promedio ", 
                                                    html.Strong(children=["79 negocios"], style={"color": "#8C1616"}),
                                                    " a una distancia radial menor de 400 metros"
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Los comercios más frecuentes son", 
                                                    html.Strong(children=[" tiendas de abarrotes, comercio de cervezas, papelerias, escuelas preescolares y restaurantes de tacos y tortas"], style={"color": "#8C1616"}),
                                                ], style={"font-size": "20px"})]
                                            )])
                                        ], xs=12)
                                    ])
                                ]
                            ),
                            dbc.Col(children=[html.Img(src='../assets/bussiness_transparent.png', style={'width':'80%','height':'auto'})], xs=4)
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center', "border-left": "5px solid #8C1616", "padding-left": "20px"}
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
                html.Img(src='../assets/cerro_silla.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
    ),

    ## COMO ESTAMOS SECTION
    dbc.Container(
        children=[
            dbc.Row(
                id="ComoEstamos",
                children=dbc.Col(children=[html.H2("¿Cuántos servicios hay por area verde?")])
            ),
            

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        figure=generate_bubble_graph()
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
                                                    "Content"
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Content"
                                                ], style={"font-size": "20px"})]
                                            )]),
                                            dbc.Row(children=[dbc.Col(
                                                children=[html.P(children=[
                                                    "Content"
                                                ], style={"font-size": "20px"})]
                                            )])
                                        ], xs=12)
                                    ])
                                ]
                            ),
                            dbc.Col(children=[html.Img(src='../assets/nature_people_circle.png', style={'width':'80%','height':'auto'})], xs=4),
                            
                        ],
                        style={'width': '90%', 'margin': 'auto', 'align-items': 'center', "border-left": "5px solid #8C1616", "padding-left": "20px"}
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
                html.Img(src='../assets/Rectangle 6.png', style={'maxWidth':'100%', 'height':'auto', 'width': '100%',})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '100px'}
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
                html.Img(src='../assets/Rectangle 6.png', style={'maxWidth':'100%', 'height':'180px', 'width': '100%', "object-fit": "cover"})
            ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'}),
        ],
        style={'background-color': '#BF9517', 'margin-top': '100px', 'margin-bottom': '0px'}
    ),
    
])