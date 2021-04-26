import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px

##### MIEMBROS
# - Julia Jimenez A00821428
# - Angel Treviño A01336559
# - Mildred Gil A00820397
#- Mauricio Lozano A01194301



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
                    dbc.DropdownMenuItem("Descripción"),
                    dbc.DropdownMenuItem("Como estamos?"),
                    dbc.DropdownMenuItem("Mapa"),
                    dbc.DropdownMenuItem("Datos")
                ]
            )
        ]),


    ## QUE ES? SECTION
    dbc.Row(
        children=[
            dbc.Col(children=[html.H1("Radiografía Urbana")]),
            dbc.Col(children=[
                dbc.Row(id="QueEs", children=html.H3("Que es?")),
                dbc.Row("Lorem ipsum")
            ])
        ]
    ),


    ## BANNER PRINCIPAL
    dbc.Row(
        dbc.Col([
            html.Img(src='../assets/imagen.png', style={'maxWidth':'100%', 'height':'auto'}),
            html.H2('Ejemplo título banner',
                style={'position': 'absolute', 'top': '50%', 'left': '50%',
                'transform': 'translate(-50%, -50%)'})
        ], style={'color': 'white', 'position': 'relative', 'textAlign': 'center'})
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