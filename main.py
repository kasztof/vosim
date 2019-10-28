import os
import json
import flask
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from os.path import join, dirname
from dotenv import load_dotenv

from vosim.utils import get_network

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

flask_app = flask.Flask(__name__)
app = dash.Dash(__name__, server=flask_app, url_base_pathname='/', external_stylesheets=external_stylesheets)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
PORT = os.environ.get('PORT')

with open(PROJECT_ROOT + '/vosim/styles/style.json', 'r') as f:
    stylesheet = json.loads(f.read())

cyto.load_extra_layouts()

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='layout-dropdown',
            options=[
                {'label': 'Cose', 'value': 'cose'},
                {'label': 'Klay', 'value': 'klay'},
                {'label': 'Random', 'value': 'random'},
                {'label': 'Circle', 'value': 'circle'},
                {'label': 'Cola', 'value': 'cola'},
                {'label': 'Dagre', 'value': 'dagre'}
            ],
            searchable=False,
            clearable=False,
            value='cose',
            placeholder="Select network layout",
        ),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
            },
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ],
        style={'width': '20%', 'display': 'inline-block'}
    ),

    html.Div([
        cyto.Cytoscape(
            id='cytoscape-elements',
            style={'width': '100%', 'height': '85vh'},
            layout={
                'name': 'cose',
                'randomize': True,
            },
            elements = [],
            stylesheet=stylesheet,

        ),
    ],
        style={'width': '80%', 'display': 'inline-block', 'float': 'right'}
    ),

    html.Div([
        dcc.Slider(
            id='my-slider',
            step=1,
            min=0,
            max=10
        )
    ],
        style={'width': '90%', 'display': 'inline-block', 'margin-left': '5%'}
    ),
])


@app.callback(Output('cytoscape-elements', 'elements'),
              [Input('upload-data', 'contents')])
def update_output(content):
    if content is not None:
        return get_network(content)
    else:
        return []


@app.callback(
    Output('cytoscape-elements', 'layout'),
    [Input('layout-dropdown', 'value')]
)
def update_layout(dropdown_value):
    return {'name': dropdown_value, 'animate': True}


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=PORT)
