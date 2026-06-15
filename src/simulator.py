from model.graph import Graph
from model.drone import Drone
from model.zone import ZoneType
from pathfinder.pathfinder import Pathfinder
from pathfinder.reservation_table import ReservationTable


class Simulator:
    """Runs the drone routing simulation."""

    def __init__(self, graph: Graph, nb_drones: int,
                 pathfinder: Pathfinder) -> None:
        """Initialize simulator with graph, drone count and pathfinder.

        Args:
            graph: The parsed zone graph.
            nb_drones: Number of drones to simulate.
            pathfinder: The pathfinder instance to use.
        """
        self.graph = graph
        self.nb_drones = nb_drones
        self.pathfinder = pathfinder
        self.drones: list[Drone] = []
        self.turn = 0
        self.max_turns = 200
        self.simulation_steps: list[list[str]] = []

    def create_drones(self) -> None:
        """Plan collision-free paths for all drones
        using the reservation table."""
        start = self.graph.start_zone
        end = self.graph.end_zone
        table = ReservationTable()

        for i in range(self.nb_drones):
            drone = Drone(f"D{i + 1}", start)

            path_nodes = self.pathfinder.dijkstra(start, end, table)

            if not path_nodes:
                print(f"No path found for D{i + 1}")
                self.drones.append(drone)
                continue

            path_nodes = [node for node in path_nodes if node[0] != start.name]
            drone.planned_path = path_nodes
            drone.path_index = 0

            for j, (zone_name, turn) in enumerate(path_nodes):
                table.reserve_zone(zone_name, turn)
                if j < len(path_nodes) - 1:
                    next_zone_name, _ = path_nodes[j + 1]
                    if zone_name != next_zone_name:
                        table.reserve_edge(zone_name, next_zone_name, turn)
                        next_zone = self.graph.get_zone(next_zone_name)
                        if next_zone.zone_type == ZoneType.RESTRICTED:
                            table.reserve_edge(zone_name,
                                               next_zone_name, turn + 1)

            self.drones.append(drone)

    def run_simulator(self) -> None:
        """Execute the simulation by moving all drones
        along their planned paths."""
        end = self.graph.end_zone
        delivered: set[str] = set()
        self.turn = 0
        while len(delivered) < len(self.drones):
            self.turn += 1
            movements: list[str] = []
            for drone in self.drones:
                if drone.is_delivered:
                    continue
                path = drone.planned_path
                idx = drone.path_index
                while idx < len(path) and path[idx][1] < self.turn:
                    idx += 1
                drone.path_index = idx
                if idx >= len(path):
                    drone.is_delivered = True
                    delivered.add(drone.drone_id)
                    continue
                zone_name, target_turn = path[idx]
                if target_turn == self.turn:
                    if zone_name != drone.current_zone.name:
                        movements.append(f"{drone.drone_id}-{zone_name}")
                        drone.current_zone = self.graph.get_zone(zone_name)
                    if zone_name == end.name:
                        drone.is_delivered = True
                        delivered.add(drone.drone_id)
                    drone.path_index += 1
                elif target_turn == self.turn + 1:
                    next_zone = self.graph.get_zone(zone_name)
                    if (
                        next_zone.zone_type == ZoneType.RESTRICTED
                        and zone_name != drone.current_zone.name
                    ):
                        origin = drone.current_zone.name
                        movements.append(
                            f"{drone.drone_id}-{origin}-{zone_name}"
                        )
            if movements:
                self.simulation_steps.append(movements)
            if self.turn > self.max_turns:
                print("Turn limit reached")
                break

    def print_output(self) -> None:
        """Print simulation output and total turns to stdout."""
        for step in self.simulation_steps:
            print(" ".join(step))
        print(f"Total turns: {self.turn}")
