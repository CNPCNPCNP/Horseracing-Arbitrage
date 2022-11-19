"""
Store each race as a custom class
"""
import shin
from enum import Enum

class RaceType(Enum):
    HORSE_RACE = 0
    GREYHOUND_RACE = 1
    TROT_RACE = 2
    UNKNOWN_RACE = 3

class Race():
    def __init__(self, venue: str, race_number: int, horses: dict, type: RaceType) -> None:
        self._venue = venue
        self._race_number = race_number
        self._horses = horses
        self._type = type
    
    def get_venue(self) -> str:
        return self._venue

    def get_race_number(self) -> str:
        return self._race_number
    
    def get_horses(self) -> dict:
        return self._horses

    def get_type(self) -> str:
        return self._type

    def shin_implied_odds(self) -> list:
        implied_odds = shin.calculate_implied_probabilities(self._horses.values())
        return implied_odds

    def __repr__(self) -> str:
        return f"<{self.get_venue()}, {self.get_race_number()}, {self.get_type()}>"

    def __str__(self) -> str:
        return f"Race {self.get_race_number()} at {self.get_venue()}\nHorses: \n{self.get_horses()}"