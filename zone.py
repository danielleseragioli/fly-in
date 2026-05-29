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

        self.name = name
        self.coord = coord
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.current_drones = 0

    def can_receive_drone(self) -> bool:
        """Return whether the zone can accept one more drone."""

        if self.zone_type == ZoneType.BLOCKED:
            return False
        elif self.current_drones < self.max_drones:
            return True
        else:
            return False
