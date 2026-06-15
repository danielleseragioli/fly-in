from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drone import Drone


class Occupiable(ABC):
    """Abstract base class for entities that can hold drones."""

    def __init__(self, max_capacity: int) -> None:
        """Initialize capacity limits and the internal drone list."""
        self.max_capacity = max_capacity
        self.drones: list[Drone] = []

    @abstractmethod
    def can_receive_drone(self) -> bool:
        """Return whether this object can currently receive one more drone."""
        pass

    def add_drone(self, current_drone: Drone) -> bool:
        """Add a drone when capacity rules allow it."""
        if not self.can_receive_drone():
            return False
        else:
            self.drones.append(current_drone)
            return True

    def remove_drone(self, current_drone: Drone) -> bool:
        """Remove a drone if it is currently stored in this object."""
        if current_drone not in self.drones:
            return False
        else:
            self.drones.remove(current_drone)
            return True
