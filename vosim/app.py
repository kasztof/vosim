import os
import json
from os.path import join, dirname

import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc

from dotenv import load_dotenv

from .server import app
from .callbacks import register_callbacks

DOTENV_PATH = join(dirname(__file__), '../.env')
load_dotenv(DOTENV_PATH)

PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
PORT = os.environ.get('PORT')

with open(PROJECT_ROOT + '/vosim/assets/style.json', 'r') as f:
    STYLESHEET = json.loads(f.read())

cyto.load_extra_layouts()

app.layout = html.Div([
    html.Div([
        dcc.Tabs(
            id='navigation-tabs',
            children=[
                dcc.Tab(
                    label='Network',
                    children=[
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.A('Select File')
                            ]),
                            className='upload-panel',
                            multiple=False
                        ),
                    ]
                ),
                
                dcc.Tab(
                    label='Simulation',
                    children=[
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
                            placeholder='Select network layout',
                        ),

                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[
                                {'label': 'Linear Treshold', 'value': 'lintres'},
                                {'label': 'Independent Cascade', 'value': 'indcas'}
                            ],
                            searchable=False,
                            clearable=False,
                            value='indcas',
                            placeholder="Select influence model",
                        ),

                        dcc.Input(
                            id='depth-limit',
                            placeholder='Enter depth limit',
                            type='number'
                        ),

                        dcc.Input(
                            id='treshold',
                            placeholder='Enter treshold',
                            type='number',
                            min=0,
                            max=1,
                            step=0.05
                        ),

                        html.Button('Start', id='start-button'),
                    ]
                ),
                
                dcc.Tab(
                    label='Summary',
                    children=[]
                )
            ]
        ),

        html.Pre(id='output-activated-nodes'),
        dcc.Store(id='data-file-content'),
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
        className='network'
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
        className='bottom-slider'
    ),
])

register_callbacks(app, STYLESHEET)
