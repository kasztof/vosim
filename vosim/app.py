import os
import json
from os.path import join, dirname

import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from dotenv import load_dotenv

from influ.finder.model import independent_cascade
from vosim.utils import get_graph, get_network

from .server import app

DOTENV_PATH = join(dirname(__file__), '../.env')
load_dotenv(DOTENV_PATH)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
PORT = os.environ.get('PORT')

with open(PROJECT_ROOT + '/vosim/styles/style.json', 'r') as f:
    STYLESHEET = json.loads(f.read())

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
        html.Button('Start', id='start-button'),
        html.Pre(id='output-activated-nodes'),
        dcc.Store(id='data-file-content'),
        dcc.Store(id='data-activated-nodes'),
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
            elements=[],
            stylesheet=STYLESHEET,

        ),
    ],
        style={'width': '80%', 'display': 'inline-block', 'float': 'right'}
    ),

    html.Div([
        dcc.Slider(
            id='slider',
            step=1,
            min=0,
            max=10,
            marks={i: '{}'.format(i) for i in range(4)},
        )
    ],
        style={'width': '90%', 'display': 'inline-block', 'margin-left': '5%'}
    ),
])


@app.callback([Output('cytoscape-elements', 'elements'),
               Output('data-file-content', 'data')],
              [Input('upload-data', 'contents')])
def load_network(content):
    if content is not None:
        return get_network(content), content
    return [], None


@app.callback([Output('data-activated-nodes', 'data'),
               Output('slider', 'value'),
               Output('slider', 'max'),
               Output('slider', 'marks')],
              [Input('start-button', 'n_clicks'),
               Input('data-file-content', 'data')])
def load_activated_nodes(n_clicks, content):
    if not n_clicks == 0 and n_clicks is not None:
        graph = get_graph(content)
        result = independent_cascade(graph, [1, 2, 3], depth=5, threshold=0.1)

        slider_value = 0
        slider_max = len(result) - 1
        slider_marks = {i: '{}'.format(i) for i in range(len(result))}

        return result, slider_value, slider_max, slider_marks
    return None, 0, 0, {}


@app.callback(Output('cytoscape-elements', 'stylesheet'),
              [Input('slider', 'value'),
               Input('data-activated-nodes', 'data')])
def update_active_nodes(value, data):
    if value is not None:
        new_styles = [
            {
                'selector': '[label = ' + str(node_id) + ']',
                'style': {
                    'background-color': 'red'
                }
            } for node_id in data[value]
        ]
        return STYLESHEET + new_styles
    return STYLESHEET


@app.callback(Output('cytoscape-elements', 'layout'),
              [Input('layout-dropdown', 'value')])
def update_layout(dropdown_value):
    return {'name': dropdown_value, 'animate': True}
