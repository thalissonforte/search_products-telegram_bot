from dotenv import load_dotenv
from src.driveBot import DriveBot
import os
import requests
import json
from collections import OrderedDict

load_dotenv()

texto_cumprimentos = ['OI', 'OIE', 'OLA', 'EAI', 'EAE', 'OPA', 'TUDO BEM?', 'COMO VAI?', '/START', 'FALA', 'SALVE', 
                      'BOM DIA', 'BOA TARDE', 'BOA NOITE']

texto_paradinhas   = ['PARADA', 'PARADAS', 'PARADINHAS', 'PARADINHA', 'BOMBA', 'VENENO']

categorias_fixas = ['WHEY PROTEIN', 'CREATINA', 'PRÉ TREINO', 'ALBUMINA', 'VITAMINA', 'HIPERCALÓRICO', 
                    'TERMOGÊNICO', 'CAFEÍNA', 'GLUTAMINA', 'BARRA DE PROTEÍNA', 'COLÁGENO', 'GLUTAMINA',
                    'BCAA', 'HIPERPROTÉICO', 'CAMISETA', 'COQUETELEIRA', 'MULTIVITAMÍNICO', 'L-CARTININA',
                    'MALTODEXTRINA', 'ÔMEGA 3', 'TERMOGÊNICO', 'PASTA DE AMENDOIM']

marcas_prioritarias = ['INTEGRAL MÉDICA', 'MAX TITANIUM', 'PROBIÓTICA', 'DARKNESS', 'BLACK SKULL', 
                        'NUTRATA', 'DUX NUTRITION', 'ATHLETICA NUTRITION', 'NATUROVOS', 'HEALTHTIME', 
                        '3VS', 'BODY ACTION', 'FTW SPORTS']

comando_forcar_carregamento = ['/ATUALIZARPLANILHA']

nLimitProducts = 10
class TelegramBot:
    def __init__(self):
        TOKEN = os.environ["API_KEY"]
        self.WHITELIST = str(os.environ["USERS_ID"]).split(':')
        print(self.WHITELIST)
        self.url = f'https://api.telegram.org/bot{TOKEN}/'
        self.driveBot = DriveBot()

    def Start(self):
        update_id = None
        # INICIAR DRIVE BOT (AQUI VERIFICAR SE PRECISA FORÇAR ATUALIZACAO)
        self.df = self.driveBot.getData()
        self.dictCategoriesDF = dict()
        self.CreateCategories(self.df) 

        while True:
            update = self.GetMessage(update_id)
            messages = update['result']
            if messages:
                print(messages)
                for message in messages:
                    try:
                        update_id    = message['update_id']
                        chat_id      = message['message']['from']['id']                        
                        message_text = message['message']['text']

                        if str(chat_id) in self.WHITELIST:
                            # CRIAR RESPOSTA
                            answer_bot   = self.CreateAnswer(message_text)
                            self.SendAnswer(chat_id, answer_bot, parse_mode='HTML')
                        else:
                            answer_bot   = 'Você não possui permissões para fazer requisições.'
                            #self.SendAnswer(chat_id, answer_bot, parse_mode='HTML')
                            pass
                        #print(answer_bot)
                    except:
                        pass


    def CreateAnswer(self, message):
        #print("Recebi uma mensagem: " + message)
        message = message.upper()
        #TRATAMENTO DA MENSAGEM
        text_splitted = message.split(' ')
        # BLOQUEIO DE PROTECAO
        if len(text_splitted) > 10:
            return 'Bloqueio de proteção: Excesso de informações digitadas.'
        elif len(text_splitted) < 1:
            return 'Bloqueio de proteção: Falta de informações.' 

        if (message in comando_forcar_carregamento):
            self.driveBot.getData(bForceAndSave=True)
            return "Planilha atualizada com sucesso!"
        if any(msg in texto_cumprimentos for msg in text_splitted):
            return "Eai meu rei, com o que posso te ajudar?"
        elif any(msg in texto_paradinhas for msg in text_splitted):
            return "\U0001F608	\U0001F608	\U0001F489 \U0001F489 "
        #elif message == '1':
            #aux = self.ConfigureResposta(self.produtosTemporarios, offset=nLimitProducts, bViewAll=True)
            #print(aux)
            #return aux
        else:
            self.produtosTemporarios = None
            self.produtosTemporarios = self.ProcessMessage(message)
            if (self.produtosTemporarios != -1):
                bRemainProducts = False
                if len(self.produtosTemporarios) > nLimitProducts:
                    bRemainProducts = True

                return self.ConfigureResposta(self.produtosTemporarios, bRemainProducts=bRemainProducts)
            else:
                return 'Não consegui achar nenhum produto aqui, me manda mais informações.'

    def GetMessage(self, update_id):
        linkRequest = f'{self.url}getUpdates?timeout=1000'
        if update_id:
            linkRequest = f'{linkRequest}&offset={update_id + 1}'            
        result = requests.get(linkRequest)
        return json.loads(result.content)

    
    def SendAnswer(self, chat_id, answer, parse_mode='Markdown'):
        send_link = f'{self.url}sendMessage?chat_id={chat_id}&text={answer}&parse_mode={parse_mode}'
        requests.post(send_link)
        return

    # CRIAR LISTAS BASEADAS NAS CATEGORIAS
    def CreateCategories(self, df):
        for cat in categorias_fixas:
            items = df[(df['CATEGORIAS'].str.contains(cat))]
            self.dictCategoriesDF[cat] = items
        return 

    # ACHAR CATEGORIA
    def FindCategory(self, text_splitted):                
        for cat in categorias_fixas:
            for text in text_splitted:
                if text in cat:
                    return cat
        return -1

    # ACHAR MARCA
    def FindMarca(self, text_splitted):
        for marca in marcas_prioritarias:
            for text in text_splitted:
                if text in marca:
                    return marca
        return -1

    # ACHAR PRODUTOS ORDENADOS
    def FindProduto(self, text_splitted, df = None, bHasCategoria = False, bHasMarca = False):
        items_encontrados = dict()
        if not df.empty:
            for row in df.itertuples():                
                produto = row[1]
                count = 0
                for text in text_splitted:                    
                    if text in produto:
                        count += 1
                    
                if (count > 0) or (bHasCategoria and bHasMarca):
                    id = row[0]                  
                    items_encontrados[id] = [count, row]
        #else: FAZER PIOR CASO, SEM CATEGORIA E SEM MARCA

        bOrdenarItems = len(text_splitted) > 1
        if bOrdenarItems:
            items_encontrados_ordenados = dict()
            for item in sorted(items_encontrados, key = items_encontrados.get, reverse=True):
                items_encontrados_ordenados[item] = items_encontrados[item]

            if len(items_encontrados_ordenados) > 0:
                return items_encontrados_ordenados
        else:
            return items_encontrados 
        return -1

    # PROCESSA MENSAGEM
    def ProcessMessage(self, msg):
        # VERIFICANDO NOVAMENTE A MENSAGEM POR QUESTOES DE PROTECAO
        msg = msg.upper()
        #TRATAMENTO DA MENSAGEM
        text_splitted = msg.split(' ')
        # BLOQUEIO DE PROTECAO
        if len(text_splitted) > 10:
            print('Bloqueio de proteção. Excesso de informação digitada.')
            return -1
        elif len(text_splitted) < 1:
            print('Bloqueio de proteção. Falta de informações.')
            return -1

        # ENCONTRANDO INFORMACOES
        categoria = self.FindCategory(text_splitted)
        marca = self.FindMarca(text_splitted)
        produtos = -1
        if categoria != -1:
            print(categoria)
            df_especifico = self.dictCategoriesDF[categoria]
            if marca != -1:
                print(marca)
                df_especifico = df_especifico[df_especifico['MARCAS'].str.contains(marca)]
                produtos = self.FindProduto(text_splitted, df_especifico, bHasCategoria=True, bHasMarca=True)
            else:
               produtos = self.FindProduto(text_splitted, df_especifico, bHasCategoria=True) 
        #else: O PIOR CASO QUANDO NAO TEM CATEGORIA TO-DO
        return produtos

    # CONFIGURAR RESPOSTA
    def ConfigureResposta(self, produtos, offset = 0, bRemainProducts = False, bViewAll=False):       
        productsAdded = 0
        resp = f'\U000026A1	Achei alguns produtos: \U000026A1\n' 
        print(f'Visualizar todos = {bViewAll}')
        nOffsetUsed = 0
        for prod in produtos.values():
            #if nOffsetUsed < offset:
                #nOffsetUsed = nOffsetUsed + 1
                #pass

            nome = (prod[1])[1]
            marca = (prod[1])[2]
            custo = (prod[1])[4]
            estoque = (prod[1])[5]
            
            
            if int(estoque) < 1:
                if (not bViewAll): # SE FOR PARA VISUALIZAR TODOS, MOSTRAR SOMENTE OS QUE TEM ESTOQUE
                    resp = f'{resp}\n\U0000274C <s>{nome}: {marca}</s> \n\U0000274C <s>Sem estoque</s>\n'
            else:
                dCusto = float(custo.replace('R$ ','').replace(',','.'))
                dVenda = round(dCusto * 1.25, 2)
                resp = f'{resp}\n<b>{nome}</b>: {marca} \n\U0001F4E6	{estoque} em estoque \n\U0001F4B5	Custo: {custo} \n\U00002705 Sugestão de venda <b>(25%)</b>: <b>R$ {dVenda}</b>\n'

            productsAdded = productsAdded + 1

            if (not bViewAll) and (productsAdded >= nLimitProducts):
                break
        
        if productsAdded > 0:
            if bRemainProducts:
                resp = f'{resp}\n\U0001F9D0	Não achou o que queria? \n\U0001F4A1	Manda <b>mais informações juntas</b> que eu posso te ajudar...'
            else:
                resp = f'{resp}\n\U0001F9D0	Isso foi tudo o que encontrei! \n\U0001F4A1	Manda <b>mais informações juntas</b> caso não tenha encontrado o que queria...'
            return resp
        else:
            return 'Nada encontrado.'

    def teste(self):
        # INICIAR DRIVE BOT (AQUI VERIFICAR SE PRECISA FORÇAR ATUALIZACAO)
        self.df = self.driveBot.getData()
        self.dictCategoriesDF = dict()
        self.CreateCategories(self.df) 

        #print(self.CreateAnswer('eai'))
        #self.CreateAnswer(f'whey')
        #self.CreateAnswer(f'1')
        #print(self.CreateAnswer(f'/atualizarplanilha'))
        #print(self.CreateAnswer(f'whey'))
