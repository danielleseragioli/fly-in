from zone import Zone
from occupiable import Occupiable


class Edge(Occupiable):
    """Represents a connection between two zones with a drone capacity limit."""

    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int):
        """Create an edge linking two zones and set its capacity settings."""

        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.current_drones = 0


    def can_receive_drone(self) -> bool:
        """Return whether the edge can accept one more drone."""

        return self.current_drones < self.max_link_capacity
