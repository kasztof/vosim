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

from datetime import datetime

# nowe
flask_app = flask.Flask(__name__)
app = dash.Dash(__name__, server=flask_app, url_base_pathname='/')
#

# 
# app = dash.Dash(__name__)
# app.title = 'VOSIM' 

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
PORT = os.environ.get('PORT')

def get_nodes():
    nodes = []
    with open('app/out.tsv') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            row = row[0].split()
            if row[0] not in nodes:
                nodes.append(row[0])
            if row[1] not in nodes:
                nodes.append(row[1])
    return nodes


def get_timestamps():
    timestamps = {}
    with open('app/out.tsv') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            row = row[0].split()
            if row[3] not in timestamps:
                timestamps[row[3]] = [(row[0], row[1])]
            else:
                timestamps[row[3]].append((row[0], row[1]))
    return timestamps


nodes_from_file = get_nodes()
num_of_nodes = len(nodes_from_file)

timestamps = get_timestamps()

nodes_array = []

nodes = [
    {
        'data': {'id': id, 'label': id},
        'position': {'x': 0, 'y': 0},
        'selectable': True
    }
    for id in (
        nodes_from_file
    )
]

for i in range(len(timestamps)):
    nodes_array.append(nodes)

edges_array = []
for key in timestamps:
    for source, target in timestamps[key]:
        edges_array.append({
            'data': {'source': source, 'target': target, 'id': key}
        })

edges_dict = {time.strftime("%Y-%m-%d %H", time.localtime(int(key))): [] for key in timestamps.keys()}

for key in timestamps:
    dt_object = time.localtime(int(key))
    period = time.strftime("%Y-%m-%d %H", dt_object)
    for source, target in timestamps[key]:
        edges_dict[period].append({
            'data': {'source': source, 'target': target}
        })

default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)'
        }
    },
]

marks = {}
i = 0
for key in edges_dict.keys():
    marks[i] = key
    i += 1

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='layout-dropdown',
            options=[
                {'label': 'Random', 'value': 'random'},
                {'label': 'Circle', 'value': 'circle'},
            ],
            searchable=False,
            clearable=False,
            value='circle',
            placeholder="Select network layout",
        ),
    ],
        style={'width': '20%', 'display': 'inline-block'}
    ),

    html.Div([
        cyto.Cytoscape(
            id='cytoscape-elements-callbacks',
            layout={'name': 'circle', 'animate': True},
            stylesheet=default_stylesheet,
            style={'width': '100%', 'height': '85vh'},
            elements=edges_array + nodes
        ),
        html.Pre(id='cytoscape-tapNodeData-json')
    ],
        style={'width': '80%', 'display': 'inline-block', 'float': 'right'}
    ),

    html.Div([
        dcc.Slider(
            id='my-slider',
            marks=marks,
            step=None,
            min=0,
            max=len(list(marks)) - 1
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


@app.callback(Output('cytoscape-elements-callbacks', 'elements'),
              [
                  Input('my-slider', 'value'),
              ],
              [State('cytoscape-elements-callbacks', 'elements')])
def update_elements(my_slider, elements):
    if my_slider is not None:
        return edges_array + nodes
    else:
        return edges_array + nodes


server = app.server

if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=PORT)
