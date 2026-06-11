from .zone import Zone
from .edge import Edge
from typing import Optional


class Graph:
    """Represents the network of zones and edges in the simulation."""

    def __init__(self, zones: dict[str, Zone], edges: list[Edge],
                 start_zone: Zone, end_zone: Zone):
        """Initialize the graph with zones, edges and adjacency list."""
        self.zones = zones
        self.edges = edges
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.adjacency: dict[str, list[Edge]] = {}
        for edge in self.edges:
            if edge.zone_a.name not in self.adjacency:
                self.adjacency[edge.zone_a.name] = []
            self.adjacency[edge.zone_a.name].append(edge)
            if edge.zone_b.name not in self.adjacency:
                self.adjacency[edge.zone_b.name] = []
            self.adjacency[edge.zone_b.name].append(edge)

    def add_zone(self, zone_to_add: Zone) -> bool:
        """Add a zone to the graph if it is not already present."""
        if zone_to_add.name in self.zones:
            return False
        self.zones[zone_to_add.name] = zone_to_add
        return True

    def add_edge(self, edge_to_add: Edge) -> bool:
        """Add an edge to the graph if it is not already present."""
        if edge_to_add in self.edges:
            return False
        self.edges.append(edge_to_add)
        return True

    def get_zone(self, zone_name: str) -> Zone:
        """Return the zone matching the given name."""
        if zone_name not in self.zones:
            raise KeyError(f"Zone '{zone_name}' not found")
        return self.zones[zone_name]

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Return the accessible neighboring zones for the given zone."""
        zone_neighbors = []
        for edge in self.adjacency.get(zone.name, []):
            if edge.zone_a == zone and not edge.zone_b.is_blocked():
                zone_neighbors.append(edge.zone_b)
            elif edge.zone_b == zone and not edge.zone_a.is_blocked():
                zone_neighbors.append(edge.zone_a)
        return zone_neighbors

    def has_connection(self, zone_a: Zone, zone_b: Zone) -> bool:
        """Return whether two zones are directly connected by an edge."""
        for edge in self.edges:
            if (edge.zone_a == zone_a and edge.zone_b == zone_b) or (
                    edge.zone_a == zone_b and edge.zone_b == zone_a):
                return True
        return False

    def get_edge(self, zone_a: Zone, zone_b: Zone) -> Optional[Edge]:
        """Return the edge connecting two zones, or None if not found."""
        for edge in self.edges:
            if (edge.zone_a == zone_a and edge.zone_b == zone_b) or (
                    edge.zone_a == zone_b and edge.zone_b == zone_a):
                return edge
        return None
