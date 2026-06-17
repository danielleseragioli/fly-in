*This project has been created as part of the 42 curriculum by dseragio*

# Fly-in

## Description

Fly-in is a drone routing simulation project developed in Python. The goal is to transport multiple drones from a starting hub to a destination hub while respecting movement costs, zone capacities, connection capacities, and collision constraints.

The simulation models a network of connected zones represented as a graph. Each drone must reach the destination using an optimized route while avoiding conflicts with other drones. The project includes:

* A custom graph implementation.
* A parser for the subject map format.
* A pathfinding system based on a space-time Dijkstra algorithm.
* A reservation system for conflict avoidance.
* A simulation engine.
* A graphical visualizer built with Pygame.

The objective is to minimize the total number of simulation turns while ensuring that all movement and occupancy rules are respected.

---

# Features

* Object-oriented architecture.
* Complete parser with validation and error handling.
* Support for all zone types:

  * Normal
  * Restricted
  * Priority
  * Blocked
* Support for zone capacities (`max_drones`).
* Support for connection capacities (`max_link_capacity`).
* Collision-free route planning.
* Strategic waiting when movement is not possible.
* Graphical simulation visualization using Pygame.
* Fully typed Python code with docstrings.

---

# Project Structure

```text
.
├── main.py
├── simulator.py
├── parser/
│   └── parser.py
├── model/
│   ├── graph.py
│   ├── zone.py
│   ├── edge.py
│   ├── drone.py
│   └── occupiable.py
├── pathfinder/
│   ├── pathfinder.py
│   └── reservation_table.py
├── visualizer/
│   └── visualizer.py
└── assets/
```

---

# Algorithm Design

## Graph Representation

The map is represented as an undirected graph:

* Nodes represent zones.
* Edges represent valid drone connections.
* Each node stores:

  * Coordinates
  * Zone type
  * Capacity
  * Color

The graph maintains an adjacency list to efficiently retrieve neighboring zones.

---

## Space-Time Dijkstra

Instead of using a traditional graph search, the project uses a **space-time graph**.

Each state is represented as:

```text
(zone_name, turn)
```

Example:

```text
(corridorA, 4)
```

means the drone is located in `corridorA` during turn 4.

This allows path planning while considering:

* Future occupancy.
* Waiting actions.
* Capacity constraints.
* Simultaneous drone movement.

### Movement Costs

| Zone Type  | Cost           |
| ---------- | -------------- |
| Normal     | 1              |
| Priority   | 1              |
| Restricted | 2              |
| Blocked    | Not accessible |

Priority zones are favored during tie-breaking in the priority queue.

---

## Reservation Table

To avoid collisions, every planned movement reserves future resources before the next drone is routed.

The reservation table stores:

### Zone reservations

```python
(zone_name, turn)
```

Example:

```text
(roof1, 5)
```

meaning a drone occupies `roof1` during turn 5.

### Edge reservations

```python
((zoneA, zoneB), turn)
```

Example:

```text
((roof1, roof2), 4)
```

meaning the connection is used during turn 4.

Before moving into a zone or traversing a connection, the pathfinder verifies that capacity limits are respected.

---

## Multi-Drone Scheduling

Drones are routed sequentially:

1. Route Drone 1.
2. Reserve its entire path.
3. Route Drone 2 considering existing reservations.
4. Reserve its path.
5. Continue until all drones are planned.

This guarantees conflict-free paths without requiring path recalculation during simulation.

---

## Waiting Strategy

When no movement is possible, the algorithm may create a waiting action:

```text
(zone, turn + 1)
```

Waiting is treated as a valid state transition.

This allows drones to:

* Avoid congestion.
* Respect capacities.
* Prevent deadlocks.

---

# Simulation Engine

The simulator executes all planned paths turn by turn.

For each turn:

1. Every drone checks its next scheduled action.
2. Drones move only when their planned turn is reached.
3. Delivered drones are removed from active simulation.
4. Movements are recorded.

Output example:

```text
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

The simulation ends when every drone reaches the destination hub.
---

# Visual Representation

The project includes a graphical visualizer built with Pygame.

## Displayed Elements

* Graph nodes (zones)
* Connections (edges)
* Drone positions
* Start hub
* End hub
* Zone type colors
* Active connections

## Zone Colors

| Type       | Color  |
| ---------- | ------ |
| Normal     | Brown  |
| Restricted | Orange |
| Priority   | Green  |
| Blocked    | Pink   |

## Controls

| Key   | Action             |
| ----- | ------------------ |
| SPACE | Next turn          |
| A     | Toggle autoplay    |
| R     | Restart simulation |
| Q     | Quit               |
| ESC   | Quit               |

## User Experience Benefits

The visualizer provides:

* Real-time observation of drone movement.
* Easier debugging of routing decisions.
* Better understanding of congestion and capacities.
* Visual verification of collision avoidance.
* Clear distinction between zone types.

---

# Instructions

## Requirements

Python 3.10+

Install dependencies:

```bash
pip install pygame
```

---

## Run Simulation

```bash
python main.py maps/map.txt
```

---

## Run With Visualizer

```bash
python main.py maps/map.txt --visual
```

---

## Example Map Format

```text
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]

hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]

connection: hub-roof1
connection: roof1-roof2
connection: roof2-goal
```

---

# Complexity Analysis

Let:

* V = number of zones
* E = number of connections
* T = maximum simulated turns

The space-time graph contains approximately:

```text
V × T
```

states.

The Dijkstra complexity becomes:

```text
O((V × T + E × T) log(V × T))
```

Memory complexity:

```text
O(V × T)
```

for distance tracking, previous nodes, and reservations.

---

# Resources

## Documentation

* https://docs.python.org/3/
* https://docs.python.org/3/library/heapq.html
* https://docs.python.org/3/library/typing.html
* https://www.pygame.org/docs/

## Algorithms

* Dijkstra's Algorithm
* Space-Time Pathfinding
* Multi-Agent Path Finding (MAPF)

Recommended reading:

* https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* https://en.wikipedia.org/wiki/Multi-agent_pathfinding

## AI Usage

Artificial Intelligence tools were used during the development of this project for:

* Reviewing algorithmic approaches.
* Discussing pathfinding strategies.
* Improving documentation quality.
* Generating explanations for technical concepts.
* Verifying code readability and structure.

All generated suggestions were manually reviewed, understood, and adapted before being integrated into the project.

---

# Author

dseragio
