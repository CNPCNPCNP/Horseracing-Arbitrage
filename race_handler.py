import time
import os

from constants import *
from race import Race, RaceType
from scraper import RaceBuilder

from betfair import BetfairController

from dotenv import load_dotenv
from threading import Thread

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

    def __init__(self, path: str, betfair: BetfairController) -> None:
        self.path = path
        self.browserController = RaceBuilder(self.path, URL, betfair)
        self.races = set(self.browserController.goto_every_race())
        for race in self.races:
            print(race)
            thread = Thread(target = self.start_race_thread, args = [race])
            thread.start()
       
    def refresh_races(self) -> None:
        races_update = self.browserController.goto_every_race()
        for race in races_update:
            if race not in self.races:
                print("Races updated", race.get_venue(), race.get_race_number())
                thread = Thread(target = self.start_race_thread, args = [races_update[2]])
                thread.start()
                self.races.add(race)
        print("Successfully refreshed")

    def start_race_thread(self, race: Race) -> None:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        wd = webdriver.Chrome(service = Service(self.path), chrome_options = options)
        wd.maximize_window()
        wd.implicitly_wait(5)
        wd.get(race.get_url())
        self.keep_updating(wd, race)

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
            race_summary[(horse_name, gate, horse_number)] = float(price.text)
        race.set_horses(race_summary)
        return True

    def keep_updating(self, wd: webdriver.Chrome, race: Race) -> None:
        while self.get_race_data(wd, race): # If method returns False, thread should close
            time.sleep(1) # Poll race data every 1 second
        self.races.remove(race) # Remove race from races when completed
        print("Removed race", race.get_venue())

def main() -> None:
    load_dotenv('C:\\Users\\bened\Documents\\Alameda-Project\\global_vars.env', override = True)

    path = os.environ.get("PATH")
    certs_path = os.environ.get("CERTS_PATH")
    my_username = os.environ.get("MY_USERNAME")
    my_password = os.environ.get("MY_PASSWORD")
    my_app_key = os.environ.get("MY_APP_KEY")

    betfair = BetfairController(certs_path, my_username, my_password, my_app_key)
    app = Application(path, betfair)
    while True:
        time.sleep(30)
        print("Refreshing races attempt")
        app.refresh_races()

if __name__ == "__main__":
    main()


