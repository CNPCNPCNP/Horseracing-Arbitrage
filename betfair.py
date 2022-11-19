# Import libraries
import betfairlightweight
from betfairlightweight import filters
import pandas as pd
import numpy as np
import os
import datetime
from dotenv import load_dotenv

# Change file path to your own global variables file (mine wasn't working sorry and can't define it in the env file. 
load_dotenv('C:\\Users\\bened\Documents\\Alameda-Project\\global_vars.env', override = True)

certs_path = os.environ.get("CERTS_PATH")
my_username = os.environ.get("MY_USERNAME")
my_password = os.environ.get("MY_PASSWORD")
my_app_key = os.environ.get("MY_APP_KEY")

class BetfairController():
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
        self.login = self.trading.login()
        return self.login

    """
    interacts with the API to return the horse racing event type id 
    """
    def horse_racing_event_id(self) -> int:
        horse_racing_filter = betfairlightweight.filters.market_filter(text_query='Horse Racing')
        horse_racing_event_type = self.trading.betting.list_event_types(filter= horse_racing_filter)
        horse_racing_event_type = horse_racing_event_type[0]
        horse_racing_event_type_id = horse_racing_event_type.event_type.id
        return horse_racing_event_type_id
    
    """
    interacts with the API to return the Aus horse races today - currently not working exactly as i wanted it. 
    """
    def aus_races_today(self):
        horse_racing_event_type_id = self.horse_racing_event_id()
        horse_racing_event_filter = betfairlightweight.filters.market_filter(event_type_ids=[horse_racing_event_type_id],
        market_countries=['AU'], market_start_time={'to': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%TZ")})
        aus_horse_events = self.trading.betting.list_events(filter= horse_racing_event_filter)
        return(aus_horse_events)

#Below code is Ben playing around with betfair api before turning into more concrete class / methods above. 
betfair = BetfairController(certs_path, my_username, my_password, my_app_key)
betfair.login()
id = betfair.horse_racing_event_id()
test = betfair.aus_races_today()
print(id)
print(test)

""" 

trading.login()

# Filter for just horse racing
horse_racing_filter = betfairlightweight.filters.market_filter(text_query='Horse Racing')

# This returns a list
horse_racing_event_type = trading.betting.list_event_types(filter=horse_racing_filter)

# Get the first element of the list
horse_racing_event_type = horse_racing_event_type[0]

horse_racing_event_type_id = horse_racing_event_type.event_type.id

# 
# Define a market filter
horse_racing_event_filter = betfairlightweight.filters.market_filter(
    event_type_ids=[horse_racing_event_type_id],
    market_countries=['AU'],
    market_start_time={
        'to': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%TZ")
    }
)

# Print the filter
horse_racing_event_filter

# Get a list of all thoroughbred events as objects
aus_thoroughbred_events = trading.betting.list_events(filter= horse_racing_event_filter)

# Create a DataFrame with all the events by iterating over each event object
aus_thoroughbred_events_today = pd.DataFrame({
    'Event Name': [event_object.event.name for event_object in aus_thoroughbred_events],
    'Event ID': [event_object.event.id for event_object in aus_thoroughbred_events],
    'Event Venue': [event_object.event.venue for event_object in aus_thoroughbred_events],
    'Country Code': [event_object.event.country_code for event_object in aus_thoroughbred_events],
    'Time Zone': [event_object.event.time_zone for event_object in aus_thoroughbred_events],
    'Open Date': [event_object.event.open_date for event_object in aus_thoroughbred_events],
    'Market Count': [event_object.market_count for event_object in aus_thoroughbred_events]
})

aus_thoroughbred_events_today """