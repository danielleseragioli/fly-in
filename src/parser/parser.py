from model.graph import Graph
from model.zone import Zone, ZoneType
from model.edge import Edge
from typing import Optional


class Parser:

    def __init__(self, file_path: str):
        """Initialize the Parser with the input file path."""
        self.file_path = file_path

    def parse(self) -> tuple[Graph, int]:
        """Parse the input file and return a (Graph, int) tuple.

        The tuple typically contains the parsed graph and an integer value
        (e.g., number of drones or similar count).
        """
        with open(self.file_path) as file:
            zones: dict[str, Zone] = {}
            edges: list[Edge] = []
            start_zone: Optional[Zone] = None
            end_zone: Optional[Zone] = None
            nb_drones: int = 0
            nb_drones_seen: bool = False
            seen_connections: set[tuple[str, str]] = set()

            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if not nb_drones_seen:
                    if not line.startswith("nb_drones:"):
                        raise ValueError("First line must define nb_drones")
                    nb_drones_seen = True

                if line.startswith("nb_drones:"):
                    parts: list[str] = line.split(":")
                    nb_drones = int(parts[1].strip())

                elif line.startswith("start_hub:"):
                    _, part2 = line.split(":", 1)
                    zone = self._parse_zone(part2.strip())
                    start_zone = zone
                    zones[zone.name] = zone

                elif line.startswith("end_hub:"):
                    _, part2 = line.split(":", 1)
                    zone = self._parse_zone(part2.strip())
                    end_zone = zone
                    zones[zone.name] = zone

                elif line.startswith("hub:"):
                    _, data = line.split(":", 1)
                    zone = self._parse_zone(data.strip())
                    zones[zone.name] = zone

                elif line.startswith("connection:"):
                    _, data = line.split(":", 1)
                    edge = self._parse_connection(data.strip(), zones)
                    if edge:
                        edge_key = tuple(sorted([edge.zone_a.name, edge.zone_b.name]))
                        if edge_key in seen_connections:
                            raise ValueError(f"Duplicate connection: {line}")
                        seen_connections.add(edge_key)
                        edges.append(edge)

        if start_zone is None:
            raise ValueError("No start_hub defined")
        if end_zone is None:
            raise ValueError("No end_hub defined")

        return (Graph(zones, edges, start_zone, end_zone), nb_drones)

    def _parse_zone(self, line: str) -> Optional[Zone]:
        """Parse the content after a hub prefix into a Zone object.

        Args:
            line: The string after the hub prefix, e.g. "roof1 3 4 [zone=restricted color=red]"

        Returns:
            A Zone instance, or None if the line is empty.

        Example:
            Input:  "roof1 3 4 [zone=restricted color=red max_drones=2]"
            Output: Zone("roof1", (3, 4), ZoneType.RESTRICTED, 2, "red")
        """
        if not line:
            return None

        if "[" in line:
            part1, part2 = line.split("[", 1)
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        part1_split = part1.split()
        name = part1_split[0]
        x = int(part1_split[1])
        y = int(part1_split[2])

        try:
            zone_type = ZoneType(metadata.get("zone", "normal"))
        except ValueError:
            raise ValueError(f"Invalid zone type: {metadata.get('zone')}")

        color = metadata.get("color", "")
        max_drones = int(metadata.get("max_drones", "1"))

        return Zone(name, (x, y), zone_type, max_drones, color)

    def _parse_metadata(self, metadata_str: str) -> dict[str, str]:
        """Parse a metadata block string into a key-value dictionary.

        Args:
            metadata_str: A bracket-enclosed metadata string,
                          e.g. "[zone=restricted color=red max_drones=2]"

        Returns:
            A dict of key-value pairs, e.g. {"zone": "restricted", "color": "red"}
            Returns an empty dict if the input is empty.
        """
        if not metadata_str:
            return {}

        metadata_str = metadata_str.strip("[]")
        parts = metadata_str.split()
        res: dict[str, str] = {}
        for item in parts:
            key, value = item.split("=")
            res[key] = value

        return res

    def _parse_connection(self, line: str, zones: dict[str, Zone]) -> Optional[Edge]:
        """Parse the content after 'connection:' into an Edge object.

        Args:
            line: The string after 'connection:', e.g. "hub-roof1" or
                  "corridorA-tunnelB [max_link_capacity=2]"
            zones: Dict of already-parsed zones to look up by name.

        Returns:
            An Edge instance, or None if the line is empty.

        Example:
            Input:  "corridorA-tunnelB [max_link_capacity=2]"
            Output: Edge(zones["corridorA"], zones["tunnelB"], 2)
        """
        if not line:
            return None

        if "[" in line:
            part1, part2 = line.split("[", 1)
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        name_zone_a, name_zone_b = part1.strip().split("-")
        zone_a = zones.get(name_zone_a.strip())
        zone_b = zones.get(name_zone_b.strip())

        if zone_a is None or zone_b is None:
            raise ValueError(f"Unknown zone in connection: {line}")

        max_link_capacity = int(metadata.get("max_link_capacity", "1"))

        return Edge(zone_a, zone_b, max_link_capacity)