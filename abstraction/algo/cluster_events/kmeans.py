import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from collections import defaultdict
from sklearn.cluster import KMeans
from pm4py.objects.log.obj import EventLog
from typing import Any, Dict, List, Optional
from abstraction.algo import EventEncoding
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, CLUSTER_COUNT, ALGORITHM, START_LIFECYCLE_VALUE
import abstraction.algo.CCA as cca 


RESULT = 'result'


def map_activities_to_classes(trace_list: List, cluster_class: List):
    activity_to_class = defaultdict(dict)
    for idx, e in enumerate(trace_list):
        activity_to_class[e][RESULT] = cluster_class[idx] + 1

    activity_to_class_lp = cca.apply(activity_to_class)

    return activity_to_class_lp


def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]]):
    if parameters is None:
        parameters = {CLUSTER_COUNT: 3, ALGORITHM: 'lloyd'}

    po_graphs_per_case, average_similarity_matrix = EventEncoding.apply(event_log)

    kmeans = KMeans(n_clusters=parameters[CLUSTER_COUNT], algorithm=parameters[ALGORITHM]).fit(average_similarity_matrix)

    trace_list = [event[DEFAULT_ACTIVITY_KEY] for case in event_log for event in case if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE]

    activity_to_class_lp = map_activities_to_classes(trace_list, kmeans.labels_)

    return activity_to_class_lp