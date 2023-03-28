import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')

from operator import itemgetter
from typing import DefaultDict, Any, Dict, Optional
from pm4py.objects.log.obj import EventLog, Event, Trace
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_LIFECYCLE_KEY, START_LIFECYCLE_VALUE
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.filtering.log.attributes import attributes_filter
from abstraction.algo import EventClustering


def merge_subsequent_events(event_log: EventLog):
    instance_id = 0
    merged_log = []
    for case in event_log:
        class_array = dict()
        event_array = []
        for event in case:
            if event['concept:name'] not in class_array:
                class_array[event['concept:name']] = dict()
                class_array[event['concept:name']]['min'] = event['time:timestamp']
                class_array[event['concept:name']]['max'] = event['time:timestamp']
            else:
                if event['time:timestamp'] < class_array[event['concept:name']]['min']:
                    class_array[event['concept:name']]['min'] = event['time:timestamp']
                if event['time:timestamp'] > class_array[event['concept:name']]['max']:
                    class_array[event['concept:name']]['max'] = event['time:timestamp']
        
        for class_name in class_array:
            event_array.append({
                'concept:name': class_name,
                'lifecycle:transition': 'start',
                'time:timestamp': class_array[class_name]['min'],
                'concept:instance': instance_id
            })
            event_array.append({
                'concept:name': class_name,
                'lifecycle:transition': 'complete',
                'time:timestamp': class_array[class_name]['max'],
                'concept:instance': instance_id
            })
            instance_id += 1
        
        merged_log.append(Trace(event_array, attributes=case.attributes))

    return EventLog(merged_log)


def get_start_event(complete_ev, case, cluster):
    # for idx, ev in enumerate(case):
    #     print(complete_ev)
    #     print(idx, ev[DEFAULT_ACTIVITY_KEY])
    # start_event = [ev for ev in case if ev[DEFAULT_LIFECYCLE_KEY] == 'start' and ev[DEFAULT_CONCEPT_INSTANCE_KEY] == complete_ev[DEFAULT_CONCEPT_INSTANCE_KEY]][0]
    start_event = [ev for ev in case if ev[DEFAULT_LIFECYCLE_KEY] == 'start' and ev[DEFAULT_ACTIVITY_KEY].split('@')[0] == complete_ev['abstracted_event'].split('@')[0]][0]
    start_event['abstracted_event'] = start_event[DEFAULT_ACTIVITY_KEY]
    start_event[DEFAULT_ACTIVITY_KEY] = 'C' + str(cluster)
    return start_event


def create_event_at_cluster_level(event: Event, cluster: int):
    new_event = event
    new_event['abstracted_event'] = event[DEFAULT_ACTIVITY_KEY]
    new_event[DEFAULT_ACTIVITY_KEY] = 'C' + str(cluster)
    return new_event


def assign_abstract_classes(event_log: EventLog, activity_to_class_lp: DefaultDict):
    abstracted_log = []
    for case in event_log:
        abstracted_events = []
        for event in case:
            if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE:
                cluster = activity_to_class_lp[event[DEFAULT_ACTIVITY_KEY]]['result']
                new_event_complete = create_event_at_cluster_level(event, cluster)
                new_event_start = get_start_event(new_event_complete, case,  cluster)
                abstracted_events.append(new_event_start)
                abstracted_events.append(new_event_complete)
                sorted_abstracted_events = sorted(abstracted_events, key=itemgetter('time:timestamp'))
        abstracted_log.append(Trace(sorted_abstracted_events, attributes=case.attributes))
    
    return EventLog(abstracted_log)


def generate_flattened_logs_per_class(abstracted_log, export_path):
    abstracted_classes = list({event[DEFAULT_ACTIVITY_KEY] for case in abstracted_log for event in case})
    for class_name in abstracted_classes:
        filtered_log = attributes_filter.apply_events(abstracted_log, [class_name],
                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: DEFAULT_ACTIVITY_KEY, attributes_filter.Parameters.POSITIVE: True})
                                        
        for case in filtered_log:
            for event in case:
                event['abstracted_class'] = event[DEFAULT_ACTIVITY_KEY]
                event[DEFAULT_ACTIVITY_KEY] = event['abstracted_event'].split('@')[0]
                del event['abstracted_event']

        print("Class log obtained : ", class_name)
        xes_exporter.apply(filtered_log, export_path + 'e_filtered_log_'+class_name+'.xes')


def apply(event_log: EventLog, parameters: Optional[Dict[Any, Any]], algorithm_variant: str, export_path: str):
    activity_to_class_lp = EventClustering.apply(event_log, parameters, algorithm_variant)

    abstracted_log = assign_abstract_classes(event_log, activity_to_class_lp)
    xes_exporter.apply(abstracted_log, export_path + 'e_abstracted.xes')

    generate_flattened_logs_per_class(abstracted_log, export_path)

    abstracted_merged_log = merge_subsequent_events(abstracted_log)

    print("Abstracted log obtained.")
    xes_exporter.apply(abstracted_merged_log, export_path+'e_abstracted_merged.xes')