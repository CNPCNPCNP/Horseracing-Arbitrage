#CONSTANTS. Use all capitals to define global constants please
import re

URL = 'https://betr.com.au/racebook#/racing/home/upcoming'
CLICK = "arguments[0].click();"
ICON_CSS_SELECTOR = '#bm-content > div.AuthoringLayout_container__N5HOH > div > div.HomeContainer_container__85Qcf > div > div > div:nth-child(1) > button > svg.Icon_icon__zcHyd.Icon_medium__8Hw0y > path'
HORSE_ICON = 'M13.1346'
TROT_ICON = 'M14.9389'
GREYHOUND_ICON = 'M2.73859'
WIN_MARKET_REGEX = re.compile(r'^R\d+$')