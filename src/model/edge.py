from .zone import Zone
from .occupiable import Occupiable


class Edge(Occupiable):
    """Represents a connection between two zones with
    a drone capacity limit."""

    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int):
        """Create an edge linking two zones and set its capacity settings."""
        super().__init__(max_link_capacity)
        self.zone_a = zone_a
        self.zone_b = zone_b

    def can_receive_drone(self) -> bool:
        """Return whether the edge can accept one more drone."""
        return len(self.drones) < self.max_capacity
