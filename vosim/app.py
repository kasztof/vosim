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
PORT = os.environ.get('PORT')

with open(PROJECT_ROOT + '/vosim/assets/style.json', 'r') as f:
    STYLESHEET = json.loads(f.read())

cyto.load_extra_layouts()

app.layout = html.Div([
    html.Div([
        dbc.Tabs(
            id='navigation-tabs',
            children=[
                dbc.Tab(
                    label='Network',
                    children=[
                        html.H3('Load network'),

                        dcc.Upload(
                            id='upload-data',
                            children=[
                                dbc.Button(
                                    'Upload from computer',
                                    color="primary",
                                    block=True
                                ),
                            ],
                            className='upload-panel',
                            multiple=False
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
                    children=[
                        dcc.Dropdown(
                            id='layout-dropdown',
                            options=layout_options,
                            searchable=False,
                            clearable=False,
                            value='cose',
                            placeholder='Select network layout',
                        ),

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
                    ]
                ),
                
                dbc.Tab(
                    label='Layout',
                    children=[
                        dcc.Dropdown(
                            id='node-size-dropdown',
                            options=node_size_options,
                            searchable=False,
                            clearable=False,
                            value='degree',
                        )
                    ]
                )
            ]
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
                    ]
                ),

                dbc.Tab(
                    label='Statistics'
                )
            ]
        )
    ],
        className='right-panel'
    ),

    html.Div([
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
])

register_callbacks(app, STYLESHEET)
