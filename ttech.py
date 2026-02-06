import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
def getCurrrency():
    url = "https://www.cbr.ru/"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        curr = soup.find_all('div', class_ = "main-indicator_rates-table")
        

        for i, indicator in enumerate(curr, 1):
            # Получаем весь текст внутри div
            text = indicator.get_text().replace('\t', '').replace("Официальный курс Банка России", "").replace('', '')
            text = ' '.join(text.split())
            res = text[:33] + "\n\n"
            for i in text[34:]:
                if i == "¥" or i == "₽" or i == "$" or i == '€':
                    res += i.replace(i, i+"\n", 1)
                else: 
                    res += i
                    
            res = res.replace("\n"+" ", "\n")
            return res
            

    except Exception as e:
        return e

def getRateKey():
    url = "https://www.cbr.ru/"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        div = None
        # Ищем элемент с ключевой ставкой (структура может меняться)
        all_indicators = soup.find_all('div', class_='main-indicator')

        

        # Способ 1: Простая фильтрация по тексту
        for i, indicator in enumerate(all_indicators, 1):
            # Получаем весь текст внутри div
            text = indicator.get_text()
            
            if 'Ключевая ставка' in text:
                div = indicator.prettify()
                if "%" in div: return div[315:321]
                break
    except Exception as e:
        print (e)





def getInflation():
    url = "https://cbr.ru/hd_base/infl/"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all('table', class_ = "data")
        
        for i, indicator in enumerate(table, 1):
            # Получаем весь текст внутри div
            
            text = indicator.get_text().replace("\n", " | ").replace(" |  | ", "\n")
            text = text.replace("Дата | Ключевая ставка, % годовых | Инфляция, % г/г | Цель по инфляции, %", " | Дата | Кл. ствка | Инфляция ", 1)
            text = text.replace("| 4,00", "")
        return text
    except Exception as e:
        return e



def moex():

    # Получить все акции
    url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
    response = requests.get(url)
    data = response.json()

    # Преобразовать в DataFrame
    securities = pd.DataFrame(data['securities']['data'], 
                            columns=data['securities']['columns'])
    marketdata = pd.DataFrame(data['marketdata']['data'],
                            columns=data['marketdata']['columns'])

    return(f'Найдено {len(securities)} бумаг:\n\n{securities[["SECID", "SHORTNAME", "LOTSIZE"]].head()}')


if __name__ == "__main__":

    rt = getRateKey()
    cr = getCurrrency()
    act = getInflation()

    print(act)
    moex()