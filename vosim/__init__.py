import csv
import os
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from os.path import join, dirname
from dotenv import load_dotenv

app = dash.Dash(__name__)

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')

def get_nodes():
    nodes = []
    with open(PROJECT_ROOT + '/vosim/out.tsv') as tsvfile:
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
    with open(PROJECT_ROOT + '/vosim/out.tsv') as tsvfile:
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
        'position': {'x': 0, 'y': 0}
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

edges_dict = {int(key):[] for key in timestamps.keys()}
for key in timestamps:
    for source, target in timestamps[key]:
        edges_dict[int(key)].append({
            'data': {'source': source, 'target': target}
        }) 


default_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#A3C4BC'
        }
    }
]

marks = {}
for key in timestamps.keys():
    marks[int(key)] = str(key)

app.layout = html.Div([

    dcc.Dropdown(
        id='layout-dropdown',
        options=[
            {'label': 'Random', 'value': 'random'},
            {'label': 'Circle', 'value': 'circle'},
        ],
        value='circle',
        placeholder="Select network layout",
    ),

    dcc.Slider(
        id='my-slider',
        marks=marks,
        step=None,
        min=list(marks)[0],
        max=list(marks)[len(marks)-1]
    ),

    cyto.Cytoscape(
        id='cytoscape-elements-callbacks',
        layout={'name': 'circle', 'animate': True},
        stylesheet=default_stylesheet,
        style={'width': '100%', 'height': '70vh'},
        elements=edges_array+nodes
    )
])

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
        return edges_dict[my_slider] + nodes
    else: 
        return edges_dict[list(edges_dict.keys())[0]]+ nodes


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
