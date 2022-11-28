import random

from race import Race

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By

class BetPlacementController():
    def __init__(self, url: str, betrUsername: str, betrPassword: str,  race: Race):
        wd = uc.Chrome()
        wd.get(url)
        pass