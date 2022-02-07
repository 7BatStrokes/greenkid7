import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pathlib
from app import app
import dash_bootstrap_components as dbc
# colombian map dependencies
from functools import reduce
import mapcolombia
import plot_by_year
import pandas as pd
from urllib.request import urlopen
import requests
import math
import ssl
import json
#import dash_auth
from app import app

ssl._create_default_https_context = ssl._create_unverified_context

with urlopen('https://raw.githubusercontent.com/namonroyr/colombia_mapa/master/co_2018_MGN_DPTO_POLITICO.geojson') as response:
    colombia = json.load(response)

with urlopen('https://greenkid7.blob.core.windows.net/blobgreenkid7/base_target_final_190101_red.csv') as response:
    base_target = pd.read_csv(response)

####PLot by year
with urlopen('https://greenkid7.blob.core.windows.net/blobgreenkid7/tomas_pivot_red.csv') as response:
    base_pivot = pd.read_csv(response, sep = '|')

#Se filtran beneficiarios cuyo target de desnutrición para los próximos 6 meses sea 1
df_target1_mal = base_target[base_target['Marca_Target_EntroEnDesnutricion_F6M']==1]

#Se agrupan los target de malnutrition por dpto para obtener el count
dpts_count_target1_mal = df_target1_mal.groupby(['cod_dpto', 'nom_dpto']).size().to_frame('Count_Dpto_Malnutrition').reset_index()

#Se agrupan el count total de registros suministrados por dpto
dpts_count_total = base_target.groupby(['cod_dpto', 'nom_dpto']).size().to_frame('Count_Dpto_Total').reset_index()

#Se unen los 3 dfs creados anteriormente
data_frames = [dpts_count_total, dpts_count_target1_mal]
dpts_count = reduce(lambda  left,right: pd.merge(left,right,on=["cod_dpto", "nom_dpto"]), data_frames)

#Se crea una columna con el ratio entre count malnutrition y total por dept
dpts_count["Malnutrition_Percentage"] = dpts_count["Count_Dpto_Malnutrition"]/dpts_count["Count_Dpto_Total"]*100
#Casting y cambios de formato
dpts_count['cod_dpto']=pd.to_numeric(dpts_count['cod_dpto'])
dpts_count['cod_dpto']=dpts_count['cod_dpto'].astype(int).apply(lambda x: '{0:0>2}'.format(x))

fig_years_dist = plot_by_year.ploting_distribution(base_pivot)
figmap_mal = mapcolombia.getfigmap(dpts_count, 'Malnutrition_Percentage', 'peach', colombia)

header = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Desnutrición infantil en Colombia", className="font-weight-bold"), align="left")
                ],
                align="center"
            ),
        )
    ],
    color="white",
    light=True,
    className = 'nav-bar__fix'
)

card_map2 = dbc.Card(
    dbc.CardBody([
        html.H4("Porcentaje de Desnutrición por departamento"),
        html.Hr(id="hr_1"),
        html.Div(
            dcc.Graph(
                id='colombia_plot_2',
                figure=figmap_mal
            )
        )
    ])
,color="primary", outline=True)

card_graph_distribution = dbc.Card(
    dbc.CardBody([
        dbc.Card([
            dbc.CardBody([
                html.H4("Porcentaje de desnutrición por año", className="card-title"),
                html.Hr(id="hr_1"),
                dcc.Graph(
                    id='years_dist_plot',
                    figure=fig_years_dist
                )
            ])
        ],color="primary", outline=True)
    ])
,color="light", outline=True)

colombian_maps = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col(
                card_map2, width = 6
            )
        ])
    ])
],color="light", outline=True)


layout = dbc.Container([
    dbc.Row(dbc.Col(colombian_maps, width=12), className="mb-4",),
    dbc.Row([
        dbc.Col(
            card_graph_distribution, width=12
        )
      ])
], fluid=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        header,
        html.Div(id='page-content', children=layout, className='content')
    ], className='app-container__header__content')

], className='rooter_container')


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080) # To make it public on the Internet
    #app.run_server(debug=True, port=8080) # To test locally