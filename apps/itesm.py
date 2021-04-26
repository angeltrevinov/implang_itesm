import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go


##### MIEMBROS
# - Julia Jimenez A00821428
# - Angel Treviño A01336559
# - Mildred Gil A00820397
#- Mauricio Lozano A01194301


###################### LOGIC ###############################
fig = go.Figure(data=[go.Scatter(
    x=[1, 2, 3, 4], y=[10, 11, 12, 13],
    text=['A<br>size: 40', 'B<br>size: 60', 'C<br>size: 80', 'D<br>size: 100'],
    mode='markers',
    marker=dict(
        color=['rgb(140, 22, 22)', 'rgb(31, 103, 166)', 'rgb(191,149,23)', 'rgb(156, 166, 83)'],
        size=[40, 60, 80, 100],
    )
)])


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
                    dbc.DropdownMenuItem("Qué es?", href="#QueEs"),
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
                dbc.Row(children=[dbc.Col("Lorem ipsum")])
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
        children=dbc.Col(children="Lorem ipsum")
    ),

    ## BANNER PRINCIPAL
    dbc.Row(
        dbc.Col([
            html.Img(src='../assets/artwall.jpg', style={'maxWidth': '100%', 'height': 'auto'})
        ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'})
    ),

    ## COMO ESTAMOS SECTION
    dbc.Row(
        id="ComoEstamos",
        children=dbc.Col(children=[html.H2("Como Estamos?")])
    ),

    ## Graph example
    dbc.Row(
        dbc.Col(
            dcc.Graph(
                figure=fig
            )
        )
    ),

    ## SECCIÓN 1
    dbc.Container([
        
        ## Títutlo
        dbc.Row(
            dbc.Col(
                html.H2('Ejemplo de título')
            ), className='px-1 pt-4'
        ),

        ## Texto
        dbc.Row(
            dbc.Col(
                html.H5('La bicicleta tiene enormes beneficios no sólo para la salud sino también para el medio ambiente, ya que se trata de un medio de transporte que favorece la movilidad sostenible.')  
            ), className='px-1 py-4'
        )

    ]),


    ## SECCION 2
    dbc.Container([
        # Título
        dbc.Row(
            dbc.Col(
                html.H2('Otro ejemplo de título')
                ),className='py-3', style={'backgroundColor': 'black','color': 'white'}
            ),

        ## Texto
        dbc.Row([
            dbc.Col(
                html.H5('La bicicleta tiene enormes beneficios no sólo para la salud sino también para el medio ambiente, ya que se trata de un medio de transporte que favorece la movilidad sostenible.'), lg=3, md=9, sm=4
            ),
            dbc.Col(
                html.H5('La bicicleta tiene enormes beneficios no sólo para la salud sino también para el medio ambiente, ya que se trata de un medio de transporte que favorece la movilidad sostenible.'), lg=9, md=3, sm=8
            ), 
        ],className='py-3')

    ]),

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