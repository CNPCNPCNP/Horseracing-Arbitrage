"""
Store each race as a custom class
"""
import shin

class Race():
    def __init__(self, location: str, race_number: int, horses: dict) -> None:
        self._location = location
        self._race_number = race_number
        self._horses = horses
    
    def get_location(self) -> str:
        return self._location

    def get_race_number(self) -> str:
        return self._race_number
    
    def get_horses(self) -> dict:
        return self._horses

    def __repr__(self) -> str:
        return f"<{self.get_location()}, {self.get_race_number()}>"

    def __str__(self) -> str:
        return f"Race {self.get_race_number()} at {self.get_location()}\nHorses: \n{self.get_horses()}"

    def shin_implied_odds(self) -> list:
        implied_odds = shin.calculate_implied_probabilities(self._horses.values())
        return implied_odds