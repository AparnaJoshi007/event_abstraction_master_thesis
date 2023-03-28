import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

import numpy as np
from pm4py.objects.log.obj import EventLog
import skfuzzy as fuzz
from collections import defaultdict
import numpy as np
from typing import Any, Dict, List, Optional
from abstraction.algo import EventEncoding
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, CLUSTERS, CLUSTER_COUNT, METRIC, START_LIFECYCLE_VALUE, THRESHOLD
import abstraction.algo.CCA as cca 

RESULT = 'result'

def map_activities_to_classes(event_log, trace_list: List, cluster_probabilities: List, threshold: float, po_graph_per_case, average_similarity_matrix):
    activity_to_class = defaultdict(dict)
    for idx, e in enumerate(trace_list):
        cluster_probabilities_for_event = []
        for cluster in cluster_probabilities:
            cluster_probabilities_for_event.append(cluster[idx])
        activity_to_class[e][CLUSTERS] = cluster_probabilities_for_event
        if len([prob for prob in cluster_probabilities_for_event if prob > threshold]) == 1:
            cluster_with_high_probability = np.argmax(cluster_probabilities_for_event) + 1
            activity_to_class[e][RESULT] = cluster_with_high_probability
        else:
            activity_to_class[e][RESULT] = -1

    activity_to_class_lp = cca.apply(event_log, activity_to_class, po_graph_per_case, average_similarity_matrix)
    return activity_to_class_lp


def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]]):
    if parameters is None:
        parameters = {CLUSTER_COUNT: 3, METRIC: 'jensenshannon', THRESHOLD: 0.35}

    po_graphs_per_case, average_similarity_matrix = EventEncoding.apply(event_log)

    center, result, result0, d, jm, p, fpc = fuzz.cluster.cmeans(np.array(average_similarity_matrix).T, parameters[CLUSTER_COUNT], 2, error=0.005, maxiter=2000, init=None, metric=parameters[METRIC])

    trace_list = [event[DEFAULT_ACTIVITY_KEY] for case in event_log for event in case if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE]


    activity_to_class_lp = map_activities_to_classes(event_log, trace_list, result, parameters[THRESHOLD], po_graphs_per_case, average_similarity_matrix)

    return activity_to_class_lp