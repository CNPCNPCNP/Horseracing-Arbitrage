import os
import random
import string
import time
import threading

import pandas as pd

from constants import *
from datetime import datetime
from race import Race, RaceType

from betr_scraper import RaceBuilder
from betfair_api import BetfairAPIController
from betfair_scraper import BetfairRaceScraper

from dotenv import load_dotenv

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

"""
Main class for our application. Primary application logic should take place in ths class. May split threading logic into 
separate class once completed. Contains an instance of BetfairController and RaceBuilder classes, which it uses to 
update the race list and manage the threads. 
"""
class Application():

    """
    Builds our application using a given BetfairController and creates a RaceBuilder using the given path and the
    constant URL. Set the races parameter to scan more races at a time. 
    """
    def __init__(self, path: str, betfair: BetfairAPIController, username: str, password: str, betr_username: str, betr_password: str, races: int) -> None:
        self.path = path
        self.username = username
        self.password = password

        self.betr_username = betr_username
        self.betr_password = betr_password

        self.race_builder = RaceBuilder(self.path, URL, races)
        self.betfair_controller = betfair
        self.betfair_controller.login()

        self.number_of_races = races
        self.races = set()
        self.betted = set()
        self.refreshing = True
        self.refresh_races()

    """
    Goes to every race on the upcoming races page. If the race is not in the current races set, adds the race to the set
    and starts a new thread (browser window) to monitor the race prices. Also grabs the betfair market id/url when the
    race is added to the races set. Set is used for slightly faster lookups than list (checking if a race is in the set)
    """
    def refresh_races(self) -> None:
        # Return early and don't refresh if refreshing boolean is False
        if not self.refreshing:
            return
        # Return early if we are already scraping the correct number of races
        if len(self.races) >= self.number_of_races:
            return
        print("Refreshing races attempt")
        self.betfair_controller.keep_alive()
        races_update = self.race_builder.goto_every_race()
        for race in races_update:
            if race not in self.races:
                print("Races updated", race.get_venue(), race.get_race_number())
                race.set_market_id(self.betfair_controller.get_market(race))
                if race.get_market_id() == 0:
                    print("Couldn't match market ID")
                    continue
                print(race.get_betfair_url())
                thread = threading.Thread(target = self.start_betr_thread, args = [race])
                thread.start()
                self.races.add(race)
        print("Successfully refreshed")

    """
    Starts a thread for a given race and enters loop of refreshing data for that race (opens a new browser window)
    """
    def start_betr_thread(self, race: Race) -> None:
        uc_options = uc.ChromeOptions()
        uc_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
        wd = uc.Chrome(options = uc_options)
        wd.maximize_window()
        wd.implicitly_wait(8)
        self.login(wd, race.get_url())

        self.betr_update(wd, race)

    def login(self, wd: uc.Chrome, url: str) -> None:
        wd.get(url)
        login = wd.find_element(By.XPATH, '//*[@id="bm-root"]/div[3]/header/div/div[2]/button[1]')
        wd.execute_script(CLICK, login)
        time.sleep(1.5 + random.random())
        username_entry = wd.find_element(By.XPATH, '//*[@id="Username"]')
        password_entry = wd.find_element(By.XPATH, '//*[@id="Password"]')
        login_button = wd.find_element(By.XPATH, '//*[@id="floating-ui-root"]/div/div/div/div[2]/div[2]/form/div[3]/div/button')
        
        username_entry.click()

        time.sleep(random.random()/5)
        username_entry.send_keys(self.betr_username)
        time.sleep(random.random()/5)
        password_entry.click()
        password_entry.send_keys(self.betr_password)
        time.sleep(random.random()/5)
        login_button.click()
        time.sleep(5)
        try:
            failure = wd.find_element(By.XPATH, '//*[@id="Username"]')
            print(f"Failed login, trying again at {url}")
            self.login(wd, url)
        except NoSuchElementException:
            print(f"Successfully logged in at {url}")

    """
    Updates the race data for a race and saves the details to the race dict. In future, this method will probably be
    used to determine betting opportunities.
    """
    def get_race_data(self, wd: uc.Chrome, race: Race) -> bool:
        horses = wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")

        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]

        race_summary = {}
        for index in range(len(horses)):
            number = 6 * index + 1

            try:
                horse = wd.find_element(By.XPATH, f'//*[@id="bm-content"]/div[2]/div/div[2]/div[2]/div[{number}]/div/div[2]/span')
            except NoSuchElementException:
                print(f"Couldn't find {index} at {race.get_venue()} {race.get_race_number()}")
                return False
            horse_number, remainder = horse.text.split(" ", 1)
            horse_name, gate = remainder.rsplit(" ", 1)
            horse_name = horse_name.translate(str.maketrans('', '', string.punctuation))
            gate = int(gate[1:-1])

            number = index * 6 + 4
            try:
                price = wd.find_element(By.XPATH, f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]")
            except NoSuchElementException:
                #If the element does not exist, can close thread as race has ended
                print("Race closed")
                return False
            race_summary[horse_name] = float(price.text)
        race.set_betr_prices(race_summary)
        return True

    """
    Main loop for individual thread (browser window). Should poll and get new race data for each race every second. If 
    data is not found for a race, thread should be killed and browser window will be closed. 
    """
    def betr_update(self, wd: uc.Chrome, race: Race) -> None:
        # Use threading.Event to stop betfair thread when the betr thread is stopped (no way to directly terminate 
        # threads in Python, instead need to use shared state)
        event = threading.Event()
        event.set()

        # Start sub thread to monitor prices on betfair
        sub_thread = threading.Thread(target = self.start_betfair_thread, args = [race, event])
        sub_thread.start()
    
        while self.get_race_data(wd, race) and event.is_set(): # If method returns False, thread should close
            if race.check_betfair_prices() and race not in self.betted:
                horse = race.get_arb_horses()
                if horse:
                    print(f"Attempting to bet on {horse} at {race.get_venue()}")
                    try:
                        race.betted = self.bet_horse(wd, horse, 1, race)
                    except NoSuchElementException:
                        print(f"Bet failed @ {race.get_venue()}")
                        event.clear()
            time.sleep(0.5) # Poll race data every 0.5 seconds
        event.clear()
        self.races.remove(race) # Remove race from races when completed
        print("Removed race", race.get_venue(), race.get_race_number())
        wd.close()
        self.refresh_races()
    
    def bet_horse(self, wd: uc.Chrome, target_horse: str, amount: int, race: Race):
        horses = wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")
        wd.implicitly_wait(0.5)

        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]

        for index, horse in enumerate(horses):
            _, remainder = horse.text.split(" ", 1)
            # Split once from the right to get gate separate from horse name. This avoids edge case where there are 
            # spaces in the horses name
            horse_name, _ = remainder.rsplit(" ", 1)
            horse_name = horse_name.translate(str.maketrans('', '', string.punctuation))
            print(horse_name)

            if horse_name == target_horse:
                number = index * 6 + 4
                button = wd.find_element(By.XPATH, f'//*[@id="bm-content"]/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]')
                wd.execute_script(CLICK, button)
                break
        
        #time.sleep(random.random()/10)
        bet_entry = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/input')
        confirm_button = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[2]') 
        bet_entry.click()
        #time.sleep(random.random()/10)
        bet_entry.send_keys(str(amount))
        #time.sleep(random.random()/10)
        confirm_button.click()
        time.sleep(random.random()/10)
        confirm_button.click()
        
        wd.implicitly_wait(8)
        time.sleep(10)
        try:
            wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/span')
            print(f"Bet placed successfully on {target_horse} for {amount}")
            self.betted.add(race)
            wd.get(race.get_url())
            return True
        except NoSuchElementException:
            print("Price changed, bet failed")
            edit_bet = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[1]')
            edit_bet.click()
            
            x_button = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div[1]/div[3]/div[1]/div/button/svg')
            x_button.click()
            wd.refresh()
            return False

    """
    Betfair scraper thread logic. One of these threads should be created for each active BETR scraper thread, so a total
    of two browser windows per race (over complicated I know)
    """
    def start_betfair_thread(self, race: Race, event: threading.Event) -> None:
        scraper = BetfairRaceScraper(self.path, race.get_betfair_url(), self.username, self.password)
        self.betfair_update(race, scraper, event)

    def betfair_update(self, race: Race, scraper: BetfairRaceScraper, event: threading.Event) -> None:
        if race.get_type() == RaceType.HORSE_RACE and race.get_venue() in AMERICAN_RACES:
            lay_price_method = scraper.get_lay_prices_american
        elif race.get_type() == RaceType.HORSE_RACE and race.get_venue() not in AMERICAN_RACES:
            lay_price_method = scraper.get_lay_prices_horses
        elif race.get_type() == RaceType.TROT_RACE:
            lay_price_method = scraper.get_lay_prices_trots
        else:
            lay_price_method = scraper.get_lay_prices_dogs
        while event.is_set(): # If method returns False, thread should close
            try:
                scraper.refresh()
            except NoSuchElementException:
                print(f"Exiting {scraper.url}")
                event.clear()
                break

            try:
                race.set_betfair_prices(lay_price_method())
            except NoSuchElementException as ex:
                print(f"No Such element, closing thread for race {race.get_race_number()} {race.get_venue()}!")
                event.clear()
                raise ex
                #Close betr and betfair threads if for some reason the betfair scraping fails
            
            if race.check_betfair_prices():
                comparison = pd.DataFrame([race.compare_prices()])
            scraper.log = pd.concat([scraper.log, comparison], ignore_index=True)
            time.sleep(1) # Poll race data every 1 second
        event.clear()
        date = datetime.now()

        scraper.log.to_csv(f'logs/{date.strftime("%d-%m-%Y")}_{race.get_venue()}_{race.get_race_number()}_{race.get_market_id()}.csv')
        scraper.close()

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
    races = int(os.environ.get("RACES"))
    betr_username = os.environ.get("BETR_USERNAME")
    betr_password = os.environ.get("BETR_PASSWORD")

    betfair = BetfairAPIController(certs_path, my_username, my_password, my_app_key)
    app = Application(path, betfair, my_username, my_password, betr_username, betr_password, races)
    stop_time = time.time() + 60 * RUN_TIME_MINUTES

    app.refreshing = True

    while time.time() < stop_time:
        print(stop_time - time.time())
        time.sleep(30) # Update races every 30 seconds, may not need to do this that often. But it seems pretty fast to
                       # do so maybe it doesn't matter.
        #app.refresh_races()
    
    app.refreshing = False
    exit() # Won't fully exit until all threads are done apparently

if __name__ == "__main__":
    main()
