from abc import ABC, abstractmethod


class Occupiable(ABC):

    @abstractmethod
    def can_receive_drone(self) -> bool:
        pass

    def add_drone(self) -> None:
        pass

    def remove_drone(self) -> None:
        pass

