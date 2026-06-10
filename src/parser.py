from graph import Graph
from zone import Zone, ZoneType
from edge import Edge
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
            zones = {}
            edges = []
            start_zone = None
            end_zone = None
            nb_drones = 0
            for line in file:
                line = line.strip()

                if line.startswith("nb_drones:"):
                    parts: list[str] = line.split(":")
                    nb_drones = int(parts[1].strip())

                elif line.startswith("start_hub:"):
                    _, part2 = line.split(":")
                    zone = self._parse_zone(part2)
                    start_zone = zone
                    zones[zone.name] = zone

                elif line.startswith("end_hub:"):
                    _, part2 = line.split(":")
                    zone = self._parse_zone(part2)
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
                            edges.append(edge)

        return (Graph(zones, edges, start_zone, end_zone), nb_drones)


                


    def _parse_zone(self, line: str) -> Optional[Zone]:

        """
        Parse the content after a hub prefix into a Zone object.

        Zone(name, coord, zone_type, max_drones, color)

        Input example:
            "roof1 3 4 [zone=restricted color=red max_drones=2]"
            "hub 0 0 [color=green]"

        Output example:
            Zone("roof1", (3, 4), ZoneType.RESTRICTED, 2, "red")
            Zone("hub", (0, 0), ZoneType.NORMAL, 1, "green")
        """

        if not line:
            return

        if "[" in line:
            part1, part2 = line.split("[")
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
        """
        Parse a metadata block string into a key-value dictionary.

         Input example:
            "[zone=restricted color=red max_drones=2]"
            ""  or no metadata present

        Output example:
            {"zone": "restricted", "color": "red", "max_drones": "2"}
            {}
        """

        if not metadata_str:
            return {}

        metadata_str = metadata_str.strip("[]")
        parts = metadata_str.split()
        res = {}
        for i in parts:
            key, value = i.split("=")
            res[key] = value

        return res

    def _parse_connection(self, line: str, zones: dict[str, Zone]) -> Optional[Edge]:
        """
        Parse the content after 'connection:' into an Edge object.

        Edge(zone_a, zone_b, max_link_capacity)

        Input example:
            "hub-roof1"
            "corridorA-tunnelB [max_link_capacity=2]"

        Output example:
            Edge(zones["hub"], zones["roof1"], 1)
            Edge(zones["corridorA"], zones["tunnelB"], 2)
        """

        if not line:
            return

        if "[" in line:
            part1, part2 = line.split("[")
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        name_zone_a, name_zone_b = part1.split("-")
        zone_a = zones.get(name_zone_a.strip())
        zone_b = zones.get(name_zone_b.strip())
        if zone_a is None or zone_b is None:
            raise ValueError(f"Unknown zone in connection: {line}")

        max_link_capacity = int(metadata.get("max_link_capacity", "1"))

        return Edge(zone_a, zone_b, max_link_capacity)
