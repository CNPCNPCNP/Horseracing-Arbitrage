import string

from constants import *
from race import Race, RaceType
from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

"""
Main controller class for building our list of races
"""
class RaceBuilder():

    """
    Creates a browser controller with the associated webdriver and URL path. Use self.wd inside this class to access 
    webdriver. Takes path as an input, so make sure you have the PATH variable setup in your .env file. If you need to 
    access the webdriver outside this class, use the getter method get_webdriver. Uses betfair controller to get the
    market id and betfair url for each race as well. Races specifies the number of races to track. Tracking more races
    uses more threads
    """
    def __init__(self, path: str, url: str, races: int) -> None:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.wd = webdriver.Chrome(service = Service(path), options = options)
        self.wd.maximize_window() # For maximizing window
        self.wd.implicitly_wait(3) # gives an implicit wait for 2 seconds
        self.wd.get(url)

        self.url = url
        self.races = races

    """
    Creates a list of every upcoming race from the upcoming races page on BETR. Hopefully classname doesn't change a lot 
    or this will be a bad way to do it
    """
    def get_all_upcoming_races(self) -> list:
        races = self.wd.find_elements(By.CLASS_NAME, "RaceUpcoming_row__rS63w")
        return races

    """
    Goes to every race on the upcoming races page and then returns a list of Races and their details
    """
    def goto_every_race(self) -> list[Race]:
        self.wd.implicitly_wait(1)
        races = []
        index = 0
        # Had issues with trying to iterate over list normally with for loop, so reload the race list every time and 
        # access each race by index. Inefficient but it works fine. Only scraping 5 races at this stage, may scrape more
        # if this approach is successful.
        while len(races) < self.races and index < 19:
            races_links = self.get_all_upcoming_races()
            self.wd.execute_script(CLICK, races_links[index])
            
            race = self.get_prices_from_race_page()
            if race.valid_race():
                races.append(race)
            self.wd.back()
            index += 1
        return races

    """
    Starting with the webdriver on a race page, creates a dictionary of every horse name and its current starting price
    """
    def get_prices_from_race_page(self) -> Race:
        horses = self.wd.find_elements(By.CLASS_NAME, "RunnerDetails_competitorName__UZ66s")
        prices = self.wd.find_elements(By.CLASS_NAME, "OddsButton_info__5qV64")

        # Race name is location + race number
        venue = self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[1]/ul/li[2]/a').text
        venue = VENUES.get(venue) # Gives us None if no equivalent venue on betfair
        try:
            race_number = int(self.wd.find_element(By.XPATH, '//*[@id="bm-content"]/div[2]/div/div[1]/ul/li[3]/a').text.split(" ")[-1])
        except NoSuchElementException:
            print("Unable to determine race number")
            race_number = 0 # Use sentinel value of 0 for races where we can't determine number, will skip matching later
        except ValueError:
            print("Found wrong value for race number?")
            race_number = 0

        # Get url so we can access the race later to bet
        url = self.wd.current_url
        
        # Can extract SVG (icon) to get type of race. Annoyingly no text on page stating race type so this method is 
        # overly complex
        try:
            race_icon = self.wd.find_element(By.CSS_SELECTOR, ICON_CSS_SELECTOR).get_attribute('d').split(" ", 1)[0]
            if race_icon == HORSE_ICON:
                race_type = RaceType.HORSE_RACE
            elif race_icon == TROT_ICON:
                race_type = RaceType.TROT_RACE
            else:
                race_type = RaceType.GREYHOUND_RACE
        except NoSuchElementException:
            race_icon = None
            race_type = RaceType.UNKNOWN_RACE

        race_summary = {}

        # Shrink horse list to match number of prices to account for scratched horses
        if len(prices) <= 4:
            horses = horses[:len(prices)]
        else:
            horses = horses[:len(prices) // 2]
        
        for index, horse in enumerate(horses):
            # Split the text into the horses number and the rest of the text on the first space
            horse_number, remainder = horse.text.split(" ", 1)
            # Split once from the right to get gate separate from horse name. This avoids edge case where there are 
            # spaces in the horses name
            horse_name, gate = remainder.rsplit(" ", 1)
            horse_name = horse_name.translate(str.maketrans('', '', string.punctuation)) # Remove punctuation from horse names
            gate = int(gate[1:-1]) #Remove brackets from gate

            # Get current price of horse. The div number seems to be separated by 6 each time starting from 4
            number = index * 6 + 4

            # Need to handle exceptions as sometimes the races don't have prices? Probably a neater way to do this
            try:
                price = self.wd.find_element(By.XPATH, f"//*[@id='bm-content']/div[2]/div/div[2]/div[2]/div[{number}]/button/div/span[2]")
            except NoSuchElementException:
                # If the element does not exist, skip this race
                break
            
            race_summary[horse_name] = float(price.text)
        return Race(venue, race_number, race_summary, url, race_type)
    