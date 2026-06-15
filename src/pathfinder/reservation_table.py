class ReservationTable:
    """Track zone and edge reservations by turn."""

    def __init__(self) -> None:
        """Initialize empty reservation stores."""
        self.zone_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[tuple[str, str], int], int] = {}

    def is_zone_available(self, zone_name: str, turn: int,
                          max_capacity: int) -> bool:
        """Return whether a zone has free capacity at a given turn."""
        curr_occupation = self.zone_reservations.get((zone_name, turn), 0)
        return curr_occupation < max_capacity

    def is_edge_available(self, zname_a: str, zname_b: str, turn: int,
                          max_capacity: int) -> bool:
        """Return whether an edge has free capacity at a given turn."""
        if zname_a < zname_b:
            edge_key: tuple[str, str] = (zname_a, zname_b)
        else:
            edge_key = (zname_b, zname_a)
        curr_reservation = self.edge_reservations.get((edge_key, turn), 0)
        return curr_reservation < max_capacity

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """Reserve one slot in a zone for a turn."""
        curr_occupation = self.zone_reservations.get((zone_name, turn), 0)
        self.zone_reservations[(zone_name, turn)] = curr_occupation + 1

    def reserve_edge(self, zona_a: str, zona_b: str, turn: int) -> None:
        """Reserve one slot on an edge for a turn."""
        if zona_a < zona_b:
            edge_key: tuple[str, str] = (zona_a, zona_b)
        else:
            edge_key = (zona_b, zona_a)
        curr_occupation = self.edge_reservations.get((edge_key, turn), 0)
        self.edge_reservations[(edge_key, turn)] = curr_occupation + 1
