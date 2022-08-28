from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

cumprimentos = ['oi', 'oie', 'ola', 'eai', 'tudo bem?', 'como vai?']

class TelegramBot:
    def __init__(self):
        TOKEN = os.getenv("API_KEY")
        self.url = f'https://api.telegram.org/bot{TOKEN}/'

    def start(self):
        update_id = None

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
        if message_text in cumprimentos:
            return "Eai meu rei, com o que posso te ajudar?"
        else:
            return 'Não entendi o que tu falou. Music is the answer!'

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