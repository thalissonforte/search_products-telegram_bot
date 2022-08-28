from dotenv import load_dotenv
from src.driveBot import DriveBot
import os
import requests
import json

load_dotenv()

texto_cumprimentos = ['oi', 'oie', 'ola', 'eai', 'opa', 'tudo bem?', 'como vai?', '/start']

texto_whey = ['whey', 'whey protein', 'wheys']
texto_creatina = ['creatina', 'crea']
texto_pretreino = ['pré treino', 'pre treino', 'pre-treino', 'pré-treino', 'pré', 'prétreino', 'pretreino']
texto_paradinhas = ['paradinhas', 'outras paradas', 'paradas']

class TelegramBot:
    def __init__(self):
        TOKEN = os.getenv("API_KEY")
        self.url = f'https://api.telegram.org/bot{TOKEN}/'
        self.driveBot = DriveBot()

    def Start(self):
        update_id = None
        self.df = self.driveBot.getData()
        self.TransformDF(self.df)

        while True:
            update = self.GetMessage(update_id)
            messages = update['result']
            if messages:
                for message in messages:
                    try:
                        update_id    = message['update_id']
                        chat_id      = message['message']['from']['id']                        
                        message_text = message['message']['text']
                        answer_bot   = self.CreateAnswer(message_text)
                        self.SendAnswer(chat_id, answer_bot)
                        print(message)
                    except:
                        pass


    def CreateAnswer(self, message_text):
        message_text = message_text.lower()
        print("Recebi uma mensagem: " + message_text) 
        if any(msg in message_text for msg in texto_cumprimentos):
            return "Eai meu rei, com o que posso te ajudar?"
        elif any(msg in message_text for msg in texto_whey):
            msg = f"Achei {str(self.wheys.shape[0])} opções kkkkkkk ta maluco"
            return msg
            #return(self.wheys.to_string())
        elif any(msg in message_text for msg in texto_creatina):
            msg = f"Achei {str(self.creatinas.shape[0])} opções da braba, mas ainda nao sei quantas tem em estoque :/"
            return msg
            #return self.creatinas.loc[0].to_string()
            #return(self.creatinas.to_string())
        elif any(msg in message_text for msg in texto_pretreino):
            msg = f"{str(self.pre_treinos.shape[0])} opções pra ficar maluco de pré treino"
            return msg
            #return self.pre_treinos.loc[0].to_string()
            #return(self.pre_treinos.to_string())
        else:
            return 'Não entendi oq tu mandou :( Music is the answer!'
        
        return 'Hehe'

    def TransformDF(self, df):
        # WHEYS
        self.wheys = df[(df['CATEGORIAS'].str.contains('WHEY PROTEIN'))]
        # CREATINA
        self.creatinas = df[(df['CATEGORIAS'].str.contains('CREATINA'))]
        # PRE TREINO
        self.pre_treinos = df[(df['CATEGORIAS'].str.contains('PRÉ TREINO'))]
        return


    def GetMessage(self, update_id):
        linkRequest = f'{self.url}getUpdates?timeout=1000'
        if update_id:
            linkRequest = f'{linkRequest}&offset={update_id + 1}'            

        result = requests.get(linkRequest)
        return json.loads(result.content)

    
    def SendAnswer(self, chat_id, answer):
        send_link = f'{self.url}sendMessage?chat_id={chat_id}&text={answer}'
        requests.get(send_link)
        return