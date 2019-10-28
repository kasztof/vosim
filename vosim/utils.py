import io
import base64
from influ import reader


def get_network(content: str, file_format: str = 'events') -> list:
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    string_io = io.StringIO(decoded.decode('utf-8'))
    # TODO handle file_format (NCOL/events)
    graph = reader.read_graph(string_io, file_format)
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
            }
        }
        for e in graph.es
    ]
    
    return nodes + edges