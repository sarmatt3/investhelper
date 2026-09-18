import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import json
def show_key_rate():
    """
    Возвращает размер ключевой ставки за 6 дней
    Returns:
    result: Размер ключевой ставки за 6 дней
    """
    result = {}
    url = "https://cbr.ru/hd_base/KeyRate/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    rate_table = soup.find_all("table", class_ = "data")
    for i, data in enumerate(rate_table, 1):
        text = data.get_text()
        lst = [x for x in text.split("\n") if x]
    list_size = len(lst)
    for i in range(2, list_size - 1, 2):
        result[lst[i]] = lst[i+1] + "%"
    return result


def key_rate_today():
    try:
        key_rates = show_key_rate()
        today = date.today().strftime("%d.%m.%Y")
        return key_rates[today]
    except KeyError:
        today = (date.today()- timedelta(days=1)).strftime("%d.%m.%Y") 
        return key_rates[today]

# ------------------------------------------------

def get_currency(basic = False):
    url = "https://cbr.ru/currency_base/daily/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    basics = ["USD", "EUR", "CNY", "BYN"]
    table = soup.find("table", class_="data")
    if not table:
        return {}
    
    rows = table.find_all("tr")
    result = {}
    
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) >= 5 and not basic:  # Убеждаемся, что строка содержит все нужные данные
            # Индексы: 0 - цифровой код, 1 - буквенный код, 2 - единиц, 3 - валюта, 4 - курс
            num_code = cells[0].text.strip()
            char_code = cells[1].text.strip()
            unit = cells[2].text.strip()
            currency_name = cells[3].text.strip()
            rate = cells[4].text.strip()
            
            result[char_code] = {
                'num_code': num_code,
                'unit': unit,
                'currency': currency_name,
                'rate': rate
            }
        elif basic:
            num_code = cells[0].text.strip()
            char_code = cells[1].text.strip()
            unit = cells[2].text.strip()
            currency_name = cells[3].text.strip()
            rate = cells[4].text.strip()
            if char_code in basics:            
                result[char_code] = {
                    'num_code': num_code,
                    'unit': unit,
                    'currency': currency_name,
                    'rate': rate
                }
    
    return result


def return_active_price(ticker, from_, till):
    url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json?from={from_}&till={till}"
    
    response = requests.get(url)
    data = response.json()
    rows = data["history"]["data"]
    result = {

    }
    for i, row in enumerate(rows):
        result[row[1]] = {
            "name": row[2],
            "low_price": row[7],
            "high_price": row[8],

        }
    json.dumps(result, indent=4, ensure_ascii=False)
    return result

def get_active_price_last(ticker):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json?iss.only=marketdata"
    response = requests.get(url)
    data = response.json()
    i = data["marketdata"]["columns"].index("LAST")
    result = data["marketdata"]["data"][0][i]
    return result

if __name__ == "__main__":
    # test = show_key_rate()
    # print(test)
    # for i in test:
    #     print(f'{i} - {test[i]}')

    # test2 = key_rate_today()
    # print(test2)
    # test3 = get_currency(True)
    # print(test3)
    test4 = get_active_price_last("T")
    print(test4)
    