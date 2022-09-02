from dotenv import load_dotenv
import gspread
import json
import os
import pandas as pd
import boto
load_dotenv()

class DriveBot:
    def __init__(self):
        self.SHEET_URL_KEY = os.environ['SHEET_URL_KEY']
        self.gc = gspread.service_account_from_dict(json.loads(os.environ['GOOGLE_CREDENTIALS']))

    def getData(self, bOnlyIfEstoque = False, bForceAndSave = False):
        # BASE OBTIDA A PARTIR DE ARQUIVO OU REQUISICAO
        if (not bForceAndSave) and (os.path.isfile('base.csv')):
            df = pd.read_csv('base.csv')
            # TRANSFORMACAO
            df = self.DataFrameTransformation(df) 
            print('Dataframe carregado por arquivo.')
        else:
            print('Requisitando dados do Google Sheets...')
            sh = self.gc.open_by_key(self.SHEET_URL_KEY)
            worksheet = sh.sheet1
            # OBTENCAO E TRANSFORMACAO PARA DATAFRAME COM OS HEADERS CORRETOS E TIPOS CORRETOS
            df = pd.DataFrame(worksheet.get_values('B8:E'))
            df.columns = df.iloc[0]
            df = df[1:-1]
            df['ESTOQUE'] = pd.DataFrame(worksheet.get_values('H8:H'))
            # TRANSFORMACAO
            df = self.DataFrameTransformation(df, bLoadedFromFile=False) 
            # SALVA NO CSV
            df.to_csv('base.csv', index=None)
            print('Dataframe salvo em arquivo.') 

        if bOnlyIfEstoque:
            df = df[df['ESTOQUE'] > 0]        
        return df

    def DataFrameTransformation(self, df, bLoadedFromFile = True):
        # LIMPA NAN
        df['ESTOQUE'] = df['ESTOQUE'].fillna(0)
        if not bLoadedFromFile:
            # LIMPA VAZIOS
            df.loc[df['ESTOQUE'].str.len() < 1, 'ESTOQUE'] = '0'
        # CONVERTE
        df['ESTOQUE'] = df['ESTOQUE'].astype(int)
        #LIMPA COLUNAS
        df = df[df['CATEGORIAS'].map(len) > 1]
        return df