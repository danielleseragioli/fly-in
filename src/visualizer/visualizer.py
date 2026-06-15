import pygame
import sys
from model.graph import Graph

# ======= ui settings =======

# -- window --
WINDOW_WIDTH = 1445
WINDOW_HEIGHT = 545
WINDOW_TITLE = "Fly-in Drone Simulation - Daniii 💫"
FPS = 10

# -- colors --
COLORS = {
    "normal":     (55, 34, 26),
    "restricted": (234, 83,  39),
    "priority":   (30,  140, 60),
    "blocked":    (245, 172, 180),
    "start":      (30,  80,  200),
    "end":        (140, 30,  200)
}

COLOR_NAMES = {
    "green":   (34, 177,  76),
    "blue":    (52,  131, 235),
    "red":     (234,  83,  39),
    "yellow":  (255, 220,  50),
    "orange":  (255, 140,   0),
    "purple":  (150,  60, 200),
    "black":   (20,   20,  20),
    "brown":   (120,  72,  40),
    "maroon":  (128,   0,   0),
    "gold":    (212, 175,  55),
    "darkred": (139,   0,   0),
    "violet":  (180,  80, 220),
    "crimson": (220,  20,  60),
    "cyan":    (0,   200, 200),
    "lime":    (160, 220,  40),
    "magenta": (220,  40, 180),
    "rainbow": (255, 255, 255),
}

COLOR_BACKGROUND = (245, 172,  180)
COLOR_EDGE_ACTIVE = (140, 30,  200)
COLOR_EDGE = (55, 34, 26)
COLOR_TEXT = (220, 220, 220)

# -- sizes --
ZONE_RADIUS = 4
DRONE_RADIUS = 10
EDGE_WIDTH = 2
MARGIN = 80

# -- images --
IMAGE_BKG = pygame.image.load("assets/bkg.png")
IMAGE_DRONE = pygame.image.load("assets/drone.png")
IMAGE_START = pygame.image.load("assets/start.png")
IMAGE_END = pygame.image.load("assets/end.png")


class Visualizer:
    """Render the simulation step by step with pygame."""

    def __init__(self, graph: Graph,
                 simulation_steps: list[list[str]]) -> None:
        """Initialize the visualizer state and load the map layout."""

        pygame.init()

        self.graph = graph
        self.simulation_steps = simulation_steps
        self.curr_turn = 0
        self.auto_play = False

        self.in_transit: dict[str, tuple[str, str]] = {}
        self.drone_positions: dict[str, str] = {}
        self._init_drone_positions()
        self.zone_positions = self._compute_positions()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)

    def _init_drone_positions(self) -> None:
        """Place every drone on the start zone before playback begins."""
        start_name = self.graph.start_zone.name
        drone_ids: set[str] = set()
        for turn in self.simulation_steps:
            for mov in turn:
                drone_id = mov.split("-")[0]
                drone_ids.add(drone_id)
        for drone_id in drone_ids:
            self.drone_positions[drone_id] = start_name

    def _compute_positions(self) -> dict[str, tuple[int, int]]:
        """Map graph coordinates to screen positions."""

        xs: list[int] = []
        ys: list[int] = []
        for zone in self.graph.zones.values():
            x, y = zone.coord
            xs.append(x)
            ys.append(y)

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        range_x = max_x - min_x
        if range_x == 0:
            range_x = 1

        range_y = max_y - min_y
        if range_y == 0:
            range_y = 1

        usable_w = WINDOW_WIDTH - MARGIN * 2
        usable_h = WINDOW_HEIGHT - MARGIN * 2

        positions: dict[str, tuple[int, int]] = {}
        start_zone_name = self.graph.start_zone.name
        end_zone_name = self.graph.end_zone.name

        for zone in self.graph.zones.values():
            x, y = zone.coord
            px = MARGIN + int((x - min_x) / range_x * usable_w)

            if zone.name == start_zone_name or zone.name == end_zone_name:
                py = WINDOW_HEIGHT // 2
            else:
                py = MARGIN + int((y - min_y) / range_y * usable_h)

            positions[zone.name] = (px, py)

        return positions

    def run(self) -> None:
        """Start the pygame loop and handle keyboard input."""
        auto_timer = 0
        while True:
            last_frame_time = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._advance_turn()
                    if event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                    if event.key == pygame.K_r:
                        self.curr_turn = 0
                        self._init_drone_positions()
                        self.in_transit = {}
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            if self.auto_play and self.curr_turn < len(self.simulation_steps):
                auto_timer += last_frame_time
                if auto_timer >= 500:
                    self._advance_turn()
                    auto_timer = 0

            self._draw()

    def _advance_turn(self) -> None:
        """Apply the movements scheduled for the current turn."""
        if self.curr_turn >= len(self.simulation_steps):
            return
        moves = self.simulation_steps[self.curr_turn]
        self.in_transit = {}
        for move in moves:
            drone_id, dest = move.split("-", 1)
            if dest in self.graph.zones:
                self.drone_positions[drone_id] = dest
            else:
                parts = dest.split("-")
                if len(parts) == 2:
                    origin = parts[0]
                    destination = parts[1]
                    self.in_transit[drone_id] = (origin, destination)
        self.curr_turn += 1

    def _draw(self) -> None:
        """Render one frame of the current simulation state."""
        if IMAGE_BKG:
            bkg = pygame.transform.scale(IMAGE_BKG,
                                         (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(bkg, (0, 0))
        else:
            self.screen.fill(COLOR_BACKGROUND)

        self._draw_edges()
        self._draw_zones()
        self._draw_drones()
        self._draw_legend()
        self._draw_ui()
        pygame.display.flip()

    def _draw_edges(self) -> None:
        """Draw all graph connections."""
        for edge in self.graph.edges:
            p1 = self.zone_positions[edge.zone_a.name]
            p2 = self.zone_positions[edge.zone_b.name]
            is_active = False
            for (origin, destination) in self.in_transit.values():
                if (
                    (origin == edge.zone_a.name and
                     destination == edge.zone_b.name) or
                    (origin == edge.zone_b.name and
                     destination == edge.zone_a.name)
                ):
                    is_active = True
            if is_active:
                color = COLOR_EDGE_ACTIVE
                stroke = EDGE_WIDTH + 2
            else:
                color = COLOR_EDGE
                stroke = EDGE_WIDTH
            pygame.draw.line(self.screen, color, p1, p2, stroke)

    def _draw_zones(self) -> None:
        """Draw zones, highlighting the start and end hubs."""
        for (name, zone) in self.graph.zones.items():
            position = self.zone_positions[name]
            if name == self.graph.start_zone.name:
                img = pygame.transform.scale(IMAGE_START, (120, 50))
                rect = img.get_rect(center=position)
                self.screen.blit(img, rect)
            elif name == self.graph.end_zone.name:
                img = pygame.transform.scale(IMAGE_END, (120, 50))
                rect = img.get_rect(center=position)
                self.screen.blit(img, rect)
            else:
                color = COLOR_NAMES.get(zone.color,
                                        COLORS.get(zone.zone_type.value,
                                                   COLORS["normal"]))
                pygame.draw.circle(self.screen, color, position, ZONE_RADIUS)

    def _draw_drones(self) -> None:
        """Draw drones at their current positions."""
        for (drone_id, zone_name) in self.drone_positions.items():
            if drone_id in self.in_transit:
                continue
            position = self.zone_positions[zone_name]
            if zone_name == self.graph.start_zone.name:
                position = (position[0], position[1] + 45)
            elif zone_name == self.graph.end_zone.name:
                position = (position[0], position[1] + 45)
            img = pygame.transform.scale(IMAGE_DRONE, (60, 60))
            rect = img.get_rect(center=position)
            self.screen.blit(img, rect)
            if zone_name not in (
                self.graph.start_zone.name,
                self.graph.end_zone.name
            ):
                label = self.font.render(drone_id, True, (255, 255, 255))
                self.screen.blit(label, (position[0] - label.get_width() // 2,
                                         position[1] - DRONE_RADIUS - 14))

        for (drone_id, (origin, dest)) in self.in_transit.items():
            p1 = self.zone_positions[origin]
            p2 = self.zone_positions[dest]
            position = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            img = pygame.transform.scale(IMAGE_DRONE, (120, 50))
            rect = img.get_rect(center=position)
            self.screen.blit(img, rect)
            label = self.font.render(drone_id, True, (255, 255, 255))
            self.screen.blit(label, (position[0] - label.get_width() // 2,
                                     position[1] - DRONE_RADIUS - 14))

    def _has_custom_colors(self) -> bool:
        """Return True if any zone in the map defines a custom color."""
        for zone in self.graph.zones.values():
            if zone.color:
                return True
        return False

    def _draw_legend(self) -> None:
        """Draw the default zone-type legend, but only if the map
        does not define any custom zone colors."""
        if self._has_custom_colors():
            return

        legend_items = [
            ("Normal", COLORS["normal"]),
            ("Restricted", COLORS["restricted"]),
            ("Priority", COLORS["priority"]),
            ("Blocked", COLORS["blocked"]),
        ]

        x = WINDOW_WIDTH - 170
        y = 20

        for label, color in legend_items:
            pygame.draw.circle(self.screen, color, (x, y + 8), 8)
            text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, (x + 20, y))
            y += 25

    def _draw_ui(self) -> None:
        """Draw the HUD with turn and control information."""

        text = f"Turn: {self.curr_turn} / {len(self.simulation_steps)}"
        surface = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(surface, (20, 20))

        text = f"Auto: {'ON' if self.auto_play else 'OFF'}"
        surface = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(surface, (20, 46))

        if self.curr_turn >= len(self.simulation_steps):
            text = f"Completed in {len(self.simulation_steps)} turns!"
            surface = self.font.render(text, True, COLOR_TEXT)
            x = WINDOW_WIDTH // 2 - surface.get_width() // 2
            self.screen.blit(surface, (x, 20))

        bar_height = 35
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (0, WINDOW_HEIGHT - bar_height, WINDOW_WIDTH, bar_height)
        )

        text = "[SPACE] Next   [A] Auto   [R] Restart   [Q] Quit"
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (20, WINDOW_HEIGHT - 26))
