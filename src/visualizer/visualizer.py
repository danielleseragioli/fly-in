import pygame
import sys
from typing import Optional
from model.graph import Graph

# ======= ui settings =======

# -- window --
WINDOW_WIDTH  = 1445
WINDOW_HEIGHT = 545
WINDOW_TITLE = "Fly-in Drone Simulation - Daniii 💫"
FPS = 10

# -- colors --
COLORS = {
    "normal":     (70,  70,  90),
    "restricted": (180, 90,  20),   
    "priority":   (30,  140, 60),
    "blocked":    (30,  30,  30),
    "start":      (30,  80,  200),
    "end":        (140, 30,  200)
}
COLOR_BACKGROUND = (245, 172,  180)
COLOR_EDGE = (140, 30,  200)

# -- sizes --
ZONE_RADIUS = 8
DRONE_RADIUS = 10
EDGE_WIDTH = 2
MARGIN = 80

# -- images --
IMAGE_BKG = pygame.image.load("assets/bkg.png")
IMAGE_DRONE = pygame.image.load("assets/drone.png")
IMAGE_START = pygame.image.load("assets/start.png")
IMAGE_END = pygame.image.load("assets/end.png")

class Visualizer:

    def __init__(self, graph: Graph, simulation_steps: list[list[str]]) -> None:

        self.graph = graph
        self.simulation_steps = simulation_steps
        self.curr_turn = 0
        self.auto_play = False

        self.in_transit = {}
        self.drone_positions = {}
        self._init_drone_positions()  
        self.zone_positions = self._compute_positions()

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)

    def _init_drone_positions(self):
        start_name = self.graph.start_zone.name
        drone_ids = set()
        for turn in self.simulation_steps:
            for mov in turn:
                drone_id = mov.split("-")[0]
                drone_ids.add(drone_id)
        for drone_id in drone_ids:
            self.drone_positions[drone_id] = start_name

    def _compute_position(self):

        xs =[]
        ys =[]
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

        positions = {}
        for zone in self.graph.zones.values():
            x, y = zone.coord
            px = MARGIN + int((x - min_x) / range_x * usable_w)
            py = MARGIN + int((y - min_y) / range_y * usable_h)
            positions[zone.name] = (px, py)

        return positions

    def run(self):
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

    def _advance_turn(self):
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

    def _draw(self):
        if IMAGE_BKG:
            bkg = pygame.transform.scale(IMAGE_BKG, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.screen.blit(bkg, (0, 0))
        else:
            self.screen.fill(COLOR_BACKGROUND)
        
        self._draw_edges()
        self._draw_zones()
        self._draw_drones()
        self._draw_ui()
        pygame.display.flip()

    def _draw_edges(self):
        pass

    def _draw_zones(self):
        pass

    def _draw_drones(self):
        pass

    def _draw_ui(self):
        pass