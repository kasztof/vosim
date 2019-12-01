import os

from vosim.middleware import get_init_nodes, get_graph
from influ.reader import direct

tests_dir =  os.path.abspath(os.path.join(__file__ ,"../.."))
filename = os.path.join(tests_dir, 'test_data/network.csv')
test_graph = direct.read_graph(filename, file_format='events', directed=False)

def test_get_init_nodes_by_degree():
    result = get_init_nodes(test_graph, 'degree', 2)
    correct_result = [0,1]
    
    assert result == correct_result


def test_get_init_nodes_by_betweenness():
    result = get_init_nodes(test_graph, 'betweenness', 2)
    correct_result = [0,1]
    
    assert result == correct_result


def test_get_init_nodes_by_clustering_coeff():
    result = get_init_nodes(test_graph, 'clustering_coeff', 2)
    correct_result = [2,3]
    
    assert result == correct_result
