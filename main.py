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

from vosim.influ.finder.model import independent_cascade
from vosim.utils import get_graph, get_network

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
def update_output(content):
    if content is not None:
        return get_network(content), content
    else:
        return [], None


@app.callback(Output('cytoscape-elements', 'layout'),
              [Input('layout-dropdown', 'value')])
def update_layout(dropdown_value):
    return {'name': dropdown_value, 'animate': True}


@app.callback(Output('cytoscape-elements', 'stylesheet'),
              [Input('my-slider', 'value'),
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
        return stylesheet + new_styles
    else:
        return stylesheet


@app.callback(Output('data-activated-nodes', 'data'),
              [Input('start-button', 'n_clicks'),
               Input('data-file-content', 'data')])
def load_activated_nodes(n_clicks, content):
    if not n_clicks == 0 and n_clicks is not None:
        graph = get_graph(content)
        result = independent_cascade(graph, [1, 2, 3], depth=5, threshold=0.1)
        return result


if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=PORT)
