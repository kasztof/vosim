import io
import base64

from influ import reader
from influ.finder.influence import SeedFinder
from influ.finder.model import independent_cascade, linear_threshold


def get_konect_network(konect_network_name):
    kr = reader.KonectReader()
    graph = kr.load(konect_network_name)

    return graph, konect_network_name


def get_graph(content: str, file_format: str = 'events', directed: bool = False):
    _, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    string_io = io.StringIO(decoded.decode('utf-8'))
    graph = reader.read_graph(string_io, file_format, directed=directed)
    return graph


def get_init_nodes(graph, init_nodes_method, init_nodes_num):
    finder = SeedFinder(graph, init_nodes_num)

    init_nodes = []
    if init_nodes_method == 'degree':
        init_nodes = finder.by_degree()
    elif init_nodes_method == 'betweenness':
        init_nodes = finder.by_betweenness()
    elif init_nodes_method == 'clustering_coeff':
        init_nodes = finder.by_clustering_coefficient()
    elif init_nodes_method == 'random':
        init_nodes = finder.by_random()

    return init_nodes



def get_model_result(graph, model, init_nodes, depth, treshold):
    if model == 'lintres':
        return linear_threshold(graph, init_nodes, depth=depth, threshold=treshold)
    else:
        return independent_cascade(graph, init_nodes, depth=depth, threshold=treshold)


def get_methods_activated_nodes_data(graph, model, init_nodes_num, methods_list, depth, threshold, manual_init_nodes=None):
    result = {}
    for method in methods_list:
        if method == 'manual' and manual_init_nodes is not None:
            init_nodes = manual_init_nodes
        else:
            init_nodes = get_init_nodes(graph, method, init_nodes_num)

        model_result = get_model_result(graph, model, init_nodes, depth=depth, treshold=threshold)
        num_of_activated_nodes = [len(l) for l in model_result]
        result[method] = num_of_activated_nodes
    return result