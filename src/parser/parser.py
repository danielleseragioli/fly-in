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

            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.startswith("nb_drones:"):
                    if nb_drones_seen:
                        raise ValueError(f"Line {line_number}: duplicate"
                                         + "nb_drones definition")
                    nb_drones_seen = True
                    parts: list[str] = line.split(":", 1)
                    if len(parts) != 2:
                        raise ValueError(f"Line {line_number}: invalid"
                                         + "nb_drones format")
                    try:
                        nb_drones = int(parts[1].strip())
                    except ValueError:
                        raise ValueError(f"Line {line_number}: invalid"
                                         + "nb_drones value")
                    if nb_drones <= 0:
                        raise ValueError(f"Line {line_number}: nb_drones"
                                         + "must be positive")

                elif line.startswith("start_hub:"):
                    _, part2 = line.split(":", 1)
                    zone = self._parse_zone(part2.strip())
                    if start_zone is not None:
                        raise ValueError(f"Line {line_number}: multiple"
                                         + "start_hub definitions")
                    else:
                        start_zone = zone
                    if zone.name in zones:
                        raise ValueError(f"Line {line_number}: "
                                         + "duplicate zone '{zone.name}'")
                    else:
                        zones[zone.name] = zone

                elif line.startswith("end_hub:"):
                    _, part2 = line.split(":", 1)
                    zone = self._parse_zone(part2.strip())
                    if end_zone is not None:
                        raise ValueError(f"Line {line_number}: multiple "
                                         + "end_hub definitions")
                    else:
                        end_zone = zone
                    if zone.name in zones:
                        raise ValueError(f"Line {line_number}: duplicate zone"
                                         + f"'{zone.name}'")
                    else:
                        zones[zone.name] = zone

                elif line.startswith("hub:"):
                    _, data = line.split(":", 1)
                    zone = self._parse_zone(data.strip())
                    if zone.name in zones:
                        raise ValueError(f"Line {line_number}: "
                                         + f"duplicate zone '{zone.name}'")
                    else:
                        zones[zone.name] = zone

                elif line.startswith("connection:"):
                    _, data = line.split(":", 1)
                    edge = self._parse_connection(data.strip(),
                                                  zones, line_number)
                    if edge:
                        edge_key = tuple(sorted([
                            edge.zone_a.name, edge.zone_b.name]))
                        if edge_key in seen_connections:
                            raise ValueError(f"Line {line_number}: duplicate "
                                             + "connection")
                        seen_connections.add(edge_key)
                        edges.append(edge)
                else:
                    raise ValueError(f"Line {line_number}: unknown directive")

        if start_zone is None:
            raise ValueError("Invalid input: missing start_hub")
        if end_zone is None:
            raise ValueError("Invalid input: missing end_hub")
        if not nb_drones_seen:
            raise ValueError("Invalid input: missing nb_drones")

        return (Graph(zones, edges, start_zone, end_zone), nb_drones)

    def _parse_zone(self, line: str) -> Zone:
        """Parse the content after a hub prefix into a Zone object.

        Args:
            line: The string after the hub prefix, e.g. "roof1 3 4
            [zone=restricted color=red]"

        Returns:
            A Zone instance, or None if the line is empty.

        Example:
            Input:  "roof1 3 4 [zone=restricted color=red max_drones=2]"
            Output: Zone("roof1", (3, 4), ZoneType.RESTRICTED, 2, "red")
        """
        if not line:
            raise ValueError("Empty zone definition")

        if "[" in line:
            part1, part2 = line.split("[", 1)
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        part1_split = part1.split()

        if len(part1_split) < 3:
            raise ValueError(f"Invalid zone format: {line}")
        name = part1_split[0]

        if "-" in name or " " in name:
            raise ValueError(f"Invalid zone name: {name}")

        try:
            x = int(part1_split[1])
            y = int(part1_split[2])
        except (IndexError, ValueError):
            raise ValueError(f"Invalid coordinates for zone: {line}")

        try:
            zone_type = ZoneType(
                metadata.get("zone", metadata.get("type", "normal"))
            )
        except ValueError:
            raise ValueError(f"Invalid zone type: {metadata.get('zone')}")

        color = metadata.get("color", "")
        try:
            max_drones = int(metadata.get("max_drones", "1"))
        except ValueError:
            raise ValueError("Invalid max_drones value")
        if max_drones <= 0:
            raise ValueError("max_drones must be positive")

        return Zone(name, (x, y), zone_type, max_drones, color)

    def _parse_metadata(self, metadata_str: str) -> dict[str, str]:
        """Parse a metadata block string into a key-value dictionary.

        Args:
            metadata_str: A bracket-enclosed metadata string,
                          e.g. "[zone=restricted color=red max_drones=2]"

        Returns:
            A dict of key-value pairs, e.g.
            {"zone": "restricted", "color": "red"}
            Returns an empty dict if the input is empty.
        """
        if not metadata_str:
            return {}

        metadata_str = metadata_str.strip("[]")
        parts = metadata_str.split()
        res: dict[str, str] = {}
        for item in parts:
            if "=" not in item:
                raise ValueError(f"Invalid metadata format: {item}")
            key, value = item.split("=", 1)
            res[key] = value

        return res

    def _parse_connection(self, line: str, zones: dict[str, Zone],
                          line_number: int) -> Edge:
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
            raise ValueError("Empty connection definition")
        if "[" in line:
            part1, part2 = line.split("[", 1)
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        if "-" not in part1:
            raise ValueError(f"Line {line_number}: invalid "
                             + f"connection format: {line}")

        parts = part1.split("-")
        if len(parts) != 2:
            raise ValueError(f"Line {line_number}: invalid "
                             + f"connection format: {line}")

        name_zone_a, name_zone_b = parts
        zone_a = zones.get(name_zone_a.strip())
        zone_b = zones.get(name_zone_b.strip())

        if zone_a is None or zone_b is None:
            raise ValueError(f"Line {line_number}: unknown zone in connection")

        value = metadata.get("max_link_capacity", "1")
        try:
            max_link_capacity = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Line {line_number}: invalid max_link_capacity")

        if max_link_capacity <= 0:
            raise ValueError(f"Line {line_number}: max_link_capacity"
                             + "must be positive")

        return Edge(zone_a, zone_b, max_link_capacity)
