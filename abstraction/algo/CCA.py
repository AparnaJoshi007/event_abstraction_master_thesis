from collections import defaultdict
import random


def get_preceding_events(po_graphs_per_case, event, caseid):
    po_graph_for_case = po_graphs_per_case[caseid]
    predecessors = po_graph_for_case.predecessors(event)
    return predecessors


def get_succeeding_events(po_graphs_per_case, event, caseid):
    po_graph_for_case = po_graphs_per_case[caseid]
    successors = po_graph_for_case.successors(event)
    return successors


def propagate_using_context(event, labels, average_similarity_matrix, event_to_pos_dict, pos_to_event_dict):
    unique_labels = list(set(labels.values()))
    position = event_to_pos_dict[event]
    avg_similarity_with_event = average_similarity_matrix[position]
    max_similarity = max(avg_similarity_with_event)
    classes_with_max_similarity = defaultdict(dict)
    for idx, similarity in enumerate(avg_similarity_with_event):
        if similarity == max_similarity:
            event_with_max_similarity = pos_to_event_dict[idx]
            class_with_max_similarity = labels[event_with_max_similarity]
            classes_with_max_similarity[class_with_max_similarity] += 1
    
    if len(classes_with_max_similarity.keys()) == 1:
        labels[event] = classes_with_max_similarity.keys()[0]
    elif len(max(classes_with_max_similarity, key=classes_with_max_similarity.get)) == 1:
        class_with_majority = max(classes_with_max_similarity, key=classes_with_max_similarity.get)
        labels[event] = class_with_majority
    else:
        labels[event] = random.choice(unique_labels)

    return labels


def apply(log, labels, po_graphs_per_case, average_similarity_matrix, event_to_pos_dict, pos_to_event_dict):
    for case in log:
        case_events = [e['concept:name'] for e in case]
        for event in labels:
            if event in case_events:
                if labels[event]['result'] == -1:
                    preceding_events = get_preceding_events(po_graphs_per_case, event, case.attributes['concept:name'])
                    succeeding_events = get_succeeding_events(po_graphs_per_case, event, case.attributes['concept:name'])
                    if (set(preceding_events) == set(succeeding_events)) and len(set(preceding_events)) == 1:
                        labels[event] = set(preceding_events)[0]
                    else:
                        labels = propagate_using_context(event, po_graphs_per_case, labels, average_similarity_matrix, event_to_pos_dict, pos_to_event_dict)

    return labels
