import random
import os

from race import Race

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By

class BetPlacementController():
    def __init__(self, url: str, betrUsername: str, betrPassword: str,  race: Race):
        wd = uc.Chrome()
        wd.get(url)

username = os.environ.get("BETR_USERNAME")
password = os.environ.get("BETR_PASSWORD")