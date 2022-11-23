# Import libraries
import datetime
import re

import betfairlightweight
from constants import *

from race import Race, RaceType

class BetfairAPIController():
    """
    Creates a login to betfair, allowing the user to interact with Betfairs API.
    """
    def __init__(self, certs_path: str, my_username: str, my_password: str, my_app_key: str) -> None:
        self.trading = betfairlightweight.APIClient(username = my_username,
                                                    password = my_password,
                                                    app_key = my_app_key,
                                                    certs = certs_path)
    
    """
    Formally logs in and establishes a connection with the API
    """
    def login(self) -> None:
        self.trading.login()

    """
    Refreshes our session with betfair so we don't get booted out
    """
    def keep_alive(self) -> None:
        self.trading.keep_alive()

    """
    Takes a venue as a string (eg. Flemington). Returns the event id of the first event at that venue, in most cases 
    there should only be one event at a venue anyway. (event is different to market)
    """
    def get_event_id_for_venue(self, venue: str) -> int:
        venue_filter = betfairlightweight.filters.market_filter(venues = [venue])
        events = self.trading.betting.list_events(filter = venue_filter)
        event_id = events[0].event.id
        return event_id

    """
    Takes a venue as a string and returns a list of markets at that venue
    """
    def get_markets_at_venue(self, venue: str) -> list:
        event_id = self.get_event_id_for_venue(venue)
        market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids = [event_id])
        market_catalogues = self.trading.betting.list_market_catalogue(filter = market_catalogue_filter, 
                                                                       max_results = 20)

        # Filter out markets that aren't main race markets using regex (string pattern matching) on market_name\
        # Not the most effective, sometimes names don't match necessarily
        market_catalogues = [catalogue for catalogue in market_catalogues if re.match(WIN_MARKET_REGEX, catalogue.market_name.split(" ")[0])]
        return market_catalogues

    """
    Takes a race object and returns a marketID from betfair. If no matching race found, returns 0. May change logic for 
    this to throw exception if race not found.
    """
    def get_market(self, race: Race):
        venue = race.get_venue()
        race_number = race.get_race_number()
        market_catalogues = self.get_markets_at_venue(venue)
        for market in market_catalogues:
            market_race_number = int(market.market_name.split(" ")[0][1:])
            if market_race_number == race_number:
                return market.market_id
        return 0

    def get_market_id(self, race: Race):
        venue = race.get_venue()
        race_type = race.get_type()
        if race_type == RaceType.GREYHOUND_RACE:
            pass