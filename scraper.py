import time
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

#CONSTANTS. Use all capitals to define global constants please
URL = 'https://betr.com.au/racebook#/racing/home/upcoming'
CLICK = "arguments[0].click();"

"""
Main controller class for webdriver and associated methods
"""
class BrowserController():

    """
    Creates a browser controller with the associated webdriver and URL path. Use self.wd inside this class to access webdriver. Takes path as an input, so make sure you have the PATH 
    variable setup in your .env file. If you need to access the webdriver outside this class, use the getter method get_webdriver
    """
    def __init__(self, path: str, url: str) -> None:
        self.path = path

        self.wd = webdriver.Chrome(path)
        self.wd.maximize_window() # For maximizing window
        self.wd.implicitly_wait(20) # gives an implicit wait for 20 seconds
        self.wd.get(url)

    """
    Get the webdriver if it is needed outside this class
    """
    def get_webdriver(self) -> webdriver:
        return self.wd

    """
    Gordon's method, currently not working. Probably can remove
    """
    def get_price(self) -> float:
        #search = self.wd.find_element(By.CLASS_NAME, "bet-button-price")
        price = self.wd.find_element(By.XPATH, "//*[@id="+'"'+'"bm-content"'+"]/div[2]/div/div[2]/div[2]/div[4]/button/div")
        return price

    """
    Test method, currently unused
    """
    def goto_first_race(self) -> None:
        next_race = self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[2]/div[2]/div[1]')
        self.wd.execute_script(CLICK, next_race)

    """
    Creates a list of every upcoming race from the upcoming races page on BETR. Hopefully classname doesn't change a lot or this will be a bad way to do it
    """
    def get_all_upcoming_races(self) -> list:
        #First grab the container of all the races
        races_container = self.wd.find_element(By.CLASS_NAME, "RaceUpcoming_grid__6YRbf")

        #From container, get every child
        races_list = races_container.find_elements(By.CLASS_NAME, "RaceUpcoming_row__rS63w")
        return races_list

if __name__ == "__main__":
    load_dotenv()
    path = os.environ.get("PATH")
    browserController = BrowserController(path, URL)
    #price = browserController.get_price()
    #print(price)
    #browserController.goto_first_race()
    browserController.get_all_upcoming_races()
    time.sleep(8)
