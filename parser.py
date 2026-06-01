from graph import Graph
from zone import Zone


class Parser:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse() -> tuple[Graph, int]:
        pass

    def _parse_zone(self, line: str) -> Zone:

        if not line:
            return

        if "[" in line:
            part1, part2 = line.split("[")
            metadata = self._parse_metadata("[" + part2)
        else:
            part1 = line
            metadata = {}

        part1_split = part1.split()
        name = part1_split.split[1]
        x = int(part1_split[2])
        y = int(part1_split[3])
        zone_type = metadata.get("zone", "normal")
        color = metadata.get("color", "")
        max_drones = metadata.get("max")

        return Zone(name, x, y, zone_type, max_drones, color)

    def _parse_metadata(self, metadata_str: str) -> dict[str, str]:
        """Parse a metadata string like [zone=restricted color=red]
        into a dict."""

        if not metadata_str:
            return {}

        metadata_str = metadata_str.strip("[]")
        parts = metadata_str.split()
        res = {}
        for i in parts:
            key, value = i.split("=")
            res[key] = value

        return res

    def _parse_connection(self):
        pass
