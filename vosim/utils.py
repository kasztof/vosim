import io
import base64

from igraph import mean

def get_network_from_graph(graph, file_format: str = 'events') -> list:
    nodes = [
        {
            'data': {
                'id': node['id'],
                'id_vosim': node['id'],
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
                'id': str(e.source + 1) + '-' + str(e.target + 1)
            }
        }
        for e in graph.es
    ]

    return nodes + edges


def get_degree_distribution_data(graph):
    degrees = {}
    for i in range(graph.vs.maxdegree() + 1):
        degrees[i] = 0

    for node in graph.vs:
        degrees[node.degree()] += 1

    return degrees


def get_graph_statistics(graph):
    return {
        'Size': str(graph.vcount()) + ' vertices',
        'Volume': str(graph.ecount()) + ' edges',
        'Average degree': str(round(mean(graph.degree()), 2)) + ' edges/vertex',
        'Clustering coefficient': str(round(graph.transitivity_undirected() * 100, 2)) + '%',
        'Diameter': str(graph.diameter(directed=False)) + ' edges',
    }


def get_network_info(network_name, graph):
    return {
        'Network name:': network_name,
        'Size:': str(graph.vcount()) + ' vertices',
        'Volume:': str(graph.ecount()) + ' edges',
        'Directed:': str(graph.is_directed())
    }