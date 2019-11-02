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
                'id': node_id,
                'label': node_id,
                'score': degree
            },
        }
        for node_id, degree in (
            zip(graph.vs.indices, graph.vs.degree())
        )
    ]

    edges = [
        {
            'data': {
                'source': e.source,
                'target': e.target,
                'id': str(e.source) + str(e.target)
            }
        }
        for e in graph.es
    ]

    return nodes + edges