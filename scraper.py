import time
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

#url for example Betfair race. 
url = 'https://betr.com.au/racebook#/racing/home/upcoming'
CLICK = "arguments[0].click();"

#selenium web driver to test accessing BETR site
class BrowserController():

    def __init__(self, path: str) -> None:
        self.path = path

        self.wd = webdriver.Chrome(path)
        self.wd.maximize_window() # For maximizing window
        self.wd.implicitly_wait(20) # gives an implicit wait for 20 seconds
        self.wd.get(url)

    def get_price(self) -> float:
        #search = self.wd.find_element(By.CLASS_NAME, "bet-button-price")
        price = self.wd.find_element(By.XPATH, "//*[@id="+'"'+'"bm-content"'+"]/div[2]/div/div[2]/div[2]/div[4]/button/div")
        
        return price

    def goto_next_race(self):
        next_race = self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[2]/div[2]/div[1]')
        self.wd.execute_script(CLICK, next_race)
        print(self.wd.title)

if __name__ == "__main__":
    load_dotenv()
    path = os.environ.get("PATH")
    browserController = BrowserController(path)
    #price = browserController.get_price()
    #print(price)
    browserController.goto_next_race()
    time.sleep(10)
