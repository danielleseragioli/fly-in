from zone import Zone
from occupiable import Occupiable


class Drone:
    def __init__(self, drone_id: str, current_zone: Zone, target_zone: Zone,
                 is_in_transit: bool, arrival_turn: int, is_delivered: bool):
        
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.target_zone = target_zone
        self.is_in_transit = is_in_transit
        self.arrival_turn = arrival_turn
        self.is_delivered = is_delivered


    def move_to_zone(self):
        pass


    def is_in_transit(self) -> bool:
        pass

    
    def is_delivered(self) -> bool:
        pass
