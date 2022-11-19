import time
import os

from race import Race
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
        self.wd.implicitly_wait(1) # gives an implicit wait for 20 seconds
        self.wd.get(url)

    """
    Get the webdriver if it is needed outside this class
    """
    def get_webdriver(self) -> webdriver:
        return self.wd

    """
    Gordon's method, currently not working. Probably can remove but really shouldn't. Don't want to take away what little he has in these trying times. 
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
        races = races_container.find_elements(By.CLASS_NAME, "RaceUpcoming_row__rS63w")
        return races

    """
    Goes to every race on the upcoming races page and then goes back
    """
    def goto_every_race(self) -> list[Race]:
        races_summary = []
        #Had issues with trying to iterate over list normally with for loop, so reload the race list every time and access each race by index. Inefficient but it works fine
        for race_number in range(20):
            races = self.get_all_upcoming_races()
            self.wd.execute_script(CLICK, races[race_number])
            
            race_summary = self.get_prices_from_race_page()
            if race_summary.get_horses():
                races_summary.append(race_summary)
            self.wd.back()
        
        return races_summary

    """
    Starting with the webdriver on a race page, creates a dictionary of every horse name and its current starting price
    """
    def get_prices_from_race_page(self) -> Race:
        horses = self.wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = self.wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")

        #Race name is location + race number
        race_location = self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[1]/ul/li[2]/a').text
        race_number = int(self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[1]/ul/li[3]/a').text.split(" ")[-1])
        print(race_location, race_number)

        race_summary = {}

        #Shrink horse list to match number of prices to account for scratched horses
        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]
        
        for index, horse in enumerate(horses):
            #Split the text into the horses number and the rest of the text on the first space
            number, remainder = horse.text.split(" ", 1)
            #Split once from the right to get gate separate from horse name. This avoids edge case where there are spaces in the horses name
            horse_name, gate = remainder.rsplit(" ", 1)
            gate = int(gate[1:-1])

            #Get current price of horse. For some reason the div number seems to be separated by 6 each time starting from 4
            number = str(index * 6 + 4)

            #Need to handle exceptions as sometimes the races don't have prices? Probably a neater way to do this
            try:
                price = self.wd.find_element(By.XPATH, f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]")
            except NoSuchElementException:
                #If the element does not exist, skip this race
                print("Exception, skipping this race")
                break
            
            race_summary[(horse_name, gate)] = float(price.text)
        return Race(race_location, race_number, race_summary)

if __name__ == "__main__":
    load_dotenv()
    path = os.environ.get("PATH")
    browserController = BrowserController(path, URL)
    races_summary = browserController.goto_every_race()

    print(races_summary)
    time.sleep(8)

    