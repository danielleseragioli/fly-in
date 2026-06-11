from parser import Parser
from model.drone import Drone
from pathfinder import Pathfinder
from pathfinder.reservation_table import ReservationTable


class Simulator:
    """Runs the drone routing simulation."""

    def __init__(self, input_file: str) -> None:
        """Initialize simulator from input file.

        Args:
            input_file: Path to the map input file.
        """
        self.parser = Parser(input_file)
        self.graph, self.nb_drones = self.parser.parse()
        start = self.graph.start_zone
        self.drones = [Drone(f"D{i + 1}", start) for i in range(self.nb_drones)]
        self.pathfinder = Pathfinder()
        self.turn = 0
        self.max_turns = 200

    def run(self, visualize: bool = False) -> None:
        """Plan paths for all drones and execute the simulation turn by turn.

        Args:
            visualize: If True, opens the pygame visualizer after running.
        """
        start = self.graph.start_zone
        end = self.graph.end_zone
        table = ReservationTable()

        for drone in self.drones:
            path_nodes = self.pathfinder.dijkstra(
                self.graph, start, end, table
            )
            if not path_nodes:
                print(f"No path found for {drone.drone_id}")
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
        simulation_steps: list[list[str]] = []

        while len(delivered) < len(self.drones):
            self.turn += 1
            movements: list[str] = []

            for drone in self.drones:
                if drone.drone_id in delivered:
                    continue

                path = drone.planned_path
                idx = drone.path_index

                
                while (
                    idx < len(path)
                    and path[idx][1] < self.turn
                ):
                    idx += 1
                drone.path_index = idx

                if idx >= len(path):
                    delivered.add(drone.drone_id)
                    continue

                zone_name, target_turn = path[idx]

                if target_turn == self.turn:
                    if zone_name != drone.current_zone.name:
                        movements.append(f"{drone.drone_id}-{zone_name}")
                        drone.current_zone = self.graph.get_zone(zone_name)

                    if zone_name == end.name:
                        delivered.add(drone.drone_id)

                    drone.path_index += 1

                elif target_turn == self.turn + 1:
                    pass

                else:
                    if idx > 0:
                        prev_zone_name, prev_turn = path[idx - 1]
                        hop_cost = target_turn - prev_turn
                        if hop_cost == 2 and self.turn == prev_turn + 1:
                            conn_label = f"{prev_zone_name}-{zone_name}"
                            movements.append(f"{drone.drone_id}-{conn_label}")

            if movements:
                print(" ".join(movements))
                simulation_steps.append(movements)

            if self.turn > self.max_turns:
                print("Turn limit reached")
                break

        print(f"\nSimulation completed in {self.turn} turns")

        if visualize:
            from visualizer.visualizer import Visualizer
            viz = Visualizer(self.graph, simulation_steps)
            viz.run()