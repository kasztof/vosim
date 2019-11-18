import os
import json
from os.path import join, dirname

import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from dotenv import load_dotenv

from .server import app
from .callbacks import register_callbacks
from .options import layout_options, model_options, konect_options, node_size_options, initial_nodes_method_options

DOTENV_PATH = join(dirname(__file__), '../.env')
load_dotenv(DOTENV_PATH)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')

with open(PROJECT_ROOT + '/vosim/assets/style.json', 'r') as f:
    STYLESHEET = json.loads(f.read())

cyto.load_extra_layouts()


app.layout = html.Div([
    html.Div([
        dbc.Tabs(
            id='navigation-tabs',
            children=[
                dbc.Tab(
                    label='Load network',
                    children=[
                        dbc.Button(
                            'Upload .csv file',
                            id='open-upload-modal',
                            color="primary",
                            block=True
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader('Select network from KONECT dataset'),
                                dbc.ModalBody([
                                    dcc.Upload(
                                        id='upload-data',
                                        children=[
                                            dbc.Button(
                                                'Upload .csv file',
                                                color="primary",
                                                block=True
                                            ),
                                        ],
                                        className='upload-panel',
                                        multiple=False
                                    ),
                                    html.Span(id='uploaded-file-name'),
                                    dcc.Checklist(
                                        id='is-directed-checkbox',
                                        options=[
                                            {'label': 'Directed', 'value': 'directed'},
                                        ],
                                    ) 
                                ]),
                                dbc.ModalFooter(
                                    [
                                        dbc.Button('Close', id='close-upload-modal', color='danger', outline=True),
                                        dbc.Button('Load', id='load-upload-network', color='primary')
                                    ]
                                ),
                            ],
                            id="computer-upload-modal",
                        ),

                        dbc.Button(
                            'Select from KONECT',
                            id='open-konect-modal',
                            color="primary",
                            block=True
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader('Select network from KONECT dataset'),
                                dbc.ModalBody(
                                    dcc.Dropdown(
                                        id='konect-networks-dropdown',
                                        options=konect_options,
                                        searchable=False,
                                        clearable=False,
                                        placeholder="Select KONECT network",
                                    ),
                                ),
                                dbc.ModalFooter(
                                    [
                                        dbc.Button('Close', id='close-konect-modal', color='danger', outline=True),
                                        dbc.Button('Load', id='load-konect-network', color='primary')
                                    ]
                                ),
                            ],
                            id="modal",
                        ),
                    ]
                ),
                
                dbc.Tab(
                    label='Simulation',
                    id='simulation-tab',
                    children=[
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=model_options,
                            searchable=False,
                            clearable=False,
                            placeholder="Select influence model",
                        ),

                        dcc.Input(
                            id='depth-limit',
                            placeholder='Depth',
                            type='number',
                            min=1,
                            step=1
                        ),

                        dcc.Input(
                            id='treshold',
                            placeholder='Treshold',
                            type='number',
                            min=0,
                            max=1,
                            step=0.05
                        ),

                        html.Div([
                            html.Label('Initial nodes'),
                            dcc.Dropdown(
                                id='initial-nodes-method-dropdown',
                                options=initial_nodes_method_options,
                                searchable=False,
                                clearable=False,
                            ),

                            dcc.Input(
                                id='initial-nodes-number',
                                type='number',
                                min=1,
                                step=1,
                                value=1,
                            ),
                        ]),

                        dbc.Button('Start', id='start-button', color='primary'),
                    ],
                    disabled=True,
                ),
                
                dbc.Tab(
                    label='Layout',
                    id='layout-tab',
                    children=[
                        html.Label('Network layout'),
                        dcc.Dropdown(
                            id='layout-dropdown',
                            options=layout_options,
                            searchable=False,
                            clearable=False,
                            value='cose',
                            placeholder='Select network layout',
                        ),
                        
                        html.Label('Node size'),
                        dcc.Dropdown(
                            id='node-size-dropdown',
                            options=node_size_options,
                            searchable=False,
                            clearable=False,
                            value='degree',
                        )
                    ],
                    disabled=True,
                )
            ]
        ),

        html.Div([
            html.A(
                'Download activations',
                id='download-link',
                download='rawdata.csv',
                target='_blank',
                className='btn btn-success btn-block disabled'
            ),

            html.Table(
                id='table-network-info',
                children=[],
            )
        ],
            id='network-info-panel'
        ),

        html.Pre(id='output-activated-nodes'),
        dcc.Store(id='graph-pickled'),
        dcc.Store(id='data-selected-nodes'),
        dcc.Loading(
            children=[
                dcc.Store(id='data-activated-nodes'),
            ],
            className='loading-box'
        ),
    ],
        className='left-panel'
    ),

    html.Div([
        dbc.Tabs(
            id='visualisation-tabs',
            children = [
                dbc.Tab(
                    label='Network',
                    children=[
                        cyto.Cytoscape( 
                            id='cytoscape-elements',
                            style={'width': '100%', 'height': '85vh'},
                            layout={
                                'name': 'cose',
                                'randomize': True,
                            },
                            elements=[],
                            stylesheet=STYLESHEET
                        ),

                        html.Div([
                            html.Span(
                                'Iteration:',
                                id='iterations-label'
                            ),
                            dcc.Slider(
                                id='slider',
                                step=1,
                                min=0,
                                max=10,
                                marks={i: '{}'.format(i) for i in range(4)},
                                updatemode='drag'
                            )
                        ],
                            className='bottom-slider'
                        ),
                    ]
                ),

                dbc.Tab(
                    label='Statistics',
                    id='statistics-tab',
                    children=[
                        dcc.Graph(
                            id='graph-degree-distribution',
                            figure={
                                'data': [],
                                'layout': {}
                            },
                        ),

                        html.Div(
                            id='div-table-graph-stats',
                            children=[
                                html.Table(
                                    id='table-graph-stats',
                                    children=[],
                                )
                            ]
                        ),

                        dcc.Graph(
                            id='activations-graph',
                            figure={
                                'data': [],
                                'layout': {
                                    'title':'Run simulation to generate this plot',
                                    'xaxis': {
                                        'title':'Iteration i',
                                        'tick0': 0,
                                        'dtick': 1,
                                    },
                                    'yaxis': {
                                        'title':'Number of activated nodes',
                                    },
                                }
                            }
                        )
                    ],
                    disabled=True,
                )
            ]
        )
    ],
        className='right-panel'
    ),
])

register_callbacks(app, STYLESHEET)
