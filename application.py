import time
import os
import threading

from constants import *
from race import Race, RaceType

from betr_scraper import RaceBuilder
from betfair_api import BetfairAPIController
from betfair_scraper import BetfairRaceScraper

from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

"""
Main class for our application. Primary application logic should take place in ths class. May split threading logic into 
separate class once completed. Contains an instance of BetfairController and RaceBuilder classes, which it uses to 
update the race list and manage the threads. 
"""
class Application():

    """
    Builds our application using a given BetfairController and creates a RaceBuilder using the given path and the
    constant URL.
    """
    def __init__(self, path: str, betfair: BetfairAPIController, username: str, password: str) -> None:
        self.path = path
        self.username = username
        self.password = password

        self.race_builder = RaceBuilder(self.path, URL, 2)
        self.betfair_controller = betfair
        self.betfair_controller.login()

        self.races = set()
        self.refresh_races()
    
    """
    Goes to every race on the upcoming races page. If the race is not in the current races set, adds the race to the set
    and starts a new thread (browser window) to monitor the race prices. Also grabs the betfair market id/url when the
    race is added to the races set. Set is used for slightly faster lookups than list (checking if a race is in the set)
    """
    def refresh_races(self) -> None:
        self.betfair_controller.keep_alive()
        races_update = self.race_builder.goto_every_race()
        for race in races_update:
            if race not in self.races:
                print("Races updated", race.get_venue(), race.get_race_number())
                race.set_market_id(self.betfair_controller.get_market(race))
                print(race.get_betfair_url())
                thread = threading.Thread(target = self.start_betr_thread, args = [race])
                thread.start()
                self.races.add(race)
        print("Successfully refreshed")

    """
    Starts a thread for a given race and enters loop of refreshing data for that race (opens a new browser window)
    """
    def start_betr_thread(self, race: Race) -> None:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        wd = webdriver.Chrome(service = Service(self.path), chrome_options = options)
        wd.maximize_window()
        wd.implicitly_wait(5)
        wd.get(race.get_url())
        self.betr_update(wd, race)

    """
    Updates the race data for a race and saves the details to the race dict. In future, this method will probably be
    used to determine betting opportunities.
    """
    def get_race_data(self, wd: webdriver.Chrome, race: Race) -> None:
        horses = wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")

        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]

        race_summary = {}
        for index, horse in enumerate(horses):
            horse_number, remainder = horse.text.split(" ", 1)
            horse_name, gate = remainder.rsplit(" ", 1)
            gate = int(gate[1:-1])
            number = index * 6 + 4
            #print(horse_name, number, gate)

            try:
                price = wd.find_element(By.XPATH, f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]")
            except NoSuchElementException:
                #If the element does not exist, can close thread as race has ended
                print("Race closed")
                return False
            race_summary[horse_name] = float(price.text)
        race.set_horses(race_summary)
        return True

    """
    Main loop for individual thread (browser window). Should poll and get new race data for each race every second. If 
    data is not found for a race, thread should be killed and browser window will be closed. 
    """
    def betr_update(self, wd: webdriver.Chrome, race: Race) -> None:
        # Use threading.Event to stop betfair thread when the betr thread is stopped (no way to directly terminate 
        # threads in Python, instead need to use shared state)
        event = threading.Event()
        event.set()

        # Start sub thread to monitor prices on betfair
        sub_thread = threading.Thread(target = self.start_betfair_thread, args = [race, event])
        sub_thread.start()
    
        wd.implicitly_wait(1)
        while self.get_race_data(wd, race): # If method returns False, thread should close
            time.sleep(1) # Poll race data every 1 second
        event.clear()
        self.races.remove(race) # Remove race from races when completed
        print("Removed race", race.get_venue(), race.get_race_number())

    """
    Betfair scraper thread logic. One of these threads should be created for each active BETR scraper thread, so a total
    of two browser windows per race (over complicated I know)
    """
    def start_betfair_thread(self, race: Race, event: threading.Event) -> None:
        scraper = BetfairRaceScraper(self.path, race.get_betfair_url(), self.username, self.password)
        self.betfair_update(race, scraper, event)

    def betfair_update(self, race: Race, scraper: BetfairRaceScraper, event: threading.Event) -> None:
        if race.get_type() == RaceType.HORSE_RACE:
            lay_price_method = scraper.get_lay_prices_horses
        elif race.get_type() == RaceType.TROT_RACE:
            lay_price_method = scraper.get_lay_prices_trots
        else:
            lay_price_method = scraper.get_lay_prices_dogs
        while event.is_set(): # If method returns False, thread should close
            scraper.refresh()
            print(lay_price_method())
            time.sleep(1) # Poll race data every 1 second


"""
Main entry point for application logic. 
"""
def main() -> None:
    load_dotenv('C:\\Users\\bened\Documents\\Alameda-Project\\global_vars.env', override = True)

    path = os.environ.get("PATH")
    certs_path = os.environ.get("CERTS_PATH")
    my_username = os.environ.get("MY_USERNAME")
    my_password = os.environ.get("MY_PASSWORD")
    my_app_key = os.environ.get("MY_APP_KEY")

    betfair = BetfairAPIController(certs_path, my_username, my_password, my_app_key)
    app = Application(path, betfair, my_username, my_password)
    while True:
        time.sleep(30) # Update races every 30 seconds, may not need to do this that often. But it seems pretty fast to
                       # do so maybe it doesn't matter.
        print("Refreshing races attempt")
        app.refresh_races()

if __name__ == "__main__":
    main()


