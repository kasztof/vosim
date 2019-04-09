import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import flask
import pandas as pd
import time
import os
import networkx as nx

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/hello-world-stock.csv')

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'




G=nx.random_geometric_graph(200,0.125)
pos=nx.get_node_attributes(G,'pos')

dmin=1
ncenter=0
for n in pos:
    x,y=pos[n]
    d=(x-0.5)**2+(y-0.5)**2
    if d<dmin:
        ncenter=n
        dmin=d

p=nx.single_source_shortest_path_length(G,ncenter)
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    x0, y0 = G.node[edge[0]]['pos']
    x1, y1 = G.node[edge[1]]['pos']
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=2)))

for node in G.nodes():
    x, y = G.node[node]['pos']
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])

for node, adjacencies in enumerate(G.adjacency()):
    node_trace['marker']['color']+=tuple([len(adjacencies[1])])
    node_info = '# of connections: '+str(len(adjacencies[1]))
    node_trace['text']+=tuple([node_info])





app.layout = html.Div([
    dcc.Graph(
        figure=go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        ),
        id='my-graph-1'
    ),
    # dcc.Dropdown(
    #     #     id='my-dropdown',
    #     #     options=[
    #     #         {'label': 'Tesla', 'value': 'TSLA'},
    #     #         {'label': 'Apple', 'value': 'AAPL'},
    #     #         {'label': 'Coke', 'value': 'COKE'}
    #     #     ],
    #     #     value='TSLA'
    #     # ),
    dcc.Graph(id='my-graph'),
    dcc.Slider(
        id='my-slider',
        min=0,
        max=2,
        step=1,
        value=0,
        updatemode='drag',
    ),
], className="container")


values = {
    0: 'TSLA',
    1: 'AAPL',
    2: 'COKE'
}


@app.callback(Output('my-graph', 'figure'),
              [Input('my-slider', 'value')])
def update_graph(selected_dropdown_value):
    print(selected_dropdown_value)
    dff = df[df['Stock'] == values[selected_dropdown_value]]
    return {
        'data': [{
            'x': dff.Date,
            'y': dff.Close,
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }


if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=True)
