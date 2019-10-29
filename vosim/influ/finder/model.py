import random
from enum import Enum
from numbers import Real
from typing import List, TypeVar, Callable, Optional, Set, Union

import igraph as ig

ThresholdV = TypeVar('ThresholdV', Real, Callable[..., Real])


class Model(Enum):
    LinearThreshold = 'LT'
    IndependentCascade = 'IC'


def get_model(model: Union[Model, str]):
    return {
        Model.LinearThreshold: linear_threshold,
        Model.LinearThreshold.value: linear_threshold,
        Model.IndependentCascade: independent_cascade,
        Model.IndependentCascade.value: independent_cascade,
    }[model]


def linear_threshold(graph: ig.Graph, initial_ids: List[int], threshold: Optional[ThresholdV] = None,
                     depth: Optional[int] = None, random_seed: Optional[int] = None) -> Set[int]:
    """
    Applies Linear Threshold influence model until no new nodes are influenced in iteration
    or iteration counter exceed depth limit
    """

    if random_seed:
        random.seed(random_seed)
    g = graph.copy()
    depth = depth or float('inf')

    if 'treshold' not in g.vertex_attributes():
        _apply_param(g, 'treshold', threshold)

    g.vs['influenced'] = False
    g.vs.select(id_in=initial_ids)['influenced'] = True
    influenced_ids = set(initial_ids)

    new_influenced = initial_ids
    i = 0
    while len(new_influenced) > 0 and i < depth:
        uninfluenced = g.vs.select(influenced=False)
        new_influenced = []

        for v in uninfluenced:
            inf_neigh = g.vs.select(g.neighbors(v, mode=ig.IN), influenced=True)
            es = g.es.select(_target=v['id'], _source_in=inf_neigh['id'])

            if inf_neigh and sum(es['weight']) >= v['treshold']:
                v['influenced'] = True
                new_influenced.append(v['id'])

        influenced_ids.update(new_influenced)
        i += 1

    return influenced_ids


def independent_cascade(graph: ig.Graph, initial_ids: List[int], threshold: Optional[ThresholdV] = None,
                        depth: Optional[int] = None, random_seed: Optional[int] = None) -> Set[int]:
    """
    Applies Independent Cascade influence model until no new nodes are influenced in iteration
    or iteration counter exceed depth limit
    """
    # print("---Model start---")
    if random_seed is not None:
        random.seed(random_seed)
        initial_ids = sorted(initial_ids)
    g = graph.copy()
    depth = depth or float('inf')

    if 'treshold' not in g.vertex_attributes():
        _apply_param(g, 'treshold', threshold)

    g.vs['influenced'] = False
    g.vs['retired'] = False
    g.vs.select(id_in=initial_ids)['influenced'] = True
    influenced_ids = initial_ids
    all_activations = [initial_ids]

    new_influenced = initial_ids
    i = 0
    while len(new_influenced) > 0 and i < depth:
        influencers = g.vs.select(new_influenced)
        new_influenced = []

        for v in influencers:
            healthy_neigh = g.vs.select(g.neighbors(v, mode=ig.OUT), influenced=False)

            for exposed in healthy_neigh:
                r = random.random()
                assert r is not None
                if r >= v['treshold']:
                    exposed['influenced'] = True
                    new_influenced.append(exposed['id'])

            v['retired'] = True
        influenced_ids = influenced_ids + new_influenced
        all_activations.append(influenced_ids)
        i += 1
    
    return all_activations


def _apply_param(g: ig.Graph, param_name: str, value: Optional[Real] = None) -> None:
    """As side effect apply parameter value to all vertices of graph"""
    if value is not None and not callable(value):
        g.vs[param_name] = value
    else:
        tresholdf = value or random.random
        g.vs[param_name] = [tresholdf() for _ in range(len(g.vs))]
