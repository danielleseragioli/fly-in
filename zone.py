from __future__ import annotations
from enum import Enum
from occupiable import Occupiable


class ZoneType(Enum):
    """Defines the possible types of zones in the simulation."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone(Occupiable):
    """Represents a zone with capacity limits and drone access rules."""

    def __init__(self, name: str, coord: tuple[int, int],
                 zone_type: ZoneType, max_drones: int,
                 color: str):
        """Create a zone with its identifying data and capacity settings."""
        super().__init__(max_drones)
        self.name = name
        self.coord = coord
        self.zone_type = zone_type
        self.color = color

    def can_receive_drone(self) -> bool:
        """Return whether the zone can accept one more drone."""
        return (
            self.zone_type != ZoneType.BLOCKED
            and super().can_receive_drone()
        )

    def is_blocked(self) -> bool:
        """Verify is the zone is blocked"""
        return self.zone_type == ZoneType.BLOCKED

    def is_restricted(self) -> bool:
        """Verify is the zone is restricted"""
        return self.zone_type == ZoneType.RESTRICTED

    def is_priority(self) -> bool:
        """Verify is the zone is priority"""
        return self.zone_type == ZoneType.PRIORITY
