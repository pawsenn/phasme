"""High level routines implementing the user-level behaviors.

"""

import os
from inspect import getfullargspec
from collections import OrderedDict
import networkx
from grasp import commons
from grasp.asp import asp_from_graph
from grasp.info import info
from grasp.commons import edge_predicate
from grasp.build_graph import graph_from_file, graph_to_file


def split_by_cc(fname:str, targets:str=None, edge_predicate:str=edge_predicate) -> tuple:
    """Return names of targets written"""
    if not targets:
        name, ext = os.path.splitext(fname)
        targets = name + '_{}' + ext
    elif not isinstance(targets, str):
        raise ValueError("Target should be a filename to write")
    elif '{}' not in targets:
        raise ValueError("Target should be a filename to write containing '{}'")
    graph = graph_from_file(fname, edge_predicate=edge_predicate)
    writtens = []
    for idx, cc_nodes in enumerate(networkx.connected_components(graph)):
        cc = graph.subgraph(cc_nodes)
        target = targets.format(idx)
        with open(target, 'w') as fd:
            for line in asp_from_graph(cc, edge_predicate=edge_predicate):
                fd.write(line+'\n')
        writtens.append(target)
    return tuple(writtens)


def clean(fname:str, target:str=None,
          edge_predicate:str=edge_predicate,
          target_edge_predicate:str=edge_predicate) -> dict:
    """Write in target the very same graph as input, but in
    an clean ASP expanded format.

    target -- file to write. If None or equal to fname, overwrite.
    target_edge_predicate -- edge predicate to use in rewritten file.

    """
    fname = commons.normalize_filename(fname)
    if target: target = commons.normalize_filename(target)
    if not target:  target = fname
    graph = graph_from_file(fname, edge_predicate=edge_predicate)
    graph_to_file(graph, target, edge_predicate=target_edge_predicate)
