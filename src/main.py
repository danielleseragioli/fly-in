import sys
from simulator import Simulator

def main() -> None:
    """Run the simulator entrypoint."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file> [--visual]")
        sys.exit(1)

    visualize = "--visual" in sys.argv
    simu = Simulator(sys.argv[1])
    simu.run(visualize=visualize)


if __name__ == "__main__":
    main()
