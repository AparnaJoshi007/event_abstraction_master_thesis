import sys
sys.path.append('/Users/aparnajoshi/thesis/fuzzy-event-abstraction')


import networkx as nx
from collections import defaultdict
from abstraction.algo.constants import DEFAULT_ACTIVITY_KEY, DEFAULT_TIMESTAMP_KEY, DEFAULT_LIFECYCLE_KEY, PRECEDING_WINDOW, START_LIFECYCLE_VALUE, SUCCEEDING_WINDOW


def is_overlapping(interval1, interval2):
    return interval1[0] <= interval2[1] and interval1[1] >= interval2[0]


def get_complete_event(start_ev, case):
    return [ev for ev in case if ev[DEFAULT_LIFECYCLE_KEY] == 'complete' and ev[DEFAULT_ACTIVITY_KEY].split('@')[0] == start_ev[DEFAULT_ACTIVITY_KEY].split('@')[0]][0]


def __get_succeeding_pattern(short_paths_list, po_graph, event, window_size):
    succeeding_patterns = list()

    for spl in short_paths_list:
        patterns = set()
        if event in spl:
            for sp in spl:
                if sp in list(nx.descendants(po_graph, event)):
                    if spl[sp] > spl[event] and spl[sp] <= spl[event] + window_size:
                        patterns.add(sp.split('@')[0])
        succeeding_patterns.append(patterns)

    return succeeding_patterns


def __get_preceding_pattern(short_paths_list, po_graph, event, window_size):
    preceding_patterns = list()

    for spl in short_paths_list:
        patterns = set()
        if event in spl:
            for sp in spl:
                if sp in list(nx.ancestors(po_graph, event)):
                    if spl[sp] < spl[event] and spl[sp] >= (spl[event] - window_size):
                        patterns.add(sp.split('@')[0])
        preceding_patterns.append(patterns)


    
    return preceding_patterns


def create_event_level_dict_serial(case):
    event_level_dicto = defaultdict(list)
    for ev in case:
        event_level_dicto[ev[DEFAULT_TIMESTAMP_KEY]].append(ev[DEFAULT_ACTIVITY_KEY])
    
    return event_level_dicto


def create_event_level_dict_parallel(case):
    event_level_dicto = defaultdict(dict)
    dict_idx = 0
    initial_start_event = case[0]
    initial_complete_event = get_complete_event(initial_start_event, case)
    event_timeframe = (initial_start_event[DEFAULT_TIMESTAMP_KEY], initial_complete_event[DEFAULT_TIMESTAMP_KEY])
    event_level_dicto[dict_idx] = {'timeframe': event_timeframe, 'activity_keys': [initial_complete_event[DEFAULT_ACTIVITY_KEY]] }
    for ev in case[1:]:
        if ev[DEFAULT_LIFECYCLE_KEY] == 'start':
            complete_event = get_complete_event(ev, case)
            for idx in event_level_dicto.keys():
                is_ol = is_overlapping(event_level_dicto[idx]['timeframe'], (ev[DEFAULT_TIMESTAMP_KEY], complete_event[DEFAULT_TIMESTAMP_KEY]))
                if is_ol:
                    min_start_time = min(event_level_dicto[idx]['timeframe'][0], ev[DEFAULT_TIMESTAMP_KEY])
                    max_complete_time = max(event_level_dicto[idx]['timeframe'][1], complete_event[DEFAULT_TIMESTAMP_KEY])
                    event_level_dicto[idx]['timeframe'] = (min_start_time, max_complete_time)
                    event_level_dicto[idx]['activity_keys'].append(complete_event[DEFAULT_ACTIVITY_KEY])
                    break
            else:
                dict_idx += 1
                event_timeframe = (ev[DEFAULT_TIMESTAMP_KEY], complete_event[DEFAULT_TIMESTAMP_KEY])
                event_level_dicto[dict_idx] = {'timeframe': event_timeframe, 'activity_keys': [complete_event[DEFAULT_ACTIVITY_KEY]] }

    return event_level_dicto


def process_event_dictionary(event_dicto):
    event_level_dicto = defaultdict(list)
    for idx in event_dicto.keys():
        event_level_dicto[idx] = event_dicto[idx]['activity_keys']
    
    return event_level_dicto


def is_reachable(v1, v2, edges_list):
    copied_edges_list = edges_list.copy()
    copied_edges_list.remove((v1,v2))
    source = v1
    target = v2
    edge_found = False
    for edge in copied_edges_list:
        if source == edge[0]:
            if target != edge[1]:
                source = edge[1]
            else: 
                edge_found = True
                break
    
    return edge_found

 
def create_po_graph_per_case(case):
    po_edges = list()
    sorted_case = sorted(case, key=lambda ev: ev[DEFAULT_TIMESTAMP_KEY])
    if any([ev[DEFAULT_LIFECYCLE_KEY] == 'start' for ev in sorted_case]):
        event_dicto = create_event_level_dict_parallel(sorted_case)
        event_level_dicto = process_event_dictionary(event_dicto)
    else:
        event_level_dicto = create_event_level_dict_serial(sorted_case)

    keys = [key for key in event_level_dicto.keys()]


    for idx, key in enumerate(keys[:-1]):
        events_at_same_level = event_level_dicto[key]
        events_at_next_level = event_level_dicto[keys[idx+1]]

        for event1 in events_at_same_level:
            for event2 in events_at_next_level:
                po_edges.append((event1, event2))


    for edge in po_edges.copy():
            if edge[0] == edge[1]:
                po_edges.remove(edge)
            elif is_reachable(edge[0], edge[1], po_edges):
                po_edges.remove(edge)


    if not po_edges:
        po_edges = event_level_dicto[keys[0]]
        po_graph = nx.DiGraph()
        po_graph.add_nodes_from(po_edges)
    
    else:
        po_graph = nx.DiGraph()
        po_graph.add_edges_from(po_edges)
    

    return po_graph, event_level_dicto[keys[0]], event_level_dicto[keys[-1]]


def get_patterns_list(case, po_graph, sa, ea, window_size, type):
    unique_events = list({ event[DEFAULT_ACTIVITY_KEY] for event in case if event[DEFAULT_LIFECYCLE_KEY] != START_LIFECYCLE_VALUE })

    short_paths_list = list()

    for a in sa:
        short_paths_list.append(dict(nx.shortest_path_length(po_graph, a)))

    pattern_dicto = defaultdict(dict)
    if type == 'p':
        for event in unique_events:
            pattern_dicto[event] = __get_preceding_pattern(short_paths_list, po_graph, event, window_size)
    
    elif type == 's':
        for event in unique_events:
             pattern_dicto[event] = __get_succeeding_pattern(short_paths_list, po_graph, event, window_size)

    return pattern_dicto


def apply(event_log):
    preceding_patterns = defaultdict(list)
    succeeding_patterns = defaultdict(list)
    po_graphs_per_case = dict()

    for case in event_log:
        po_graph, sa, ea  = create_po_graph_per_case(case)
        
        p_patterns = get_patterns_list(case, po_graph, sa, ea, PRECEDING_WINDOW, 'p')
        preceding_patterns.update(p_patterns)

        s_patterns = get_patterns_list(case, po_graph, sa, ea, SUCCEEDING_WINDOW, 's')
        succeeding_patterns.update(s_patterns)

        po_graphs_per_case[case.attributes['concept:name']] = po_graph

    return po_graphs_per_case, preceding_patterns, succeeding_patterns