import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from enum import Enum
from pm4py.objects.log.obj import EventLog
from typing import Any, Dict, Optional
from abstraction.algo.cluster_events import cmeans, hdbscan, kmeans, dbscan, agglomerative, optics


class AlgorithmVariants(Enum):
    CMEANS = cmeans
    KMEANS = kmeans
    DBSCAN = dbscan
    AGGLOMERATIVE = agglomerative
    OPTICS = optics
    HDBSCAN = hdbscan


CMEANS = AlgorithmVariants.CMEANS
KMEANS = AlgorithmVariants.KMEANS
DBSCAN = AlgorithmVariants.DBSCAN
AGGLOMERATIVE = AlgorithmVariants.AGGLOMERATIVE
OPTICS = AlgorithmVariants.OPTICS
HDBSCAN = AlgorithmVariants.HDBSCAN


DEFAULT_VARIANT = CMEANS


def get_variant(variant):
    if isinstance(variant, Enum):
        return variant.value
    return variant


def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]], algorithm_variant: str = DEFAULT_VARIANT):
    activity_to_class_lp = get_variant(algorithm_variant).apply(event_log, parameters)

    return activity_to_class_lp