import sys
from simulator import Simulator

if __name__ == "__main__":
    simu = Simulator(sys.argv[1])
    simu.run()
