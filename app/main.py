import csv
import os
import json
import time
import flask

import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from os.path import join, dirname
from dotenv import load_dotenv
import random
from influ import reader
cyto.load_extra_layouts()

flask_app = flask.Flask(__name__)
app = dash.Dash(__name__, server=flask_app, url_base_pathname='/')

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
PORT = os.environ.get('PORT')

graph = reader.read_graph(PROJECT_ROOT + '/datasets/extracted/david_copperfield/david_copperfield.csv', 'events')

num_of_nodes = len(graph.vs.indices)

nodes = [
    {
        'data': {
            'id': id,
            'label': id,
        },
    }
    for id in (
        graph.vs.indices
    )
]

edges_array = []
for e in graph.es:
    edges_array.append({
        'data': {
            'source': e.tuple[0],
            'target': e.tuple[1],
        }
    })
        
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='layout-dropdown',
            options=[
                {'label': 'Klay', 'value': 'klay'},
                {'label': 'Random', 'value': 'random'},
                {'label': 'Circle', 'value': 'circle'},
                {'label': 'Cola', 'value': 'cola'},
                {'label': 'Dagre', 'value': 'dagre'}
            ],
            searchable=False,
            clearable=False,
            value='klay',
            placeholder="Select network layout",
        ),
    ],
        style={'width': '20%', 'display': 'inline-block'}
    ),

    html.Div([
        cyto.Cytoscape(
            id='cytoscape-elements-callbacks',
            style={'width': '100%', 'height': '85vh'},
            layout={
                'name': 'klay',
            },
            elements=edges_array + nodes
        ),
        html.Pre(id='cytoscape-tapNodeData-json')
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


@app.callback(
    Output('cytoscape-tapNodeData-json', 'children'),
    [Input('cytoscape-elements-callbacks', 'tapNodeData')]
)
def displayTapNodeData(data):
    return json.dumps(data, indent=2)


@app.callback(
    Output('cytoscape-elements-callbacks', 'layout'),
    [Input('layout-dropdown', 'value')]
)
def update_layout(dropdown_value):
    return {'name': dropdown_value, 'animate': True}


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=PORT)
