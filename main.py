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
import numpy as np
import PredictMini
import dash_bootstrap_components as dbc
# colombian map dependencies
from functools import reduce
import mapcolombia
import plot_by_year
import pandas as pd
from urllib.request import urlopen
import requests
import joblib
import pathlib
import math
import ssl
import json
#import dash_auth
from app import app

ssl._create_default_https_context = ssl._create_unverified_context

with urlopen('https://greenkid7.blob.core.windows.net/blobgreenkid7/Modelo_malnutrition_subset.sav') as response:
    Modelo_malnutrition_subset = joblib.load(response)


# List of child care categories
child_care_opt = ["Asiste a un lugar comunitario, jardín de infantes, centro de desarrollo infantil o escuela.",
"Con sus padres en casa", "Con sus padres en el trabajo", "Con mucama o niñera en casa",
"Al cuidado de un familiar mayor de 18 años", "Al cuidado de un familiar menor de 18 años",
"Solo en casa","No aplica por flujo"]

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
        html.H4("Porcentaje de Desnutrición por Departamento"),
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
        html.H4("Porcentaje de Desnutrición por Año", className="card-title"),
        html.Div(
            dcc.Graph(
                id='years_dist_plot',
                figure=fig_years_dist
            )
        )
    ])
,color="primary", outline=True)

colombian_maps = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col(
                card_map2, width = 5
            ),
            dbc.Col(
                card_graph_distribution, width = 7
            )
        ])
    ])
],color="light", outline=True)


# Dropdown to select the model
drop_model = dbc.FormGroup(
    [
        #html.
        dbc.Label("Model", html_for="model", className="label_selector", width=3),
        dbc.Col([
            dcc.Dropdown(
                id="model",
                options=[{'value': 0, 'label': "Desnutrición"}],
                value=0,
                #className="container-fluid"
            ),
        ], width=9, align="center"),#className="lg-auto",),
    ],
    row=True,
    #inline=True,
    className="ml-0 mr-0",
)


# Dropdown child-care
drop_child_care = dbc.FormGroup(
    [
        #html.
        dbc.Label("Tipo de cuidado del niño", html_for="ch_care", className="label_selector", width=3),
        dbc.Col([
            dcc.Dropdown(
                id="ch_care",
                options=[{'value': i+1, 'label': care_opt} for i, care_opt in enumerate(child_care_opt)],
                value=1,
                #className="container-fluid"
            ),
        ], width=9, align="center"),#className="lg-auto",),
    ],
    row=True,
    #inline=True,
    className="ml-0 mr-0",
)


#style={"font-size":"0.8125rem","font-weight":"bold"}
step = 1
slider_min_z = dbc.FormGroup(
    [
        dbc.Label("Mín. Z-score peso-altura:", html_for="slider-min-z",
             width=4, className="label_selector" , align="center"),
        dbc.Col(
            dcc.Slider(
                id='slider-min-z',
                min=-3,
                max=3,
                step=0.01,
                marks={int(i) : str(i) for i in np.linspace(-3.0,3.0,num=int((6/step)+1))},
                value=0,
                tooltip= {"always_visible":True,"placement":"top"},
                #className="pt-0"
            ),
            width=8, align="center"
        ),
    ],
    row=True, className="mb-0 ml-0 mr-0",
)

slider_max_z = dbc.FormGroup(
    [
        dbc.Label("Máx. Z-score peso-altura:", html_for="slider-max-z",
             width=12, className="label_selector" , align="center"),
        dbc.Col(
            dcc.Slider(
                id='slider-max-z',
                min=-3,
                max=3,
                step=0.01,
                marks={int(i) : str(i) for i in np.linspace(-3.0,3.0,num=int((6/1)+1))},
                value=0,
                tooltip= {"always_visible":True,"placement":"top"},
            ),
            width=12, align="center"
        ),
    ], className="mb-0",
    #row=True,
)

slider_avg_z = dbc.FormGroup(
    [
        dbc.Label("Promedio Z-score peso-altura:", html_for="slider-avg-z",
             width=12, className="label_selector" , align="center"),
        dbc.Col(
            dcc.Slider(
                id='slider-avg-z',
                min=-3,
                max=3,
                step=0.01,
                marks={int(i) : str(i) for i in np.linspace(-3.0,3.0,num=int((6/1)+1))},
                value=0,
                tooltip= {"always_visible":True,"placement":"top"},
            ),
            width=12, align="center"
        ),
    ], className="mb-0",
    #row=True,
)


slider_under = dbc.FormGroup(
    [
        dbc.Label("No. de veces en desnutrición:", html_for="slider-under",
             width=12, className="label_selector" , align="center"),
        dbc.Col(
            dcc.Slider(
                id='slider-under',
                min=0,
                max=12,
                step=1,
                marks={int(i) : str(i) for i in range(13)},
                value=0,
                #tooltip= {"always_visible":True,"placement":"top"},
            ),
            width=12, align="center"
        ),
    ],
    #row=True,
)

slider_over = dbc.FormGroup(
    [
        dbc.Label("No. de veces en sobrepeso:", html_for="slider-over",
             width=12, className="label_selector" , align="center"),
        dbc.Col(
            dcc.Slider(
                id='slider-over',
                min=0,
                max=12,
                step=1,
                marks={int(i) : str(i) for i in range(13)},
                value=0,
                #tooltip= {"always_visible":True,"placement":"top"},
            ),
            width=12, align="center"
        ),
    ],
    #row=True,
)


switches = dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Toggle a bunch", html_for="switches",
                        hidden=True, width=12, align="center"),
                    dbc.Checklist(
                        options=[
                            {"label": "Discapacidad", "value": 1},
                            {"label": "Alfabetizado", "value": 2},
                            {"label": "Estudia", "value": 3},
                            {"label": "Recibe Comida", "value": 4},
                        ],
                        value=[1],
                        id="switches",
                        switch=True,
                        #inline=True,
                        #labelClassName="label_selector",
                        labelCheckedClassName="label_selector",
                        #style={"display": "flex", "justify-content": "space-evenly"},
                        className="just_even_2",
                    ),
                ],),  #row=True
            ], width=12, )#style={"display": "flex", "justify-content": "space-evenly"},),
        ], form=True, align="start", className="mb-0 pt-0",)


# Section where the user type the variables' values
selectors = html.Div([
                html.H5("Selecione todos los parámetros que apliquen", className="card-title"),
                drop_model,
                #dbc.Row([
                    #dbc.Col([
                        #dbc.Form([           
                            drop_child_care,
                        #],),#inline=True),
                    #]),
                #]),
                slider_min_z,
                dbc.Row(
                [
                    dbc.Col(
                        slider_max_z,
                     width=6,),
                     dbc.Col(
                        slider_avg_z,
                     width=6,),
                ],
                form=True, align="start", className="mb-0 pt-0",
                ),

                dbc.Row(
                [
                    dbc.Col(
                        slider_under,
                     width=6,),
                     dbc.Col(
                        slider_over,
                     width=6,),
                ],
                form=True, align="start", className="mb-0",
                ),
])




exp_prob = dcc.Markdown('''
---
>
> ¿Cómo interpretar la probabilidad?.
> 
''')  


# Middle-section of the page - Predictor
prediction_cards = dbc.Card(
            dbc.CardBody(
                [
                html.H1('Herramienta de predicción para niños individuales',className="card-title"),
                dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        selectors,
                                        #dbc.Row(
                                            #[
                                                #dbc.Col([
                                                    switches,
                                                #], width=12),
                                            #]),#, justify="center"),

                                    ]
                                ), color="primary", outline=True
                            ),
                        ], width=8),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        
                                        html.H5("Instrucciones", className="card-title"),
                                        #html.P(description_short_SHAP,className="text-justify"),
                                        dbc.Alert(html.P(("Predicción de la probabilidad de que un niño sufra desnutrición "
                                        "durante los próximos 6 meses. Por favor modifique los parámetros de la izquierda y luego presione ",
                                        html.Em("\"Ejecutar Predictor\""), " para obtener la predicción."),className="text-justify"), color="success"),
                                        #html.P(
                                            #"This card has some text content.",
                                            #className="card-text",
                                        #),
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button(
                                                    id="button_pred", children="Run predictor", n_clicks=0,
                                                    color="warning", className="mt-auto"
                                                ),
                                            ], className="just_center"), #style={"display": "flex","justify-content": "center"}),
                                        ],),


                                        exp_prob,
                                        html.Div([
                                            html.Ul([
                                                html.Li([html.Span("Riesgo Bajo: ", style={"color": "#1fbd38"}),
                                                "El niño actualmente tiene bajo riesgo de padecer esta enfermedad."]),
                                                html.Li([html.Span("Riesgo Leve: ", style={"color": "#fff000"}),
                                                "El niño tiene un riesgo leve de padecer esta enfermedad."]),
                                                html.Li([html.Span("Riesgo Latente: ", style={"color": "#f86e02"}),
                                                "El niño tiene riesgo latente de sufrir esta enfermedad."]),
                                                html.Li([html.Span("Alto Riesgo: ", style={"color": "#f30404"}),
                                                "El niño debe ser priorizado."]),
                                            ]),
                                        ]),
                                        dbc.Progress(id="prog-bar", value="", color="",
                                            striped=True, animated=True, 
                                            className="mb-3 mt-4" , style={"height": "30px"}),
                                    ]
                                ), color="primary", outline=True
                            ),
                        ],width=4),
                    ],)
                ])
            )
text_short_SHAP_1 = ("What you see on the left side is a waterfall plot to visualize "
"SHAP values for each model feature. Feature values in", html.Span(" pink ", className="pink_bold"),
"cause an increase in the "
"final prediction (malnutrition/relapse probability). In contrast, feature "
"values in" , html.Span(" blue ", className="blue_bold"), "cause a decrease in the final prediction. Size of the bar shows the "
"magnitude of the feature's effect. A larger bar means that the corresponding feature "
"has larger impact. The sum of all feature SHAP values explains why model prediction "
"was different from the baseline.")


#f"Model predicted {prob:.3f}
text_short_SHAP_2 = ("Model predicted a probability of ",
html.Span(children=[],id="prob-span", className="pink_bold"),
" of suffering ", html.Span(children=[],id="model-span", className="pink_bold"),
", whereas the base_value is 0.5. ", html.P(id="msg-least",children=[]), html.P(id="msg-great",children=[]))

description_short_SHAP = dbc.Alert(
            [   
                html.P(text_short_SHAP_1),
                html.P(text_short_SHAP_2),
                #html.A("example link", href="#", className="alert-link"),
                #html.B(red, style:"red")
            ],
            color="dark", className="text-justify p-4",
        )



# Bottom-section of the page - SHAP values visualization and their interpretation  
Shap_cards = dbc.Card(
                dbc.CardBody(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                        html.H3("SHAP values summary", className="card-title text-center"),
                                        #html.Img(src=img, height="275px"),
                                ),
                                dbc.CardImg(id="shap_img", bottom=True), #, src=""
                                #html.Img(id="shap_img",src=""),
                            ], color="primary", outline=True),
                        ],width=8),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H3("Interpretation of the SHAP values", className="card-title"),
                                        #html.P(description_short_SHAP,className="text-justify"),
                                        description_short_SHAP,
                                    ]
                                ), color="primary", outline=True, 
                            ),
                        ],width=4),
                    ]),
                ],
            )
        )

layout = dbc.Container([
    dbc.Row(dbc.Col(colombian_maps, width=12), className="mb-4",),
    dbc.Row(dbc.Col(prediction_cards, width=12), className="mb-4",),
], fluid=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        header,
        html.Div(id='page-content', children=layout, className='content')
    ], className='app-container__header__content')

], className='rooter_container')


@app.callback(
    [Output(component_id = "shap_img", component_property = "src"),
    Output(component_id = "prob-span", component_property = "children"),
    Output(component_id = "model-span", component_property = "children"),
    Output(component_id = "prog-bar", component_property = "children"),
    Output(component_id = "prog-bar", component_property = "value"),
    Output(component_id = "prog-bar", component_property = "color"),
    Output(component_id = "msg-least", component_property = "children"),
    Output(component_id = "msg-great", component_property = "children"),
    ],
    [Input(component_id = "button_pred", component_property = "n_clicks"),
    ],
    [State(component_id = "model", component_property = "value"),
    State(component_id = "ch_care", component_property = "value"),
    State(component_id = "slider-min-z", component_property = "value"),
    State(component_id = "slider-max-z", component_property = "value"),
    State(component_id = "slider-avg-z", component_property = "value"),
    State(component_id = "slider-under", component_property = "value"),
    State(component_id = "slider-over", component_property = "value"),
    State(component_id = "switches", component_property = "value"),
    ]
)
def on_button_click(n, model_val, care, min_z, max_z, avg_z, under, over, switch_list):
    """
    print(f"button-n_clicks are: {n}, and type: {type(n)}")
    print(f"value model is: {model_val}, and type: {type(model_val)}")
    print(f"value care is: {care}, and type: {type(care)}")
    print(f"value min_z is: {min_z}, and type: {type(min_z)}")
    print(f"value max_z is: {max_z}, and type: {type(max_z)}")
    print(f"value avg_z is: {avg_z}, and type: {type(avg_z)}")
    print(f"value under is: {under}, and type: {type(under)}")
    print(f"value over is: {over}, and type: {type(over)}")
    print(f"value switch_list is: {switch_list}, and type: {type(switch_list)}")
    """
    # Trigger: each time the user gives a click
    if n >= 0:
        # Building the feature vector
        valores = {"AVG_ZScorePesoTalla_12M": avg_z, #[-3,3] --> Slider float
           "MAX_ZScorePesoTalla_12M": max_z, #[-3,3] --> Slider float
           "Veces_DesnutricionSM_12M": under, # 0 en adelante --> Slider enteros positivos
           "Veces_SobrePeso_12M": over, # 0 en adelante --> Slider enteros positivos
           "MIN_ZScorePesoTalla_12M": min_z, # [-3,3] --> Slider float
           } 

        valores["tip_cuidado_niños"] = 9 if care == 8 else care
        valores["ind_discap"] =        "si" if 1 in switches else "ninguna"
        valores["ind_leer_escribir"] =  1 if 2 in switches else 2
        valores["ind_estudia"] =        1 if 3 in switches else 2
        valores["ind_recibe_comida"] =  1 if 4 in switches else 2

        # Turning the feature dict in a pd.dataframe
        base_variables = PredictMini.convertirDicEnBase(valores)

        img, shap_values = PredictMini.plotShapValues(Modelo_malnutrition_subset,base_variables)
        str_modelo =  "malnutrition"
        ranges = [0.34, 0.46, 0.59]
        print("Malnutrition")
        
        # Prob. predicted for the model
        shap_vals = shap_values[1][0]
        prob = 0.5 + shap_vals.sum()

        # Bar color selection
        if prob <= ranges[0]:
            color_bar = "#1fbd38" #alt. success
        elif prob <= ranges[1]:
            color_bar = "#fff000" #alt. warning
        elif prob <= ranges[2]:
            color_bar = "#f86e02"
        elif prob <= 1:
            color_bar = "#f30404" #alt. danger
        
        # print(type(shap_values[1][0]))
        
        
        var_least, var_great = PredictMini.greatest_least(shap_vals)

        msg_least = ""
        msg_great = ""

        if var_least != "":
            msg_least = ("The variable ", html.Span(var_least,className="blue_bold"), " was the one with ",
            "the greatest effect in ", html.Span("reducing", className="blue_bold"), " the risk of suffering ",
            html.Span(str_modelo, className="pink_bold"), ". ")


        if var_great != "":
            msg_great = ("The variable ", html.Span(var_great, className="pink_bold"), " was the one with ",
            "the greatest effect in ", html.Span("increasing", className="pink_bold"), " the risk of suffering ",
            html.Span(str_modelo, className="pink_bold"), ".")


        return (img, f"{prob:.3f}", str_modelo, f"{prob*100:.0f}%", f"{prob*100:.0f}", color_bar, msg_least, msg_great)






if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080) 