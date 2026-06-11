"""Module for managing drone entities and their movement through zones."""

from .zone import Zone
from .edge import Edge
from typing import Optional


class Drone:
    """Represents a drone that moves between zones and edges."""
    def __init__(self, drone_id: str, start_zone: Zone):
        """Initialize a drone with ID and starting zone."""
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.target_zone: Optional[Zone] = None
        self.is_in_transit: bool = False
        self.arrival_turn: Optional[int] = None
        self.is_delivered: bool = False

    def move_to_zone(self, dest_zone: Zone) -> bool:
        """Move drone to destination zone if capacity allows."""
        if not dest_zone.can_receive_drone():
            return False
        else:
            self.current_zone.remove_drone(self)
            dest_zone.add_drone(self)
            self.current_zone = dest_zone
            return True

    def start_transit_restricted(self, dest_zone: Zone, edge: Edge,
                                 current_turn: int) -> bool:
        """Start transit along edge (2 turns to arrival)."""
        if not edge.can_receive_drone():
            return False
        else:
            self.current_zone.remove_drone(self)
            edge.add_drone(self)
            self.target_zone = dest_zone
            self.arrival_turn = current_turn + 2
            self.is_in_transit = True
            return True

    def deliver(self) -> None:
        """Mark drone as delivered and reset transit state."""
        self.is_delivered = True
        self.is_in_transit = False
        self.target_zone = None
        self.arrival_turn = None
