import selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By

# file path for chrome webdriver
PATH = "C:\Program Files (x86)\chromedriver.exe"

#url for example BETR race. 
url = 'https://www.betfair.com.au/exchange/plus/en/football/fifa-world-cup/winner-2022-betting-1.145970106' 

#selenium web driver to test accessing BETR site 
wd = webdriver.Chrome('chromedriver')
wd.maximize_window() # For maximizing window
wd.implicitly_wait(20) # gives an implicit wait for 20 seconds
wd.get(url)


# I can't seem to toggle with this command to return where the odds for the horse are :(, currently yields an erorr
price_of_horsey= wd.find_element(By.XPATH, "//*[@id="+'"'+'"bm-content"'+"]/div[2]/div/div[2]/div[2]/div[4]/button/div")

