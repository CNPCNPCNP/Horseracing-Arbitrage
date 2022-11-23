from constants import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

class BetfairRaceScraper():

    def __init__(self, path: str, url: str) -> None:
        self.wd = webdriver.Chrome(service = Service(path))
        self.url = url
        self.wd.maximize_window()
        self.wd.implicitly_wait(10) 
        self.wd.get(url)

        # Set refresh button once to avoid having to find it every time we want to click it
        self.refresh_button = self.wd.find_element(By.CLASS_NAME, 'refresh-btn')

    def set_implicit_wait(self, wait: int) -> None:
        self.wd.implicitly_wait(wait)

    """
    Pages are slightly different for Trots, dogs and horse races. So need slightly different methods to scrape correctly.
    Ensure in main controlling class that correct method is used or there will be issues.
    """
    def get_lay_prices_horses(self) -> dict:
        # Need to find how many non-scratched horses there are
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        
        for index in range(1, len(horses)):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div[2]/div[2]/bf-runner-info/div/div/div[3]/h3').text
            
            horse_number = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div[2]/div[2]/bf-runner-info/div/div/div[1]/p[1]').text

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            prices[horse_name] = float(lay_price)

        return prices

    def get_lay_prices_trots(self) -> dict:
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        
        for index in range(1, len(horses)):
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[3]/h3').text
            
            horse_number = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[1]/p[1]').text

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            prices[horse_name] = float(lay_price)

        return prices

    def get_lay_prices_dogs(self) -> dict:
        dogs = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        
        for index in range(1, len(dogs)):
            # The XPATH for betfair is always so ugly, oh well
            dog_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[2]/h3').text

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            prices[dog_name] = float(lay_price)

        return prices

    def refresh(self) -> None:
        self.wd.execute_script(CLICK, self.refresh_button)

import time
path = "C:\Program Files (x86)\chromedriver.exe"
url = "https://www.betfair.com.au/exchange/plus/horse-racing/market/1.206747616"
test = BetfairRaceScraper(path, url)

while True:
    print(test.get_lay_prices_horses())
    test.refresh()
    time.sleep(1)