import os
from vosim.utils import get_network_from_graph, get_init_nodes, get_degree_distribution_data, get_network_info, get_graph_statistics
from influ.reader import direct
from conftest import test_data_path
from igraph import Graph

tests_dir =  os.path.abspath(os.path.join(__file__ ,"../.."))
filename = os.path.join(tests_dir, 'test_data/network.csv')
test_graph = direct.read_graph(filename, file_format='events', directed=False)


def test_get_network_from_graph_undirected(test_data_path):
    correct_result_nodes = [
        {
            'data': {
                'id': 1,
                'id_vosim': 1,
                'label': 1,
                'degree': 3,
                'betweenness': 0.5,
                'clustering_coeff': 0.6666666666666666
            },
        },
        {
            'data': {
                'id': 2,
                'id_vosim': 2,
                'label': 2,
                'degree': 3,
                'betweenness': 0.5,
                'clustering_coeff': 0.6666666666666666
            },
        },
        {
            'data': {
                'id': 3,
                'id_vosim': 3,
                'label': 3,
                'degree': 2,
                'betweenness': 0.0,
                'clustering_coeff': 1.0
            },
        },
        {
            'data': {
                'id': 4,
                'id_vosim': 4,
                'label': 4,
                'degree': 2,
                'betweenness': 0.0,
                'clustering_coeff': 1.0
            },
        }
    ]

    correct_result_edges = [
        {
            'data': {
                'source': 1,
                'target': 2,
                'id': '1-2'
            }
        },
        {
            'data': {
                'source': 1,
                'target': 3,
                'id': '1-3'
            }
        },
        {
            'data': {
                'source': 2,
                'target': 3,
                'id': '2-3'
            }
        },
        {
            'data': {
                'source': 1,
                'target': 4,
                'id': '1-4'
            }
        },
        {
            'data': {
                'source': 2,
                'target': 4,
                'id': '2-4'
            }
        }
    ]

    correct_response = correct_result_nodes + correct_result_edges
    response = get_network_from_graph(test_graph)
   
    assert correct_response == response


def test_get_init_nodes_by_degree():
    result = get_init_nodes(test_graph, 'degree', 2)
    correct_result = [0,1]
    
    assert result == correct_result


def test_get_degree_distribution_data():
    result = get_degree_distribution_data(test_graph)
    correct_result = {0: 0, 1: 0, 2: 2, 3: 2}
    
    assert result == correct_result

def test_graph_statistics():
    result = get_graph_statistics(test_graph)
    correct_result = {
        'Average degree': '2.5 edges/vertex',
        'Clustering coefficient': '75.0%',
        'Diameter': '2 edges',
        'Size': '4 vertices',
        'Volume': '5 edges'
    }

    assert result == correct_result



def test_get_network_info():
    result = get_network_info('test', test_graph)
    correct_result = {
        'Network name:': 'test',
        'Size:': '4 vertices',
        'Volume:': '5 edges',
        'Directed:': 'False'
    }
    
    assert result == correct_result