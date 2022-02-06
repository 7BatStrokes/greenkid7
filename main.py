import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
#import dash_auth
from app import app

# Connect to app pages
header = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Desnutrición infantil en Colombia", className="font-weight-bold"), align="left")
                ],
                align="center"
            ),
        ),
    ],
    color="white",
    light=True,
    className = 'nav-bar__fix'
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        header,
        html.Div(id='page-content', children=[], className='content')
    ], className='app-container__header__content')

], className='rooter_container')


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080) # To make it public on the Internet
    #app.run_server(debug=True, port=8080) # To test locally
