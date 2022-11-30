import random
import string
import os
import time

from race import Race, RaceType

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class BetPlacementController():
    def __init__(self, url: str, betrUsername: str, betrPassword: str, horse: str, amount: str) -> None:
        self.wd = uc.Chrome()
        self.wd.maximize_window()
        self.wd.implicitly_wait(8)
        self.wd.get(url)

        self.horse = horse
        self.amount = amount

        login = self.wd.find_element(By.XPATH, '//*[@id="bm-root"]/div[3]/header/div/div[2]/button[1]')
        time.sleep(random.random())
        
        login.click()
        time.sleep(random.random())

        username_entry = self.wd.find_element(By.XPATH, '//*[@id="Username"]')
        password_entry = self.wd.find_element(By.XPATH, '//*[@id="Password"]')
        login_button = self.wd.find_element(By.XPATH, '//*[@id="floating-ui-root"]/div/div/div/div[2]/div[2]/form/div[3]/div/button')
        
        username_entry.click()

        time.sleep(random.random()/5)
        for letter in betrUsername:
            username_entry.send_keys(letter)
            time.sleep(random.random()/8)
        
        password_entry.click()
        time.sleep(random.random()/5)

        for letter in betrPassword:
            password_entry.send_keys(letter)
            time.sleep(random.random()/8)
        
        time.sleep(random.random()/5)
        login_button.click()

        horses = self.wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = self.wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")

        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]

        clicked = False
        for index, horse in enumerate(horses):
            _, remainder = horse.text.split(" ", 1)
            # Split once from the right to get gate separate from horse name. This avoids edge case where there are 
            # spaces in the horses name
            horse_name, _ = remainder.rsplit(" ", 1)
            horse_name = horse_name.translate(str.maketrans('', '', string.punctuation))
            print(horse_name)

            if horse_name == self.horse:
                number = index * 6 + 4
                button = self.wd.find_element(By.XPATH, f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]")
                self.button = f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]"
                button.click()
                print("Clicked")
                clicked = True
        
        if not clicked:
            raise Exception("Failed to find that horse")
        time.sleep(random.random()/6)
        self.bet_entry = self.wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div/input')
        self.confirm_button = self.wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[3]/div[3]/button[2]') 
        time.sleep(random.random()/6)
        self.bet_entry.click()
        time.sleep(random.random()/10)
        for letter in amount:
            self.bet_entry.send_keys(letter)
            time.sleep(random.random()/10)
        self.confirm_button.click()

    def confirm_bet(self, price: int) -> bool:
        self.confirm_button.click()
        try:
            self.wd.find_element(By.XPATH, '//*[@id="bm-grid"]/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/span')
            print(f"Bet placed successfully on {self.horse} for {self.amount} @ {price}")
            return True
        except NoSuchElementException:
            print("Price changed, bet failed")
            return False


# username = os.environ.get("BETR_USERNAME")
# password = os.environ.get("BETR_PASSWORD")
# url = "https://betr.com.au/racebook#/racing/2022-11-29/meeting/1007558/race/1095443"
# race = Race("Tamworth", 1, {}, url, RaceType.UNKNOWN_RACE)
# test = BetPlacementController(url, username, password, "King Qin", "2")
# time.sleep(10)
# test.confirm_bet(3)
# time.sleep(10)
