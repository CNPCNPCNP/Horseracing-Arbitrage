"""
Store each race as a custom class
"""
import shin
from enum import Enum

class RaceType(Enum):
    UNKNOWN_RACE = 0
    HORSE_RACE = 1
    GREYHOUND_RACE = 2
    TROT_RACE = 3

class Race():
    def __init__(self, venue: str, race_number: int, prices: dict, url: str, type: RaceType) -> None:
        self._venue = venue
        self._race_number = race_number
        self._prices = prices
        self._url = url
        self._type = type

        # Betfair stuff
        self._market_id = 0
        self._betfair_url = ""
        self._betfair_prices = None
    
    def get_venue(self) -> str:
        return self._venue

    def get_race_number(self) -> str:
        return self._race_number
    
    def get_prices(self) -> dict:
        return self._prices

    def get_url(self) -> str:
        return self._url

    def get_type(self) -> str:
        return self._type

    def get_market_id(self) -> int:
        return self._market_id

    def get_betfair_url(self) -> str:
        return self._betfair_url

    def check_betfair_prices(self) -> bool:
        return self._betfair_prices is not None

    def set_market_id(self, market_id: int) -> None:
        self._market_id = market_id
        if self.get_type() == RaceType.GREYHOUND_RACE:
            self._betfair_url = f"https://www.betfair.com.au/exchange/plus/greyhound-racing/market/{market_id}"
        else:
            self._betfair_url = f"https://www.betfair.com.au/exchange/plus/horse-racing/market/{market_id}"

    def set_betr_prices(self, prices: dict) -> None:
        self._prices = prices

    def set_betfair_prices(self, prices: dict) -> None:
        self._betfair_prices = prices

    def valid_race(self) -> bool:
        return self._venue and self._race_number and self._prices and self._url and self._type != RaceType.UNKNOWN_RACE

    def shin_implied_odds(self) -> list:
        implied_odds = shin.calculate_implied_probabilities(self._prices.values())
        return implied_odds

    def compare_prices(self) -> dict:
        results = {}
        for horse in self._prices:
            betr_price = self._prices[horse]
            betfair_price = self._betfair_prices.get(horse, 99999)
            if betfair_price < betr_price:
                print("ARB POSSIBLE")
            results[horse] = betr_price, betfair_price
        return results

    def __repr__(self) -> str:
        return f"<{self.get_venue()}, {self.get_race_number()}, {self.get_type()}>"

    def __str__(self) -> str:
        return f"Race {self.get_race_number()} at {self.get_venue()}\nRunners: \n{self.get_betr_prices()}"

    def __hash__(self) -> int:
        return hash(self._url)

    def __eq__(self, other) -> bool:
        if isinstance(other, Race):
            return self.get_url() == other.get_url()
        return False

    def __ne__(self, other) -> bool:
        return not (self == other)
