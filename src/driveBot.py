from dotenv import load_dotenv
import gspread
import json
import os
import pandas as pd
load_dotenv()

class DriveBot:
    def __init__(self):
        self.SHEET_URL_KEY = os.getenv('SHEET_URL_KEY')
        self.gc = gspread.service_account(filename='credentials.json')

    def getData(self):
        sh = self.gc.open_by_key(self.SHEET_URL_KEY) #SHEET URL KEY
        worksheet = sh.sheet1
        dataframe = pd.DataFrame(worksheet.get_all_values())
        return dataframe