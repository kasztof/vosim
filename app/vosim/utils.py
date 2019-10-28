from typing import Optional

def get_network(file, file_format):
    nodes = [
        {
            'data': {
                'id': id,
                'label': id,
                'score': degree
            },
        }
        for id, degree in (
            zip(graph.vs.indices, graph.vs.degree())
        )
    ]

    edges = []
    for e in graph.es:
        edges_array.append({
            'data': {
                'source': e.tuple[0],
                'target': e.tuple[1],
            }
        })
