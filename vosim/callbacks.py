from dash.dependencies import Input, Output, State, ClientsideFunction
from vosim.utils import get_network_from_graph, get_degree_distribution_data, get_graph_statistics, get_network_info
import dash_html_components as html

from .options import initial_nodes_method_options
from .middleware import get_konect_network, get_graph, get_init_nodes, get_model_result, get_methods_activated_nodes_data

import urllib.parse
import io
import csv
import pickle

def register_callbacks(app, stylesheet):
    @app.callback([Output('cytoscape-elements', 'elements'),
                   Output('graph-pickled', 'data'),
                   Output('graph-degree-distribution', 'figure'),
                   Output('table-graph-stats', 'children'),
                   Output('layout-tab', 'disabled'),
                   Output('simulation-tab', 'disabled'),
                   Output('statistics-tab', 'disabled'),
                   Output('table-network-info', 'children')],
                  [Input('load-upload-network', 'n_clicks'),
                   Input('load-konect-network', 'n_clicks')],
                  [State('upload-data', 'contents'),
                   State('konect-networks-dropdown', 'value'),
                   State('is-directed-checkbox', 'value'),
                   State('upload-data', 'filename')])
    def load_network(load_data_button, n_clicks, upload_content, konect_network_name, is_directed, upload_network_name):
        graph = None
        network_name = ''

        if upload_content is not None and load_data_button !=0 and load_data_button is not None: # if load from csv button was clicked
            directed = True if is_directed is not None else False
            graph = get_graph(upload_content, directed=directed)
            network_name = upload_network_name
        elif n_clicks != 0 and n_clicks is not None and konect_network_name is not None: # if load from konect was clicked
            graph, network_name = get_konect_network(konect_network_name)


        if graph is not None:
            
            degrees_histogram_data = get_degree_distribution_data(graph)
            graph_stats = get_graph_statistics(graph)
            network_info = get_network_info(network_name, graph)

            degree_hist_figure = {
                'data': [
                    {
                        'type': 'scatter',
                        'mode': 'markers',
                        'y': list(degrees_histogram_data.values()),
                        'x': list(degrees_histogram_data.keys()),
                    }
                ],
                'layout': {
                    'title':'Degree distribution',
                    'showlegend': False,
                    'xaxis': {
                        'title':'Degree (d)',
                        'tick0': 0,
                        'dtick': 1,
                    },
                    'yaxis': {
                        'title': 'Frequency',
                        'tick0': 0,
                        'dtick': 1,
                    },
                }
            }

            table_graph_stats = [html.Tr([
                html.Td(stat), html.Td(graph_stats[stat])
            ]) for stat in graph_stats]

            table_network_info = [html.Tr([
                html.Td(stat), html.Td(network_info[stat])
            ]) for stat in network_info]

            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode(), degree_hist_figure, table_graph_stats, False, False, False, table_network_info
        else:
            return [], None, [], [], True, True, True, ''
    
    @app.callback([Output('data-activated-nodes', 'data'),
                   Output('slider', 'value'),
                   Output('slider', 'max'),
                   Output('slider', 'marks'),
                   Output('download-link', 'className')],
                  [Input('start-button', 'n_clicks_timestamp'),
                   Input('load-upload-network', 'n_clicks_timestamp'),
                   Input('load-konect-network', 'n_clicks_timestamp')],
                  [State('graph-pickled', 'data'),
                   State('depth-limit', 'value'),
                   State('treshold', 'value'),
                   State('model-dropdown', 'value'),
                   State('data-selected-nodes', 'data'),
                   State('initial-nodes-method-dropdown','value'),
                   State('initial-nodes-number', 'value'),
                   State('download-link', 'className')])
    def load_activated_nodes(start_button_timestamp, load_csv_timestamp, load_konect_timestamp, graph_pickled, depth, treshold, model, initial_nodes, init_nodes_method, init_nodes_num, download_link_class):
        start_button_timestamp = 0 if start_button_timestamp is None else start_button_timestamp
        load_csv_timestamp = 0 if load_csv_timestamp is None else load_csv_timestamp
        load_konect_timestamp = 0 if load_konect_timestamp is None else load_konect_timestamp

        clicked = ''

        if start_button_timestamp > load_csv_timestamp and start_button_timestamp > load_konect_timestamp:
            clicked = 'start_button'
        elif load_csv_timestamp > start_button_timestamp and load_csv_timestamp > load_konect_timestamp:
            clicked = 'load_csv'
        elif load_konect_timestamp > start_button_timestamp and load_konect_timestamp > load_csv_timestamp:
            clicked = 'load_konect'

        if clicked == 'start_button' and graph_pickled is not None:
            graph = pickle.loads((graph_pickled.encode()))

            if init_nodes_method == 'manual':
                new_initial = []
                for node in initial_nodes:
                    new_initial.append(node-1)
                init_nodes = new_initial
            else:
                init_nodes = get_init_nodes(graph, init_nodes_method, init_nodes_num)

            result = get_model_result(graph, model, init_nodes, depth, treshold)
    
            slider_value = 0
            slider_max = len(result) - 1
            slider_marks = {i: '{}'.format(i) for i in range(len(result))}

            return result, slider_value, slider_max, slider_marks, download_link_class.rsplit(' ', 1)[0]
        elif clicked == 'load_csv' or clicked == 'load_konect':
            return None, 0, 0, {}, 'btn btn-success btn-block disabled'
        else:
            return None, 0, 0, {}, download_link_class
    
    @app.callback(Output('initial-nodes-number', 'disabled'),
                  [Input('initial-nodes-method-dropdown', 'value')])
    def toggle_init_nodes_input(init_nodes_method):
        init_nodes_num_disabled = True if init_nodes_method == 'manual' else False
        return init_nodes_num_disabled


    @app.callback(Output('cytoscape-elements', 'stylesheet'),
                  [Input('slider', 'value'),
                   Input('data-activated-nodes', 'data'),
                   Input('node-size-dropdown', 'value')],
                  [State('graph-pickled', 'data')])
    def update_active_nodes(slider_value, data, node_size_metric, graph_pickled):
        if slider_value is not None and data is not None:
            activated_nodes = [
                {
                    'selector': '[id_vosim = ' + str(node_id + 1) + ']',
                    'style': {
                        'background-color': 'red'
                    }
                } for node_id in data[slider_value]
            ]

            newly_activated_nodes = set(data[slider_value]) - set(data[slider_value - 1]) if slider_value != 0 else []

            newly_activated_styles = [
                {
                    'selector': '[id_vosim = ' + str(node_id + 1) + ']',
                    'style': {
                        'border-width': '1px',
                        'border-color': 'green'
                    }
                } for node_id in newly_activated_nodes
            ]

            rule = "mapData(" + node_size_metric + ", 1, 50, 2, 15)" if node_size_metric != 'clustering_coeff' \
                else "mapData(" + node_size_metric + ", 0, 1, 2, 10)"
            node_size_metric_style = [
                {
                    "selector": "node",
                    "style": {
                        "width": rule,
                        "height": rule,
                        "font-size": "6px",
                    }
                }
            ]

            if graph_pickled is not None:
                graph = pickle.loads((graph_pickled.encode()))
                if(graph.is_directed()):
                    directed_edges = [
                        {
                            'selector': '#' + str(e.source + 1) + '-' + str(e.target + 1),
                            'style': {
                                'target-arrow-color': 'blue',
                                'target-arrow-shape': 'triangle',
                                'arrow-scale': 0.3,
                            }
                        } for e in graph.es
                    ]
                else:
                    directed_edges = []
            else:
                directed_edges = []

            return stylesheet + activated_nodes + newly_activated_styles + node_size_metric_style + directed_edges

        if node_size_metric is not None:
            rule = "mapData(" + node_size_metric + ", 1, 50, 2, 15)" if node_size_metric != 'clustering_coeff' \
                else "mapData(" + node_size_metric + ", 0, 1, 2, 10)"
            node_size_metric_style = [
                {
                    "selector": "node",
                    "style": {
                        "width": rule,
                        "height": rule,
                        "font-size": "6px",
                    }
                }
            ]
            return stylesheet + node_size_metric_style
        return stylesheet
    
    @app.callback(Output('cytoscape-elements', 'layout'),
                  [Input('layout-dropdown', 'value')])
    def update_layout(dropdown_value):
        return {'name': dropdown_value, 'animate': True}
    
    @app.callback(Output('data-selected-nodes', 'data'),
                  [Input('cytoscape-elements', 'selectedNodeData')])
    def update_selected_nodes(selected_nodes):
        if selected_nodes:
            return [int(node['id'])for node in selected_nodes]
        return []

    @app.callback(Output('computer-upload-modal', 'is_open'),
                  [Input('open-upload-modal', 'n_clicks'), Input('close-upload-modal', 'n_clicks')],
                  [State('computer-upload-modal', 'is_open')])
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(Output('modal', 'is_open'),
                  [Input('open-konect-modal', 'n_clicks'), Input('close-konect-modal', 'n_clicks')],
                  [State('modal', 'is_open')])
    def toggle_modal2(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(Output('info-modal', 'is_open'),
                  [Input('info-button', 'n_clicks'), Input('close-info-button', 'n_clicks')],
                  [State('info-modal', 'is_open')])
    def toggle_info_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(Output('uploaded-file-name', 'children'),
                [Input('upload-data', 'filename')])
    def set_uploaded_filename(filename):
        if filename is not None:
            return filename
        return ''

    @app.callback(Output('activations-graph', 'figure'),
                  [Input('start-button', 'n_clicks')],
                  [State('graph-pickled', 'data'),
                   State('depth-limit', 'value'),
                   State('treshold', 'value'),
                   State('data-selected-nodes', 'data'),
                   State('initial-nodes-method-dropdown','value'),
                   State('initial-nodes-number', 'value'),
                   State('model-dropdown', 'value')])
    def generate_statistics(n_clicks, graph_pickled, depth, treshold, initial_nodes, init_nodes_method, init_nodes_num, model):
        if not n_clicks == 0 and n_clicks is not None and graph_pickled is not None and treshold is not None and depth is not None:
            graph = pickle.loads((graph_pickled.encode()))

            init_nodes_methods = [option['value'] for option in initial_nodes_method_options]

            if initial_nodes == []:
                init_nodes_methods.remove('manual')
            
            activated_nodes_data = get_methods_activated_nodes_data(graph, model, init_nodes_num, init_nodes_methods, depth, treshold, initial_nodes)

            activations_figure = {
                'data': [
                    {
                        'type': 'scatter',
                        'y': activated_nodes_data[method],
                        'name': method,
                    } for method in activated_nodes_data
                ],
                'layout': {
                    'title':'Activated nodes in iteration i',
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

            return activations_figure
        return {}


    @app.callback(Output('download-link', 'href'),
                  [Input('data-activated-nodes', 'data')])
    def update_download_link(activations_data):
        if activations_data is not None:
            result = io.StringIO()
            writer = csv.writer(result)
            for node_list in activations_data:
                new_list = [node + 1 for node in node_list]
                writer.writerow(new_list)
            csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(result.getvalue())
            return csv_string
        else:
            return ''

    @app.callback(Output('treshold', 'disabled'),
                  [Input('model-dropdown', 'value')])
    def treshold_input_state(model):
        if model == 'lintres':
            return True
        else:
            return False