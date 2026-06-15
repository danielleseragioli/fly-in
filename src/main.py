import sys
from parser.parser import Parser
from pathfinder.pathfinder import Pathfinder
from simulator import Simulator


def main() -> None:
    """Run the simulator entrypoint."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file> [--visual]")
        sys.exit(1)

    file_path: str = sys.argv[1]

    parser = Parser(file_path)
    graph, nb_drones = parser.parse()
    pathfinder = Pathfinder(graph)
    simulator = Simulator(graph, nb_drones, pathfinder)
    simulator.create_drones()
    simulator.run_simulator()
    simulator.print_output()

    if "--visual" in sys.argv:
        from visualizer.visualizer import Visualizer
        viz = Visualizer(graph, simulator.simulation_steps)
        viz.run()


if __name__ == "__main__":
    main()
