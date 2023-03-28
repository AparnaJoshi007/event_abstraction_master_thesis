import sys
from xml.dom.pulldom import START_DOCUMENT
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from collections import defaultdict
from sklearn.cluster import OPTICS
from pm4py.objects.log.obj import EventLog
from typing import Any, Dict, List, Optional
from abstraction.algo import EventEncoding
from abstraction.algo.constants import CLUSTERS, DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, DEFAULT_LIFECYCLE_VALUE, MIN_SAMPLES, METRIC, START_LIFECYCLE_VALUE
import abstraction.algo.CCA as cca 


RESULT = 'result'


def map_activities_to_classes(trace_list: List, cluster_class: List, cluster_encoding):
    activity_to_class = defaultdict(dict)
    for idx, e in enumerate(trace_list):
        activity_to_class[e][RESULT] = cluster_class[idx] + 1

    activity_to_class_lp = cca.apply(activity_to_class)

    return activity_to_class_lp




def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]]):
    if parameters is None:
        parameters = {MIN_SAMPLES: 3, METRIC: 'chebyshev'}

    po_graphs_per_case, average_similarity_matrix = EventEncoding.apply(event_log)

    optics = OPTICS(min_samples=parameters[MIN_SAMPLES], metric=parameters[METRIC]).fit(average_similarity_matrix)

    trace_list = [event[DEFAULT_ACTIVITY_KEY] for case in event_log for event in case if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE]

    activity_to_class_lp = map_activities_to_classes(trace_list, optics.labels_, average_similarity_matrix)

    return activity_to_class_lp