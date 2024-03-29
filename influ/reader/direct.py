from typing import Optional

import igraph as ig
import pandas as pd

from .merge import merge_edges


def read_graph(filepath: str, file_format: Optional[str] = None, **kwargs) -> ig.Graph:
    """
    Read graph from file if it is saved in event format.
    Otherwise igraph read method is used.

    :param filepath: path to file with graph
    :param file_format: optional (but recommended) format name how graph is stored
    :param kwargs: additional keyword arguments specific to source file type
    :return: igraph Graph object
    """
    if file_format == 'events':
        g = _read_events(filepath, **kwargs)
    else:
        g = ig.Graph.Read(f=filepath, format=file_format, **kwargs)

    if not hasattr(g, 'shift'):
        g.shift = 0

    if 'id' in g.vs.attributes():
        g.vs['origin_id'] = g.vs['id']
    g.vs['id'] = range(1, len(g.vs) + 1)
    g.vs['calc_id'] = range(0, len(g.vs) + 1)

    return merge_edges(g)


def _read_events(filepath: str, sep: str = ',', directed: bool = True) -> ig.Graph:
    df = pd.read_csv(filepath, sep)
    return _df_to_graph(df, directed)


def _df_to_graph(data: pd.DataFrame, directed: bool = True) -> ig.Graph:
    """
    Converts Pandas DataFrame to Graph.
    First column is expected to be index of starting node, second - index of target node,
    any additional columns will be treated as attributes of edge.

    :param data: pandas DataFrame to be converted to graph
    :param directed: flag is graph directed or undirected.
    :return: igraph Graph object
    """
    _from, _to, *_attrs = data.columns
    # shift = int(min(data.min()[:2])) # wartosc odpowiadajaca najmniejszemu indeksowi wezla?
    edges = list(zip(data[_from].astype(int), data[_to].astype(int)))
    edge_attributes = {attr: data[attr].tolist() for attr in _attrs}
    graph = ig.Graph(edges=edges, edge_attrs=edge_attributes, directed=directed)

    origin_ids = []
    for n in graph.vs:
        origin_ids.append(n.index)
    graph.vs['label'] = origin_ids
    
    to_delete_ids = [v.index for v in graph.vs if v.degree() == 0]
    graph.delete_vertices(to_delete_ids)
    return graph
