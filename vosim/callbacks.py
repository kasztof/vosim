from dash.dependencies import Input, Output, State
from influ.finder.model import independent_cascade
from influ import reader
from vosim.utils import get_graph, get_network_from_graph
import pickle

def register_callbacks(app, stylesheet):
    @app.callback([Output('cytoscape-elements', 'elements'),
                   Output('graph-pickled', 'data')],
                  [Input('upload-data', 'contents'),
                   Input('load-konect-network', 'n_clicks')],
                  [State('konect-networks-dropdown', 'value')])
    def load_network(upload_content, n_clicks, konect_network_name):
        if upload_content is not None:
            graph = get_graph(upload_content)
            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode() 
        elif n_clicks != 0 and n_clicks is not None and konect_network_name is not None:
            kr = reader.KonectReader()
            graph = kr.load(konect_network_name)
            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode() 
        return [], None
    
    @app.callback([Output('data-activated-nodes', 'data'),
                   Output('slider', 'value'),
                   Output('slider', 'max'),
                   Output('slider', 'marks')],
                  [Input('start-button', 'n_clicks')],
                  [State('graph-pickled', 'data'),
                   State('depth-limit', 'value'),
                   State('treshold', 'value'),
                   State('data-selected-nodes', 'data')])
    def load_activated_nodes(n_clicks, graph_pickled, depth, treshold, initial_nodes):
        if not n_clicks == 0 and n_clicks is not None and graph_pickled is not None:
            graph = pickle.loads((graph_pickled.encode()))
            result = independent_cascade(graph, initial_nodes, depth=depth, threshold=treshold)
    
            slider_value = 0
            slider_max = len(result) - 1
            slider_marks = {i: '{}'.format(i) for i in range(len(result))}
    
            return result, slider_value, slider_max, slider_marks
        return None, 0, 0, {}
    
    @app.callback(Output('cytoscape-elements', 'stylesheet'),
                  [Input('slider', 'value'),
                   Input('data-activated-nodes', 'data'),
                   Input('node-size-dropdown', 'value')])
    def update_active_nodes(slider_value, data, node_size_metric):
        if slider_value is not None and data is not None:
            new_styles = [
                {
                    'selector': '[label = ' + str(node_id) + ']',
                    'style': {
                        'background-color': 'red'
                    }
                } for node_id in data[slider_value]
            ]
            return stylesheet + new_styles

        elif node_size_metric is not None:
            rule = "mapData(" + node_size_metric + ", 1, 50, 2, 15)" if node_size_metric != 'clustering_coeff' \
                else "mapData(" + node_size_metric + ", 0, 1, 2, 10)"
            print(rule)
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

    @app.callback(Output("modal", "is_open"),
                  [Input("open-konect-modal", "n_clicks"), Input("close-konect-modal", "n_clicks")],
                  [State("modal", "is_open")])
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open