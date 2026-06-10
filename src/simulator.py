from parser import Parser
from drone import Drone
from pathfinder import Pathfinder
from reservation_table import ReservationTable


class Simulator:
    """Runs the drone routing simulation."""

    def __init__(self, input_file: str) -> None:
        """Initialize simulator from input file."""
        self.parser = Parser(input_file)
        self.graph, self.nb_drones = self.parser.parse()
        start = self.graph.start_zone
        self.drones = [Drone(f"D{i+1}", start) for i in range(self.nb_drones)]
        self.pathfinder = Pathfinder()
        self.turn = 0
        self.max_turns = 100

    def run(self) -> None:
        """Plan paths for all drones and execute the simulation turn by turn."""
        start = self.graph.start_zone
        end = self.graph.end_zone
        table = ReservationTable()

        for drone in self.drones:
            path_nodes = self.pathfinder.dijkstra(
                self.graph, start, end, table
            )

            if not path_nodes:
                print(f"❌ No path to {drone.drone_id}")
                return

            drone.planned_path = path_nodes
            drone.path_index = 0

            for i, (zone_name, turn) in enumerate(path_nodes):
                table.reserve_zone(zone_name, turn)
                if i < len(path_nodes) - 1:
                    next_zone_name, _ = path_nodes[i + 1]
                    if zone_name != next_zone_name:
                        table.reserve_edge(zone_name, next_zone_name, turn)

        delivered: set[str] = set()
        self.turn = 0

        while len(delivered) < len(self.drones):
            self.turn += 1
            movements = []

            for drone in self.drones:
                if drone.drone_id in delivered:
                    continue

                path = drone.planned_path

                while (
                    drone.path_index < len(path)
                    and path[drone.path_index][1] < self.turn
                ):
                    drone.path_index += 1

                if drone.path_index >= len(path):
                    delivered.add(drone.drone_id)
                    continue

                zone_name, target_turn = path[drone.path_index]

                if target_turn == self.turn:
                    if zone_name != drone.current_zone.name:
                        movements.append(f"{drone.drone_id}-{zone_name}")
                        drone.current_zone = self.graph.get_zone(zone_name)

                    if zone_name == end.name:
                        delivered.add(drone.drone_id)

                    drone.path_index += 1

            if movements:
                print(" ".join(movements))

            if self.turn > self.max_turns:
                print("❌ Shift limit reached")
                break

        print(f"\n✅ Simulation completed in {self.turn} turns")