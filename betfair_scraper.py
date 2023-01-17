import time
import pandas as pd

from constants import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class BetfairRaceScraper():

    def __init__(self, path: str, url: str, username: str, password: str) -> None:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.wd = webdriver.Chrome(service = Service(path), options = options)
        self.url = url
        self.wd.maximize_window()
        self.wd.implicitly_wait(20)
        self.wd.get(url)

        self.username = self.wd.find_element(By.XPATH, '//*[@id="ssc-liu"]')
        self.password = self.wd.find_element(By.XPATH, '//*[@id="ssc-lipw"]')
        self.login = self.wd.find_element(By.XPATH, '//*[@id="ssc-lis"]')

        self.username.send_keys(username)
        self.password.send_keys(password)
        self.wd.execute_script(CLICK, self.login)

        self.wd.implicitly_wait(15)
        time.sleep(8)

    def set_implicit_wait(self, wait: int) -> None:
        self.wd.implicitly_wait(wait)

    """
    Pages are slightly different for Trots, dogs and horse races. So need slightly different methods to scrape correctly.
    Ensure in main controlling class that correct method is used or there will be issues.
    """
    def get_prices_horses(self) -> dict:
        # Need to find how many non-scratched horses there are
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_elements(By.CLASS_NAME,'runner-name')[index - 1].text

            back_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[1]').text
            
            back_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[2]').text.replace("$", "")

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            lay_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[2]').text.replace("$", "")

            if not back_price:
                back_price = 9998
                back_volume = 1
            if not lay_price:
                lay_price = 9999
                lay_volume = 1
            if not back_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                back_volume = 1
            if not lay_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                lay_volume = 1

            back_price, back_volume, lay_price, lay_volume = float(back_price), int(back_volume), float(lay_price), int(lay_volume)

            midpoint_price = ((lay_price - back_price) / (back_volume + lay_volume) * back_volume) + back_price
            prices[horse_name] = midpoint_price

        return prices, volume

    def get_prices_american(self) -> dict:
        # Need to find how many non-scratched horses there are
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div[2]/div[2]/bf-runner-info/div/div/div[2]/h3').text
            
            back_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[1]').text
            
            back_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[2]').text.replace("$", "")

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text
            
            lay_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[2]').text.replace("$", "")

            if not back_price:
                back_price = 9998
                back_volume = 1
            if not lay_price:
                lay_price = 9999
                lay_volume = 1
            if not back_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                back_volume = 1
            if not lay_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                lay_volume = 1

            back_price, back_volume, lay_price, lay_volume = float(back_price), int(back_volume), float(lay_price), int(lay_volume)

            midpoint_price = ((lay_price - back_price) / (back_volume + lay_volume) * back_volume) + back_price
            prices[horse_name] = midpoint_price

        return prices, volume

    def get_prices_trots(self) -> dict:
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[3]/h3').text

            back_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[1]').text
            
            back_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[2]').text.replace("$", "")

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text
            
            lay_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[2]').text.replace("$", "")

            if not back_price:
                back_price = 9998
                back_volume = 1
            if not lay_price:
                lay_price = 9999
                lay_volume = 1
            if not back_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                back_volume = 1
            if not lay_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                lay_volume = 1

            back_price, back_volume, lay_price, lay_volume = float(back_price), int(back_volume), float(lay_price), int(lay_volume)

            midpoint_price = ((lay_price - back_price) / (back_volume + lay_volume) * back_volume) + back_price
            prices[horse_name] = midpoint_price

        return prices, volume

    def get_prices_dogs(self) -> dict:
        dogs = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(dogs) + 1):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[2]/h3').text
            
            back_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[1]').text
            
            back_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[4]/button/div/span[2]').text.replace("$", "")

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text
            
            lay_volume = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[2]').text.replace("$", "")

            if not back_price:
                back_price = 9998
                back_volume = 1
            if not lay_price:
                lay_price = 9999
                lay_volume = 1
            if not back_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                back_volume = 1
            if not lay_volume:
                print(f'No volume at {self.url} {back_volume} {lay_volume}')
                lay_volume = 1

            back_price, back_volume, lay_price, lay_volume = float(back_price), int(back_volume), float(lay_price), int(lay_volume)

            midpoint_price = ((lay_price - back_price) / (back_volume + lay_volume) * back_volume) + back_price
            prices[horse_name] = midpoint_price

        return prices, volume

    def get_lay_prices_horses(self) -> dict:
        # Need to find how many non-scratched horses there are
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_elements(By.CLASS_NAME,'runner-name')[index - 1].text

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            if lay_price:
                prices[horse_name] = float(lay_price)
            else:
                prices[horse_name] = 99999

        return prices, volume

    def get_lay_prices_american(self) -> dict:
        # Need to find how many non-scratched horses there are
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            # The XPATH for betfair is always so ugly, oh well
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div[2]/div[2]/bf-runner-info/div/div/div[2]/h3').text
            
            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text
            
            if lay_price:
                prices[horse_name] = float(lay_price)
            else:
                prices[horse_name] = 99999

        return prices, volume

    def get_lay_prices_trots(self) -> dict:
        horses = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(horses) + 1):
            
            horse_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[3]/h3').text

            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            if lay_price:
                prices[horse_name] = float(lay_price)
            else:
                prices[horse_name] = 99999

        return prices, volume

    def get_lay_prices_dogs(self) -> dict:
        dogs = self.wd.find_elements(By.CLASS_NAME, "back-selection-button")
        prices = {}
        volume = int(self.wd.find_element(By.CLASS_NAME, "total-matched").text.split(" ")[1].replace(",", ""))
        
        for index in range(1, len(dogs) + 1):
            # The XPATH for betfair is always so ugly, oh well
            dog_name = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[1]/div/div[2]/bf-runner-info/div/div/div[2]/h3').text
             
            lay_price = self.wd.find_element(By.XPATH,
            f'//*[@id="main-wrapper"]/div/div[2]/div/ui-view/div/div/div[1]/div[3]/div/div[1]/div/bf-main-market/bf-main-marketview/div/div[2]/bf-marketview-runners-list[2]/div/div/div/table/tbody/tr[{index}]/td[5]/button/div/span[1]').text

            if lay_price:
                prices[dog_name] = float(lay_price)
            else:
                prices[dog_name] = 99998

        return prices, volume

    def refresh(self) -> None:
        refresh_button = self.wd.find_element(By.CLASS_NAME, 'refresh-btn')
        self.wd.execute_script(CLICK, refresh_button)

    def close(self) -> None:
        self.wd.close()