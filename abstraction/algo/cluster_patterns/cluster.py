import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

import numpy as np
from pm4py.objects.log.obj import EventLog
from abstraction.algo.cluster_patterns.create_patterns import apply as patterns
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, PATTERNS, MATRIX, START_LIFECYCLE_VALUE
from sklearn.metrics import pairwise_distances
import networkx as nx
import numpy as np


patt_list = []
def __graph_edit_distance(el1, el2):
    if el1 != None and el2 != None:
        x = set(patt_list[int(el1[0])].split('-'))
        y = set(patt_list[int(el2[0])].split('-'))
        patt1 = nx.DiGraph()
        patt2 = nx.DiGraph()
        patt1.add_nodes_from(x)
        patt2.add_nodes_from(y)
        return nx.graph_edit_distance(patt1, patt2)
    else:
        return None


def __get_pattern_distance_matrix(patterns_list):
    unique_sets =  np.unique(['-'.join(list(p)) for p in patterns_list])
    patterns_list_set = np.array(['-'.join(patt) for patt in patterns_list]).reshape(-1, 1)
    X = np.searchsorted(unique_sets, patterns_list_set).reshape(-1, 1)

    global patt_list
    patt_list = unique_sets

    distance_matrix = pairwise_distances(X, metric=__graph_edit_distance)

    return distance_matrix


def get_matrix(patterns, trace_events):
    patt_list = []
    for e in trace_events:
        for p in patterns[e]:
            patt_list.append(p)

    distance_matrix = __get_pattern_distance_matrix(patt_list)
    return distance_matrix



def add_id_to_events(event_log):
    idx = 0
    for case in event_log:
        for event in case:
            event['@@index'] = idx
            event['concept:name'] = event['concept:name'] + '@' + str(idx)
            idx += 1


def apply(event_log: EventLog):
    add_id_to_events(event_log)

    events = [event[DEFAULT_ACTIVITY_KEY] for trace in event_log for event in trace if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE]

    po_graphs_per_case, preceding_patterns, succeeding_patterns = patterns(event_log)

    preceding_matrix = get_matrix(preceding_patterns, events)

    succeeding_matrix = get_matrix(succeeding_patterns, events)

    preceding_cluster_data = {
        PATTERNS: preceding_patterns,
        MATRIX: preceding_matrix
    }

    succeeding_cluster_data = {
        PATTERNS: succeeding_patterns,
        MATRIX: succeeding_matrix
    }

    return po_graphs_per_case, preceding_cluster_data, succeeding_cluster_data
