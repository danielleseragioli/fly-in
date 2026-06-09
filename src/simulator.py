from parser import Parser
from drone import Drone
from pathfinder import Pathfinder
from reservation_table import ReservationTable


class Simulator:
    def __init__(self, input_file: str):
        self.parser = Parser(input_file)
        self.graph, self.nb_drones = self.parser.parse()
        start = self.graph.start_zone
        self.drones = [Drone(f"D{i+1}", start) for i in range(self.nb_drones)]
        self.pathfinder = Pathfinder()
        self.turn = 0
        self.max_turns = 45

    def run(self) -> None:
        start = self.graph.start_zone
        end = self.graph.end_zone

        table = ReservationTable()
        
        for drone in self.drones:
            chosen_path_nodes = self.pathfinder.dijkstra(self.graph, start, end, table)
            
            if not chosen_path_nodes:
                print(f"❌ Erro: Não foi possível encontrar um caminho válido para o {drone.drone_id}")
                return
                
            drone.planned_path = chosen_path_nodes
            drone.path_index = 1 if len(chosen_path_nodes) > 1 else 0
            
            for i in range(len(chosen_path_nodes)):
                zone_name, turn = chosen_path_nodes[i]
                
                table.reserve_zone(zone_name, turn)
                
                if i < len(chosen_path_nodes) - 1:
                    next_zone_name, next_turn = chosen_path_nodes[i + 1]
                    if zone_name != next_zone_name:
                        table.reserve_edge(zone_name, next_zone_name, turn)
        
        delivered = set()
        self.turn = 0
        
        while len(delivered) < len(self.drones):
            movements = []
            
            for drone in self.drones:
                if drone.drone_id in delivered:
                    continue
                
                if drone.path_index < len(drone.planned_path):
                    zone_name, target_turn = drone.planned_path[drone.path_index]

                    if zone_name != drone.current_zone.name:
                        movements.append(f"{drone.drone_id}-{zone_name}")
                        drone.current_zone = self.graph.get_zone(zone_name)

                    if zone_name == end.name:
                        delivered.add(drone.drone_id)

                    drone.path_index += 1
                else:
                    if drone.drone_id not in delivered:
                        delivered.add(drone.drone_id)

            if movements:
                self.turn += 1
                print(" ".join(movements))
            else:
                if len(delivered) == len(self.drones):
                    break
                self.turn += 1
        print(f"\n✅ Simulação concluída em {self.turn} turnos")