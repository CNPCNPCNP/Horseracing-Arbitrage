import time
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

#url for example Betfair race. 
url = 'https://www.betfair.com.au/exchange/plus/en/football/fifa-world-cup/winner-2022-betting-1.145970106' 

#selenium web driver to test accessing BETR site
class BrowserController():
    def __init__(self, path: str) -> None:
        self.path = path
        self.wd = webdriver.Chrome('chromedriver')
        self.wd.maximize_window() # For maximizing window
        self.wd.implicitly_wait(20) # gives an implicit wait for 20 seconds
        self.wd.get(url)
        
# I can't seem to toggle with this command to return where the odds for the horse are :(, currently yields an erorr
#price_of_horsey= wd.find_element(By.XPATH, "//*[@id="+'"'+'"bm-content"'+"]/div[2]/div/div[2]/div[2]/div[4]/button/div")

if __name__ == "__main__":
    load_dotenv()
    path = os.environ.get("PATH")
    browserController = BrowserController(path)
    time.sleep(10)
