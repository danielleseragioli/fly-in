from model.graph import Graph
from model.zone import Zone, ZoneType
from .reservation_table import ReservationTable
import heapq


class Pathfinder:
    """Finds optimal paths through the graph using Dijkstra on a space-time graph."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the pathfinder with the graph."""
        self.graph = graph

    def dijkstra(
        self,
        start_zone: Zone,
        end_zone: Zone,
        reservation_table: ReservationTable,
        start_turn: int = 0,
        ) -> list[tuple[str, int]]:
        """Find shortest path from start to end using space-time Dijkstra.

        Returns a list of (zone_name, turn) tuples representing the planned path.
        Restricted zones cost 2 turns to enter; all others cost 1.
        """
        MAX_TURN = 200
        distances: dict[tuple[str, int], float] = {}
        previous: dict[tuple[str, int], tuple[str, int] | None] = {}
        visited: set[tuple[str, int]] = set()

        node_start = (start_zone.name, start_turn)
        distances[node_start] = 0
        previous[node_start] = None

        counter: int = 0
        heap: list[tuple[float, int, int, str, int]] = [(0.0, 0, 0, start_zone.name, start_turn)]

        while heap:
            d, _, _, curr_zone_name, curr_turn = heapq.heappop(heap)
            current = (curr_zone_name, curr_turn)

            if current in visited:
                continue
            visited.add(current)


            if curr_zone_name == end_zone.name:
                break

            if curr_turn >= MAX_TURN:
                continue

            curr_zone = self.graph.get_zone(curr_zone_name)
            curr_dist = d

            for neighbor in self.graph.get_neighbors(curr_zone):
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue

                weight = 2 if neighbor.zone_type == ZoneType.RESTRICTED else 1
                next_turn = curr_turn + weight

                if next_turn > MAX_TURN:
                    continue

                edge = self.graph.get_edge(curr_zone, neighbor)

                if edge:
                    if not reservation_table.is_edge_available(
                        curr_zone_name, neighbor.name, curr_turn, edge.max_capacity
                    ):
                        continue

                if (
                    neighbor.name != end_zone.name
                    and neighbor.name != start_zone.name
                ):
                    if neighbor.zone_type == ZoneType.RESTRICTED:
                        ok = all(
                            reservation_table.is_zone_available(
                                neighbor.name, t, neighbor.max_capacity
                            )
                            for t in range(curr_turn + 1, next_turn + 1)
                        )
                    else:
                        ok = reservation_table.is_zone_available(
                            neighbor.name, next_turn, neighbor.max_capacity
                        )
                    if not ok:
                        continue

                next_node = (neighbor.name, next_turn)
                new_dist = curr_dist + weight

                if new_dist < distances.get(next_node, float('inf')):
                    distances[next_node] = new_dist
                    previous[next_node] = current
                    counter += 1
                    priority_bonus = -1 if neighbor.zone_type == ZoneType.PRIORITY else 0
                    heapq.heappush(heap, (new_dist, priority_bonus, counter, neighbor.name, next_turn))

            wait_turn = curr_turn + 1
            if wait_turn <= MAX_TURN:
                can_wait = (
                    curr_zone_name == start_zone.name
                    or reservation_table.is_zone_available(
                        curr_zone_name, wait_turn, curr_zone.max_capacity
                    )
                )
                if can_wait:
                    wait_node = (curr_zone_name, wait_turn)
                    wait_dist = curr_dist + 1
                    if wait_dist < distances.get(wait_node, float('inf')):
                        distances[wait_node] = wait_dist
                        previous[wait_node] = current
                        counter += 1
                        heapq.heappush(heap, (wait_dist, 0, counter, curr_zone_name, wait_turn))

        end_nodes = [
            (n, d) for n, d in distances.items()
            if n[0] == end_zone.name and n in visited
        ]

        if not end_nodes:
            return []

        end_node = min(end_nodes, key=lambda x: x[1])[0]

        path: list[tuple[str, int]] = []
        curr_node: tuple[str, int] | None = end_node
        while curr_node is not None:
            path.insert(0, curr_node)
            curr_node = previous.get(curr_node)

        return path