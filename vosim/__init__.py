import csv
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)


def get_nodes():
    nodes = []
    with open('out.tsv') as tsvfile:
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
    with open('out.tsv') as tsvfile:
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
        'data': {'id': id},
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
            'data': {'source': source, 'target': target}
        })

nodes = [
    {
        'data': {'id': id},
        'position': {'x': 0, 'y': 0}
    }
    for id in (
        nodes_from_file
    )
]


edges = [
    {'data': {'source': source, 'target': target}}
    for source, target in (
        (1, 2),
        (4, 5)
    )
]


nodes2 = [
    {
        'data': {'id': id},
        'position': {'x': 0, 'y': 0}
    }
    for id in (
        1, 2, 3, 4
    )
]

edges2 = [
    {'data': {'source': source, 'target': target}}
    for source, target in (
        (2, 3),
        (1, 2),
    )
]

all_nodes = [nodes, nodes2]
all_edges = [edges, edges2]

print(nodes)
print(edges_array + nodes)

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


app.layout = html.Div([
    html.Div([
        html.Button('Add Node', id='btn-add-node', n_clicks_timestamp=0),
        html.Button('Remove Node', id='btn-remove-node', n_clicks_timestamp=0)
    ]),

    dcc.Slider(
        id='my-slider',
        min=1,
        max=len(timestamps),
        step=1,
        value=1,
    ),

    cyto.Cytoscape(
        id='cytoscape-elements-callbacks',
        layout={'name': 'random', 'animate': True},
        stylesheet=default_stylesheet,
        style={'width': '100%', 'height': '450px'},
        elements=edges_array+nodes
    )
])


@app.callback(Output('cytoscape-elements-callbacks', 'elements'),
              [Input('btn-add-node', 'n_clicks_timestamp'),
               Input('btn-remove-node', 'n_clicks_timestamp'),
               Input('my-slider', 'value'),
               ],
              [State('cytoscape-elements-callbacks', 'elements')])
def update_elements(btn_add, btn_remove, my_slider, elements):
    # If the add button was clicked most recently
    # if int(btn_add) > int(btn_remove):
    #     next_node_idx = len(elements) - len(edges)

    #     # As long as we have not reached the max number of nodes, we add them
    #     # to the cytoscape elements
    #     if next_node_idx < len(nodes):
    #         return edges2 + nodes2

    # # If the remove button was clicked most recently
    # elif int(btn_remove) > int(btn_add):
    #     if len(elements) > len(edges):
    #         return elements[:-1]

    # Neither have been clicked yet (or fallback condition)
    return all_edges[my_slider-1] + all_nodes[my_slider-1]


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
