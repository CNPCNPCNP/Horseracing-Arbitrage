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
    def __init__(self, venue: str, race_number: int, horses: dict, url: str, type: RaceType) -> None:
        self._venue = venue
        self._race_number = race_number
        self._horses = horses
        self._url = url
        self._type = type
    
    def get_venue(self) -> str:
        return self._venue

    def get_race_number(self) -> str:
        return self._race_number
    
    def get_horses(self) -> dict:
        return self._horses

    def get_url(self) -> str:
        return self._url

    def get_type(self) -> str:
        return self._type

    def set_horses(self, horses: dict) -> None:
        self._horses = horses

    def valid_race(self) -> bool:
        return self._venue and self._race_number and self._horses and self._url

    def shin_implied_odds(self) -> list:
        implied_odds = shin.calculate_implied_probabilities(self._horses.values())
        return implied_odds

    def __repr__(self) -> str:
        return f"<{self.get_venue()}, {self.get_race_number()}, {self.get_type()}>"

    def __str__(self) -> str:
        return f"Race {self.get_race_number()} at {self.get_venue()}\nRunners: \n{self.get_horses()}"

    def __hash__(self) -> int:
        return hash(self._url)

    def __eq__(self, other) -> bool:
        if isinstance(other, Race):
            return self.get_url() == other.get_url()
        return False

    def __ne__(self, other) -> bool:
        return not (self == other)
