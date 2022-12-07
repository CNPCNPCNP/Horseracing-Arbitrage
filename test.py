import pandas as pd
from datetime import datetime

fake = {1: ['1', '2'], 2: ['2', '3'], 3: ['3', '4']}

current = datetime.now()
comparison = pd.DataFrame([fake], index=[current.strftime('%d-%m-%Y_%H:%M:%S')])

print(comparison)