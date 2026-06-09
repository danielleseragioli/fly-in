from graph import Graph
from zone import Zone, ZoneType
from reservation_table import ReservationTable


class Pathfinder:

    def __init__(self):
        pass

    def dijkstra(self, graph: Graph, start_zone: Zone, end_zone: Zone, reservation_table: ReservationTable):

        MAX_TURN = 45
        start_turn = 0
        distances = {}
        previous = {}
        visited = set()

        node_inicial = (start_zone.name, start_turn)
        distances[node_inicial] = 0
        previous[node_inicial] = None

        for zone in graph.zones.values():
            for turn in range(0, MAX_TURN + 1):
                node = (zone.name, turn)
                if node != node_inicial:
                    distances[node] = float('inf')

        while len(visited) < len(distances):
            current = None
            min_distance = float('inf')

            for node in distances:
                if node in visited:
                    continue
                if distances[node] < min_distance:
                    min_distance = distances[node]
                    current = node

            if current is None:
                break

            curr_zone_name, curr_turn = current
            
            if curr_zone_name == end_zone.name:
                break

            visited.add(current)
            curr_zone = graph.get_zone(curr_zone_name)

            for neighbor in graph.get_neighbors(curr_zone):
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue


                if neighbor.zone_type == ZoneType.RESTRICTED:
                    weight = 2  
                else:
                    weight = 1  
                
                next_turn = curr_turn + weight

                if next_turn > MAX_TURN:
                    continue

                edge = graph.get_edge(curr_zone, neighbor)
                if edge:
                    if neighbor.name != end_zone.name:
                        if not reservation_table.is_edge_available(curr_zone.name, neighbor.name, curr_turn, edge.max_capacity):
                            continue

                if neighbor.name != end_zone.name and neighbor.name != start_zone.name:
                    if not reservation_table.is_zone_available(neighbor.name, next_turn, neighbor.max_capacity):
                        continue

                next_node = (neighbor.name, next_turn)
                new_distance = distances[current] + weight

                if new_distance < distances[next_node]:
                    distances[next_node] = new_distance
                    previous[next_node] = current

            if curr_turn < MAX_TURN:
                if curr_zone_name == start_zone.name or reservation_table.is_zone_available(curr_zone_name, curr_turn + 1, curr_zone.max_capacity):
                    wait_node = (curr_zone_name, curr_turn + 1)
                    wait_distance = distances[current] + 1
            
                    if wait_distance < distances[wait_node]:
                        distances[wait_node] = wait_distance
                        previous[wait_node] = current

        if current is None or distances[current] == float('inf'):
            return []

        path_nodes = []
        curr_node = current

        while curr_node is not None:
            path_nodes.insert(0, curr_node)
            curr_node = previous.get(curr_node)

        return path_nodes