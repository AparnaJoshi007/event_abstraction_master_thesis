import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from collections import defaultdict
from sklearn.cluster import AgglomerativeClustering
from pm4py.objects.log.obj import EventLog
from typing import Any, Dict, List, Optional
from abstraction.algo import EventEncoding
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, DEFAULT_LIFECYCLE_VALUE, CLUSTER_COUNT, METRIC, START_LIFECYCLE_VALUE
import abstraction.algo.CCA as cca 


RESULT = 'result'


def map_activities_to_classes(trace_list: List, cluster_class: List):
    activity_to_class = defaultdict(dict)
    for idx, e in enumerate(trace_list):
        activity_to_class[e][RESULT] = cluster_class[idx] + 1

    activity_to_class_lp = cca.apply(activity_to_class)

    return activity_to_class_lp


def map_cluster_to_patterns(activity_to_class_lp, preceding_patterns, succeeding_patterns):
    cluster_to_patterns = defaultdict(dict)
    for activity in activity_to_class_lp:
        cluster = activity_to_class_lp[activity]
        preceding = preceding_patterns[activity]
        succeeding = succeeding_patterns[activity]
        if 'Preceding' not in cluster_to_patterns[cluster[RESULT]]:
            cluster_to_patterns[cluster[RESULT]]['Preceding'] = set()
        if 'Succeeding' not in cluster_to_patterns[cluster[RESULT]]:
            cluster_to_patterns[cluster[RESULT]]['Succeeding'] = set()
        cluster_to_patterns[cluster[RESULT]]['Preceding'].add(repr(preceding[0]))
        cluster_to_patterns[cluster[RESULT]]['Succeeding'].add(repr(succeeding[0]))

    return cluster_to_patterns


def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]]):
    if parameters is None:
        parameters = {CLUSTER_COUNT: 3, METRIC: 'euclidean'}

    po_graphs_per_case, average_similarity_matrix = EventEncoding.apply(event_log)

    kmeans = AgglomerativeClustering(n_clusters=parameters[CLUSTER_COUNT], affinity=parameters[METRIC], linkage='average').fit(average_similarity_matrix)

    trace_list = [event[DEFAULT_ACTIVITY_KEY] for case in event_log for event in case if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE]

    activity_to_class_lp = map_activities_to_classes(trace_list, kmeans.labels_)

    return activity_to_class_lp