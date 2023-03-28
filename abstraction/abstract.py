"""
Create an abstracted event log, and also create event logs for each classes,
and provide them as output
Allow for various inputs, especially for choice of clustering, and num of clusters if applicable.
Might have to implement a diff function in between for various clustering techniques.
"""
import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from abstraction.algo.constants import EPS, MIN_SAMPLES, EPSILON_VALUE, METRIC
from abstraction.algo import EventClustering, EventAbstraction
from pm4py.objects.log.importer.xes import importer as xes_importer



log_input_path = '../data/life/labour1.xes'
export_path = '../data/life/'

event_log = xes_importer.apply(log_input_path)

parameters = {EPS: EPSILON_VALUE, MIN_SAMPLES: 100, METRIC: 'precomputed'} # DBSCAN


EventAbstraction.apply(event_log, parameters, EventClustering.AlgorithmVariants.DBSCAN, export_path)