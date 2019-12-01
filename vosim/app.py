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

app.title = 'Vosim'
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
                        html.Label('Influence model'),
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=model_options,
                            searchable=False,
                            clearable=False,
                            placeholder='Select influence model',
                            value='indcas'
                        ),

                        html.Label('Iterations limit'),
                        dcc.Input(
                            id='depth-limit',
                            placeholder='Depth',
                            type='number',
                            min=1,
                            step=1,
                            value=1,
                        ),

                        html.Label('Treshold'),
                        dcc.Input(
                            id='treshold',
                            placeholder='Treshold',
                            type='number',
                            min=0,
                            max=1,
                            step=0.05,
                        ),

                        html.Div([
                            html.Label('Initial nodes selection method'),

                            html.Div(
                                id='init-node-selection-container',
                                children=[
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
                                ]
                            )
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
        ),
        dbc.Button(
            'User manual',
            color='info',
            className='mr-1',
            id='info-button'
        ),
        dbc.Modal(
            [
                dbc.ModalHeader('How to use this application?'),
                dbc.ModalBody([
                    html.H3('Loading network'),
                    html.P('You have two options of loading a network:'),
                    html.Ul([
                        html.Li('Upload .csv file from your computer - file can have either commas or spaces as separators. The file should contain edges in the following format:'),
                        html.Pre('source, target, [attributes]'),
                        html.Li('Select network directly from KONECT datasets - currently 3 datasets are available.')
                    ]),

                    html.H3('Changing network layout'),
                    html.P('You can select one of the network layouts under "Layout" tab. You can also change the node size metric. By default, node size on the graph depends on node degree.'),

                    html.H3('Running social influence models'),
                    html.P('In "Simulation" tab you can select one of the currently available social influence models and set its properties values as well as set the maximum number of model iterations. You can also select one of the methods of selecting initial nodes. If you decide to use the "Manual" method, please select the nodes by clicking on them while holding Ctrl key.'),

                    html.H3('Downloading results'),
                    html.P('After the simulation is done, you will be able to download the results by clicking "Download activations" on the left side bottom panel. In nth row, the file contains all nodes activated in nth iteration.'),
                
                    html.H3('Network statistics'),
                    html.P('In "Statistics" tab, you can see some informations regarding the currently loaded network such as degree distribution plot, general network metrics or plot of the activated nodes number in iterations for different initial nodes selection methods (This plot contains results of single model run, using given initial nodes selection method. The values here are not related to the simulation results in "Network" tab).')
                ]),
                dbc.ModalFooter(
                    dbc.Button('Close', id='close-info-button', className='ml-auto')
                ),
            ],
            id='info-modal',
            size='lg'
        ),
    ],
        className='right-panel'
    ),
])

register_callbacks(app, STYLESHEET)
