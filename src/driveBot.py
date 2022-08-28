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

    def getData(self, bOnlyIfEstoque = False, bForceAndSave = False):
        if (not bForceAndSave) and (os.path.isfile('base.csv')):
            df = pd.read_csv('base.csv')
            print('Dataframe carregado por arquivo.')
        else:
            print('Requisitando dados do Google Sheets.')
            sh = self.gc.open_by_key(self.SHEET_URL_KEY) #SHEET URL KEY
            worksheet = sh.sheet1
            # OBTENCAO E TRANSFORMACAO PARA DATAFRAME COM OS HEADERS CORRETOS E TIPOS CORRETOS
            df = pd.DataFrame(worksheet.get_values('B8:E'))
            df.columns = df.iloc[0]
            df = df[1:-1]
            df['ESTOQUE'] = pd.DataFrame(worksheet.get_values('H8:H'))
            df = df[df['CATEGORIAS'].map(len) > 1]

            df.to_csv('base.csv', index=None)
            print('Dataframe salvo em arquivo.') 

        if bOnlyIfEstoque:
            df = df[df['ESTOQUE'] != '0']        

        return df

