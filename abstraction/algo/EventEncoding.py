import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

import numpy as np
from pm4py.objects.log.obj import EventLog
from abstraction.algo.cluster_patterns import cluster
from abstraction.algo.constants import PATTERNS, CLUSTERS, DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, DEFAULT_LIFECYCLE_VALUE, MATRIX


def get_cluster_count(cluster_dicto):
    return max(val for val in cluster_dicto.values()) + 1


def get_data_for_event_clustering(event_log, cluster_data):
    cluster_encoding = []   
    total_no_of_clusters = get_cluster_count(cluster_data[CLUSTERS])

    for case in event_log:
        trace = [event[DEFAULT_ACTIVITY_KEY].split('@')[0] for event in case if event[DEFAULT_LIFECYCLE_KEY] == DEFAULT_LIFECYCLE_VALUE]
        for event in case:
            if event[DEFAULT_LIFECYCLE_KEY] == DEFAULT_LIFECYCLE_VALUE:
                arr = list(np.zeros(total_no_of_clusters, dtype = int))
                patterns = cluster_data[PATTERNS][event[DEFAULT_ACTIVITY_KEY]]
                for patt in patterns:
                    check =  all(item in trace for item in list(patt))
                    if check:
                        arr[cluster_data[CLUSTERS][repr(patt)]] = 1
                    
                cluster_encoding.append(arr)

    return cluster_encoding


def merge_prec_succ_clusters(preceding_cluster_encoding, succeeding_cluster_encoding):
    for idx, ele in enumerate(preceding_cluster_encoding):
        new_vals = []
  
        # getting all values at same index row
        for ele in succeeding_cluster_encoding[idx]:
            new_vals.append(ele)
    
        # extending the initial matrix
        preceding_cluster_encoding[idx].extend(new_vals)
    
    return preceding_cluster_encoding


def apply(event_log: EventLog):
    po_graph_per_case, preceding_cluster_data, succeeding_cluster_data = cluster.apply(event_log)

    average_similarity_matrix = (preceding_cluster_data[MATRIX] + succeeding_cluster_data[MATRIX]) / 2

    return po_graph_per_case, average_similarity_matrix
