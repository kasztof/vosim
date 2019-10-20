from collections import defaultdict
from typing import Iterable

import igraph as ig


class EdgeSum:
    """
    Sum of edges with the same source and target.
    Attributes of all copies of edge are collected into list.
    """

    def __init__(self, source, target, init_size=None, init_attrs=None):
        self.source = source
        self.target = target
        self.size = init_size or 0
        self.attributes = init_attrs or defaultdict(list)

    def update(self, attrs):
        self.size += 1
        for attr_name, attr_value in attrs.items():
            self.attributes[attr_name].append(attr_value)

    @property
    def weight(self):
        return self.attributes['weight']

    def set_weight(self, total_edges):
        if 'weight' in self.attributes:
            self.attributes['original_weight'] = self.attributes['weight']
        self.attributes['weight'] = self.size / total_edges

    def __eq__(self, other):
        return (self.source == other.source
                and self.target == other.target
                and self.size == other.size
                and self.attributes == other.attributes)

    def __repr__(self):
        return f'EdgeSum({self.source}, {self.target}, {self.size}, {self.attributes}'


def merge_edges(graph: ig.Graph) -> ig.Graph:
    """
    For every vertex:
      * remove self-loops
      * remove duplicated edges with single edge with weight,
        where weight is number of edges with the same (source, target),
        divided by number of edges with the same target
      * additional attributes of edges are kept as list attribute in new edge
      e.g.:
      [
        Edge(_from=0, _to=1, attrs={asd:22}),
        Edge(_from=0, _to=1, attrs={asd:15}),
        Edge(_from=1, _to=1, attrs={asd:5}),
        Edge(_from=2, _to=1, attrs={asd:6}),
        Edge(_from=2, _to=3, attrs={asd:-4})
      ]
        are transformed to:
      [
        Edge(_from=0, _to=1, attrs={asd:[22, 15], weight: 2/3}),
        Edge(_from=2, _to=1, attrs={asd:[6], weight: 1/3}),
        Edge(_from=2, _to=3, attrs={asd:[-4], weight: 1/1})
      ]
    """
    edges = []
    g = graph.copy()
    g.delete_edges(g.es)
    for vertex_id in range(graph.vcount()):
        edges.extend(sum_edges(graph, vertex_id))

    for edge in edges:
        g.add_edge(edge.source, edge.target, **edge.attributes)

    return g


def sum_edges(graph: ig.Graph, target: int) -> Iterable[EdgeSum]:
    """
    Sum edges with the same source.
    Omits self-loops.

    :param graph: Graph
    :param target: id of target vertex
    :return: list of EdgeSum objects
    """
    edges = graph.es.select(_target=target, _source_ne=target)
    total_edges = 0
    counter = {}
    for e in edges:
        total_edges += 1
        esum = counter.setdefault(e.source, EdgeSum(e.source, target))
        esum.update(attrs=e.attributes())

    for esum in counter.values():
        esum.set_weight(total_edges)
    return counter.values()
