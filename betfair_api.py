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
    def get_events_for_venue(self, venue: str, type: RaceType):
        if type == RaceType.GREYHOUND_RACE:
            race_type = "greyhound"
        else:
            race_type = "horse"
        venue_filter = betfairlightweight.filters.market_filter(venues = [venue],
                                                                text_query = race_type)
        events = self.trading.betting.list_events(filter = venue_filter)
        return events

    """
    Takes a venue as a string and returns a list of markets at that venue
    """
    def get_markets_at_venue(self, venue: str, type: RaceType) -> list:
        events = self.get_events_for_venue(venue, type)
        for event in events:
            event_id = event.event.id
            market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids = [event_id])
            market_catalogues = self.trading.betting.list_market_catalogue(market_projection=['MARKET_START_TIME'],
                                                                           filter = market_catalogue_filter, 
                                                                           max_results = 20)
            date = market_catalogues[0].market_start_time.date()
            if date == date.today():
                market_catalogues = list(filter(matches, market_catalogues))
                return market_catalogues
        
    """
    Takes a race object and returns a marketID from betfair. If no matching race found, returns 0. May change logic for 
    this to throw exception if race not found.
    """
    def get_market(self, race: Race):
        venue = race.get_venue()
        race_number = race.get_race_number()
        market_catalogues = self.get_markets_at_venue(venue, race.get_type())
        for market in market_catalogues:
            market_race_number = int(market.market_name.split(" ")[0][1:])
            if market_race_number == race_number:
                return market.market_id
        return 0

def matches(catalogue) -> bool:
    name = catalogue.market_name.split(" ")[0]
    return re.match(WIN_MARKET_REGEX, name)