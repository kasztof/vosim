from dash.dependencies import Input, Output, State
from influ.finder.model import independent_cascade
from influ import reader
from vosim.utils import get_graph, get_network_from_graph
import pickle

def register_callbacks(app, stylesheet):
    @app.callback([Output('cytoscape-elements', 'elements'),
                   Output('graph-pickled', 'data'),
                   Output('cytoscape-elements', 'stylesheet')],
                  [Input('upload-data', 'contents'),
                   Input('load-konect-network', 'n_clicks'),
                   Input('slider', 'value'),
                   Input('data-activated-nodes', 'data')],
                  [State('konect-networks-dropdown', 'value'),
                   State('cytoscape-elements', 'stylesheet')])
    def load_network(upload_content, n_clicks, slider_value, activated_nodes, konect_network_name, stylesheet):
        if slider_value is not None and activated_nodes is not None:
            print("FIRST")
            graph = get_graph(upload_content)
            new_styles = [
                {
                    'selector': '[label = ' + str(node_id) + ']',
                    'style': {
                        'background-color': 'red'
                    }
                } for node_id in activated_nodes[slider_value]
            ]
            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode(), stylesheet + new_styles
        elif upload_content is not None:
            print("SECOND")
            graph = get_graph(upload_content)

            directed_edges = [
                {
                    'selector': '#' + str(e.source) + str(e.target),
                    'style': {
                        'target-arrow-color': 'blue',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': 0.3,
                    }
                } for e in graph.es
            ]

            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode(), stylesheet + directed_edges
        elif n_clicks != 0 and n_clicks is not None and konect_network_name is not None:
            print("THIRD")
            kr = reader.KonectReader()
            graph = kr.load(konect_network_name)

            directed_edges = [
                {
                    'selector': '#' + str(e.source) + str(e.target),
                    'style': {
                        'source-arrow-color': 'blue',
                        'source-arrow-shape': 'triangle',
                        'arrow-scale': 0.3,
                    }
                } for e in graph.es
            ]

            return get_network_from_graph(graph), pickle.dumps(graph, 0).decode(), stylesheet + directed_edges
        return [], None, stylesheet
    
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
    
    # @app.callback(Output('cytoscape-elements', 'stylesheet'),
    #               [Input('slider', 'value'),
    #                Input('data-activated-nodes', 'data')])
    # def update_active_nodes(value, data):
    #     if value is not None and data is not None:
    #         new_styles = [
    #             {
    #                 'selector': '[label = ' + str(node_id) + ']',
    #                 'style': {
    #                     'background-color': 'red'
    #                 }
    #             } for node_id in data[value]
    #         ]
    #         return stylesheet + new_styles
    #     return stylesheet
    
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