import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output


app = dash.Dash(__name__, title='Instituto Municipal de Planeación y Gestión Urbana - IMPLANG', external_stylesheets=[dbc.themes.BOOTSTRAP],
				meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}], suppress_callback_exceptions=True)

server = app.server


# Connect to app pages

from apps import home, itesm


# App Layout

app.layout = dbc.Container([

	dbc.NavbarSimple(
		[

        	dbc.Button('ITESM', href='/apps/itesm', color='light'),

		],
		brand='IMPLANG',
		brand_href='/apps/home'
	),

	html.Div(id='page-content', children=[]),
	dcc.Location(id='url', refresh=False)

])

# TODO: delete this is just a test
import os
import json
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
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
	Output(component_id='map_services_by_park', component_property='figure'),
	Input(component_id='select_service_by_park', component_property='value')
)
def generate_map_services(selected_park):
	''''
	Generates map of services by green area
	'''
	selected_park_data = df_denue_av_data[df_denue_av_data['av_union'] == float(selected_park)]
	# setting points of services
	fig = px.scatter_mapbox(
		selected_park_data,
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
			featureidkey="properties.UNION"
		)
	)
	# building the layout
	sector_k1_polygon.forEach()

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
						'features': [sector_k1_av['features'][1]]
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


@app.callback(Output(component_id='page-content', component_property=
					'children'),
			[Input(component_id='url', component_property='pathname')])
def display_page(pathname):
	if pathname == '/apps/itesm':
		return itesm.layout
	else:
		return home.layout


if __name__ == '__main__':
	app.run_server(debug=True)


