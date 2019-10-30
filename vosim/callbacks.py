from dash.dependencies import Input, Output
from influ.finder.model import independent_cascade
from vosim.utils import get_graph, get_network


def register_callbacks(app, stylesheet):
    @app.callback([Output('cytoscape-elements', 'elements'),
                   Output('data-file-content', 'data')],
                  [Input('upload-data', 'contents')])
    def load_network(content):
        if content is not None:
            return get_network(content), content
        return [], None
    
    @app.callback([Output('data-activated-nodes', 'data'),
                   Output('slider', 'value'),
                   Output('slider', 'max'),
                   Output('slider', 'marks')],
                  [Input('start-button', 'n_clicks'),
                   Input('data-file-content', 'data'),
                   Input('depth-limit', 'value'),
                   Input('treshold', 'value'),
                   Input('data-selected-nodes', 'data')])
    def load_activated_nodes(n_clicks, content, depth, treshold, initial_nodes):
        if not n_clicks == 0 and n_clicks is not None and content is not None:
            graph = get_graph(content)
            result = independent_cascade(graph, initial_nodes, depth=depth, threshold=treshold)
    
            slider_value = 0
            slider_max = len(result) - 1
            slider_marks = {i: '{}'.format(i) for i in range(len(result))}
    
            return result, slider_value, slider_max, slider_marks
        return None, 0, 0, {}
    
    @app.callback(Output('cytoscape-elements', 'stylesheet'),
                  [Input('slider', 'value'),
                   Input('data-activated-nodes', 'data')])
    def update_active_nodes(value, data):
        if value is not None and data is not None:
            new_styles = [
                {
                    'selector': '[label = ' + str(node_id) + ']',
                    'style': {
                        'background-color': 'red'
                    }
                } for node_id in data[value]
            ]
            return stylesheet + new_styles
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
