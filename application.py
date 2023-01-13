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
        self.betted = {}
        self.betted_horses = set()
        self.refreshing = True
        self.fails = 0
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
                self.betted[race] = 0
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
            _ = wd.find_element(By.XPATH, '//*[@id="Username"]')
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
            
            try:
                _, remainder = horse.text.split(" ", 1)
            except ValueError as ex:
                print(f"Failed to get {horse.text} at {race.get_venue()} {race.get_race_number()}")
                return False
            except Exception as ex:
                print(f'{race.get_venue()}, {race.get_race_number()} other exception thrown')
                return False
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
            if race.check_betfair_prices() and self.betted[race] <= 0.5:
                horse, price, volume, midpoint_price = race.get_arb_horses()
                if horse and horse not in self.betted_horses:
                    print(f"Attempting to bet on {horse} at {race.get_venue()}")
                    try:
                        timestamp = datetime.now()
                        amount = round(TARGET_WINNINGS / price, 1) #Round to nearest 10c to make amounts less suspicious
                        print(f"Betting {amount}")
                        betted = self.bet_horse(wd, horse, amount, race)
                        bet = Bet(horse, amount, race.get_type(), race.get_venue(), race.get_race_number(), price, volume, timestamp, midpoint_price, race.get_event_id())
                    except NoSuchElementException as ex:
                        print(ex)
                        print(f"Bet failed @ {race.get_venue()}")
                        betted = False
                        event.clear()

                    if betted:
                        bet.log_bet()
                        self.betted[race] += 1/price
                        self.betted_horses.add(horse)
                        try:
                            clear_slip = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[1]')
                            wd.execute_script(CLICK, clear_slip)
                        except NoSuchElementException:
                            print(f"Couldn't find refresh button at {race.get_venue()} {race.get_race_number()}")
                        wd.refresh()
                        wd.get(race.get_url())
                    else:
                        self.fails += 1
                        
            time.sleep(0.5) # Poll race data every 0.5 seconds
        event.clear()
        self.races.remove(race) # Remove race from races when completed
        print("Removed race", race.get_venue(), race.get_race_number())
        wd.close()
        self.refresh_races()
    
    def bet_horse(self, wd: uc.Chrome, target_horse: str, amount: int, race: Race) -> bool:
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

            if horse_name == target_horse:
                number = index * 6 + 4
                button = wd.find_element(By.XPATH, f'//*[@id="bm-content"]/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]')
                wd.execute_script(CLICK, button)
                break
        
        bet_entry = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/input')
        confirm_button = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[2]') 
        wd.execute_script(CLICK, bet_entry)
        bet_entry.send_keys(str(amount))
        wd.execute_script(CLICK, confirm_button)
        time.sleep(random.random()/10)
        wd.execute_script(CLICK, confirm_button)
        
        wd.implicitly_wait(8)
        time.sleep(10)
        try:
            wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/span')
            print(f"Bet placed successfully on {target_horse} for {amount}")
            wd.get(race.get_url())
            wd.refresh()
            return True
        except NoSuchElementException:
            print("Price changed, bet failed")
            edit_bet = wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[1]')
            wd.execute_script(CLICK, edit_bet)
            wd.get(race.get_url())
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
            price_method = scraper.get_lay_prices_american
            midpoint_method = scraper.get_prices_american
        elif race.get_type() == RaceType.HORSE_RACE and race.get_venue() not in AMERICAN_RACES:
            price_method = scraper.get_lay_prices_horses
            midpoint_method = scraper.get_prices_horses
        elif race.get_type() == RaceType.TROT_RACE:
            price_method = scraper.get_lay_prices_trots
            midpoint_method = scraper.get_prices_trots
        else:
            price_method = scraper.get_lay_prices_dogs
            midpoint_method = scraper.get_prices_dogs
        while event.is_set(): # If method returns False, thread should close
            try:
                scraper.refresh()
            except NoSuchElementException:
                print(f"Exiting {scraper.url}")
                event.clear()
                break

            try:
                prices, volume = price_method()
                race.set_betfair_prices(prices)
                race.set_volume(volume)
                prices, _ = midpoint_method()
                race.set_midpoint_prices(prices)
            except NoSuchElementException:
                print(f"No Such element, closing thread for race {race.get_race_number()} {race.get_venue()}!")
                event.clear()
                break
                #Close betr and betfair threads if for some reason the betfair scraping fails
            
            if race.check_betfair_prices():
                current = datetime.now()
                comparison = pd.DataFrame([race.compare_prices()], index=[current.strftime('%d-%m-%Y %H:%M:%S.%f')])
            scraper.log = pd.concat([scraper.log, comparison])
            time.sleep(0.5) # Poll race data every 0.5s
        event.clear()
        date = datetime.now()

        scraper.log.to_csv(f'logs/{date.strftime("%d-%m-%Y_%S")}_{race.get_venue()}_{race.get_race_number()}_{race.get_market_id()}_{race.get_event_id()}.csv')
        scraper.close()

class Bet():
    def __init__(self, horse: str, amount: float, type: RaceType, venue: str, race_number: int, price: float, volume: int, time: datetime, midpoint_price: float, event_id: int):
        self.horse = horse
        self.amount = amount
        self.type = type
        self.venue = venue
        self.race_number = race_number
        self.price = price
        self.volume = volume
        self.time = time
        self.event_id = event_id
        self.midpoint_price = midpoint_price

        if venue in AMERICAN_RACES:
            self.location = 'USA'
        else:
            self.location = 'AUS'

    def log_bet(self) -> None:
        date = datetime.now().strftime('%d-%m-%Y')
        bet = pd.DataFrame({'Horse': self.horse,
                            'Amount': self.amount,
                            'Type': self.type,
                            'Venue': f'{self.venue} {self.race_number}',
                            'Location': self.location,
                            'Event ID': self.event_id,
                            'Price': self.price,
                            'Volume': self.volume,
                            'Midpoint Price': self.midpoint_price
                            }, index=[self.time.strftime('%d-%m-%Y %H:%M:%S')])
        bet.to_csv(f'bets/{date}_{self.horse}_{self.venue}_{self.race_number}.csv')

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
        print(app.races, app.fails)
        time.sleep(30) # Update races every 30 seconds, may not need to do this that often. But it seems pretty fast to
                       # do so maybe it doesn't matter.
        #app.refresh_races()
    
    app.refreshing = False
    exit() # Won't fully exit until all threads are done apparently

if __name__ == "__main__":
    main()
