import numpy as np
from math import gcd, log
from functools import reduce

def list_gcd(numbers):
    """Compute GCD of a list of numbers."""
    return reduce(gcd, numbers)

def cluster_customers(distances, L):
    """Clusters customers based on distance to the depot."""
    depot_distances = distances[0]
    max_distance = max(depot_distances[1:])
    cluster_labels = {}

    for i, dist in enumerate(depot_distances):
        if i == 0:
            continue
        cluster = int((dist / max_distance) * L) + 1
        cluster_labels[i] = min(cluster, L)

    return cluster_labels

def generate_splitting_rules(gcd_value, s_max, L, vehicle_capacity):
    """Generates demand splitting rules based on GCD and vehicle capacity."""
    rules = {}
    for level in range(1, L + 1):
        splitting_rule = []
        for i in range(s_max, -1, -1):
            portion = gcd_value * (2 ** i)
            if portion <= vehicle_capacity:
                splitting_rule.append(portion)
        rules[level] = splitting_rule
    return rules

def split_demand(demand, splitting_rule):
    """Splits demand based on the largest-first strategy."""
    splits = []
    remaining_demand = demand
    for portion in splitting_rule:
        while remaining_demand >= portion:
            splits.append(portion)
            remaining_demand -= portion
    return splits

def update_graph(distances, demands, vehicle_capacity, num_vehicles):
    """Processes PASA algorithm to adjust demands and distance matrix."""
    n_customers = len(demands) - 1
    gcd_value = list_gcd(demands[1:] + [vehicle_capacity])
    avg_demand = sum(demands[1:]) / n_customers
    s_max = int(log(avg_demand / gcd_value, 2)) + 1
    L = max(3, int(np.sqrt(n_customers)))

    cluster_labels = cluster_customers(distances, L)
    splitting_rules = generate_splitting_rules(gcd_value, s_max, L, vehicle_capacity)

    updated_demands = []
    split_mapping = {}
    new_indices = {}
    current_index = 0

    for customer, demand in enumerate(demands):
        if customer == 0:
            updated_demands.append(demand)
            new_indices[customer] = [current_index]
            current_index += 1
            continue

        cluster = cluster_labels[customer]
        splitting_rule = splitting_rules[cluster]
        splits = split_demand(demand, splitting_rule)

        split_mapping[customer] = []
        for split in splits:
            updated_demands.append(split)
            split_mapping[customer].append(current_index)
            current_index += 1

        new_indices[customer] = split_mapping[customer]

    n_original = len(distances)
    n_new = len(updated_demands)
    updated_distances = np.zeros((n_new, n_new), dtype=int)

    for i in range(n_original):
        for j in range(n_original):
            for new_i in new_indices[i]:
                for new_j in new_indices[j]:
                    updated_distances[new_i][new_j] = int(distances[i][j])

    vehicle_capacities = [vehicle_capacity] * num_vehicles  # Create vehicle capacity list

    return updated_distances.tolist(), [int(d) for d in updated_demands], vehicle_capacities

