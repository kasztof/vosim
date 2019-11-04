import io
import base64
from influ import reader


def get_graph(content: str, file_format: str = 'events'):
    _, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    string_io = io.StringIO(decoded.decode('utf-8'))
    graph = reader.read_graph(string_io, file_format)
    return graph


def get_network_from_graph(graph, file_format: str = 'events') -> list:
    nodes = [
        {
            'data': {
                'id': node['id'],
                'label': node['label'],
                'degree': degree,
                'betweenness': betweenness,
                'clustering_coeff': clustering_coeff
            },
        }
        for node, degree, betweenness, clustering_coeff in (
            zip(graph.vs, graph.degree(), graph.betweenness(), graph.transitivity_local_undirected())
        )
    ]

    edges = [
        {
            'data': {
                'source': e.source + 1,
                'target': e.target + 1,
            }
        }
        for e in graph.es
    ]

    return nodes + edges