import requests
import csv
from datetime import datetime, timedelta
import os
import json
import holidays
import logging
import shutil
import datetime

#Obtém a data e hora atuais e formata no formato desejado
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%d%m%Y_%H%M")

#Caminho do arquivo de log com o timestamp incluído
log_file_path = f"C:\\digite\\seu\\repositorio\\cotacao_moedas\\logs\\log_{formatted_time}.txt"

#Configurando o logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s: %(message)s')

try:
    #Extraindo feriados do Brasil
    br_holidays = holidays.Brazil()

    #Pegando a data atual
    today = datetime.datetime.now()

    #Verificando se é terça, quarta, quinta, sexta ou sábado
    if today.weekday() in [0, 1, 2, 3, 4] and today not in br_holidays:
        #Condição caso seja um dos dias acima
        pass
        logging.info("Validado o dia de execução. Seguindo com o processo...")

        #Função para obter a data atual no formato dd/MM/yyyy
        def get_formatted_date(date):
            return date.strftime("%d/%m/%Y")

        #Data atual e a data anterior
        tomorrow = today + timedelta(days=1)

        #Formatando as datas conforme necessário
        data_ini = get_formatted_date(today)
        data_fim = get_formatted_date(tomorrow)

        #URL do Banco Central para cotação de Yuan com as datas de início e fim
        url_yuan = f"https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=178&DATAINI={data_ini}&DATAFIM={data_fim}"
        url_selic = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados?formato=csv&dataInicial={data_ini}&dataFinal={data_ini}"

        #Download do arquivo CSV da cotação Yuan
        response = requests.get(url_yuan)

        #Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            #Abre o arquivo CSV
            with open("CotacoesMoedasPeriodo.csv", "wb") as f:
                f.write(response.content)
                logging.info("Download CSV cotação Yuan realizado")

            #Abre o arquivo CSV e converte para TXT
            with open("CotacoesMoedasPeriodo.csv", "r", newline='') as csv_file:
                with open("CotacoesMoedasPeriodo.txt", "w") as txt_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        txt_file.write(','.join(row) + '\n')
                        logging.info("Conversão para TXT cotação Yuan realizado")
        else:
            print("Falha ao baixar o arquivo CSV.")
            logging.info("Download CSV cotação Yuan não efetuado")

        #Excluindo o arquivo CSV
        os.remove("CotacoesMoedasPeriodo.csv")
        logging.info("CSV cotação Yuan excluído")

        #Alterando o TXT e extraindo a cotação Yuan
        with open("CotacoesMoedasPeriodo.txt", "r") as txt_file:
            content = txt_file.read()    
            lines = content.split("\n")
        
            cotacao_cny = None
            for line in lines:
                campos = line.split(";")
                if "CNY" in campos:
                    indice_cny = campos.index("CNY")

                    #Verifica se há um campo após "CNY"
                    if indice_cny + 1 < len(campos):
                        cotacao_cny = campos[indice_cny + 1]
                        break
                    if 'cotacao_cny' in row:
                        encontrou_valor = True

            #Exibe o valor encontrado
        if cotacao_cny is None:
                print("Valor 'cotacao_cny' não encontrado.")
                logging.info("Valor Taxa Selic não encontrado.")
        else:
            print("Falha ao baixar o arquivo CSV.")
            logging.info("Download CSV Yuan não efetuado")
            
        cotacao_cny_float = float(cotacao_cny.replace(',', '.'))

        cotacao_yuan = round(cotacao_cny_float, 4)
        logging.info("Cotação Yuan extraída.")
        
        #Excluindo o arquivo TXT
        os.remove("CotacoesMoedasPeriodo.txt")
        logging.info("TXT cotação Yuan excluído.")

        #Download do arquivo CSV da Taxa Selic
        response = requests.get(url_selic)

        #Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            #Salva o arquivo CSV
            with open("bcdata.sgs.1178.csv", "wb") as f:
                f.write(response.content)
                logging.info("Download CSV Taxa Selic realizado.")

            #Lê o arquivo CSV e procura pelo valor desejado
            with open("bcdata.sgs.1178.csv", "r", newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                selic = None
                encontrou_valor = False
                for row in csv_reader:
                    if encontrou_valor:
                        selic = row[1]  #Assumindo que o valor desejado está na segunda coluna
                        break
                    if 'valor' in row:
                        encontrou_valor = True

            #Exibe o valor encontrado
            if selic is None:
                print("Valor 'valor' não encontrado.")
                logging.info("Valor Taxa Selic não encontrado.")
        else:
            print("Falha ao baixar o arquivo CSV.")
            logging.info("Download CSV Taxa Selic não efetuado")

        taxa_selic = float(selic.replace(',', '.'))
        logging.info("Taxa Selic extraída.")

        #Excluindo o arquivo CSV
        os.remove("bcdata.sgs.1178.csv")
        logging.info("CSV Taxa Selic excluído.")

        def obter_cotacao_moedas(data_cotacao):
            #Formata a data no formato necessário para a API
            hoje = data_cotacao.strftime('%m-%d-%Y')

            #Obter a data do dia seguinte
            data_do_dia_seguinte = data_cotacao + timedelta(days=1)

            #Formatar a data no formato mm-DD-yyyy
            amanha = data_do_dia_seguinte.strftime('%m-%d-%Y')
            
            #URL da API do Banco Central para cotação do Dólar - Compra e Venda
            url_dolar = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{hoje}'&$top=100&$format=json&$select=cotacaoCompra,cotacaoVenda"
            resposta_dolar = requests.get(url_dolar)
            dados_dolar = resposta_dolar.json()

            #URL da API do Banco Central para cotação do Euro - Compra
            url_euro = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodoFechamento(codigoMoeda=@codigoMoeda,dataInicialCotacao=@dataInicialCotacao,dataFinalCotacao=@dataFinalCotacao)?@codigoMoeda='EUR'&@dataInicialCotacao='{hoje}'&@dataFinalCotacao='{hoje}'&$format=json&$select=cotacaoCompra,cotacaoVenda"
            resposta_euro = requests.get(url_euro)
            dados_euro = resposta_euro.json()

            #Extrai informações das cotações
            cotacao_dolar = dados_dolar['value'][0] if dados_dolar['value'] else None
            cotacao_euro = dados_euro['value'][0] if dados_euro['value'] else None

            return cotacao_dolar, cotacao_euro

    #Uso da função
    from datetime import date, timedelta

    data_cotacao = date.today()
    dolar, euro = obter_cotacao_moedas(data_cotacao)

    if dolar and euro:
        print(f"Dólar: Compra {dolar['cotacaoCompra']}, Venda {dolar['cotacaoVenda']}")
        print(f"Euro: {euro['cotacaoCompra']}")
        print(f"Yuan: {cotacao_yuan}")
        print(f"Taxa Selic: {taxa_selic}")

        with open('cotacoes_bacen.txt', 'w') as arquivo:
            arquivo.write(f"{dolar['cotacaoCompra']},{dolar['cotacaoVenda']},{euro['cotacaoCompra']},{cotacao_yuan},{taxa_selic}")

        generated_file_path = "cotacoes_bacen.txt"
        destination_path = "C:\\digite\\seu\\repositorio\\cotacao_moedas\\"
        logging.info("Criando o arquivo cotacoes_bacen.")

            #Caminho para o arquivo 'cotacao_sgd.txt'
        path_cotacao_sgd = "C:\\digite\\seu\\repositorio\\cotacao_moedas\\\cotacao_sgd.txt"      
            #Ler o conteúdo do arquivo 'cotacao_sgd.txt'
        with open(path_cotacao_sgd, 'r') as file_sgd:
            conteudo_sgd = file_sgd.read().strip()
            print(f"Dólar SGD: {conteudo_sgd}")
            logging.info("Lendo o arquivo cotacao_sgd.")

            #Ler o conteúdo do arquivo 'cotacoes_bacen.txt'
        with open('cotacoes_bacen.txt', 'r') as file_cotacoes:
            conteudo_cotacoes = file_cotacoes.read().strip()
            logging.info("Lendo o arquivo cotacoes_bacen.")

            #Combinar os conteúdos
        cotacoes = conteudo_sgd + "," + conteudo_cotacoes
        logging.info("Combinando arquivos TXTs.")

            #Escrever o conteúdo combinado de volta em um arquivo (pode ser um dos existentes ou um novo)
        with open(C:\\digite\\seu\\repositorio\\cotacao_moedas\\cotacao.txt", 'w') as file_new:
            file_new.write(cotacoes)
            logging.info("Arquivos combinados com sucesso.")

            #Movendo o arquivo gerado para o destino especificado
        shutil.move(file_new, destination_path)
        logging.info("Arquivo gerado movido com sucesso.")

        #Excluindo o arquivo cotacoes_bacen.txt
        os.remove("cotacoes_bacen.txt")
        logging.info("O .txt cotacoes_bacen foi excluído.")       

    else:
            #Caso seja domingo, segunda ou feriado, o script termina aqui
            print("Hoje é domingo, segunda-feira ou feriado. O script não será executado.")
            logging.info("Validado o dia de execução. O script não será executado.")
            exit()

        #Adicionando log para indicar o final da execução do script
    logging.info("Execução do script finalizada.")

except Exception as e:
    logging.error("Erro durante a execução do script: %s", e)
