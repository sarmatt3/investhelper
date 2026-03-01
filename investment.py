from t_tech.invest import *
import funcs

def tokenCheck(uid):
    result = funcs.dbConnect("SELECT * FROM ports WHERE uid = ?", (uid,))
    return result != [] #Найдено - true

def addToken(token, uid):
    try:
        if funcs.dbConnect("INSERT INTO ports(uid, token) VALUES (?,?)", (uid, token)):
            return True
        
    except Exception as e:
        return e


class Management:
    async def __init__(self, token):
        self.token = token
        

    async def getAssetName(self, figi, client):
        name = client.instruments.get_instrument_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)
        return name.instrument.name
        
        
    async def getCase(self):

        result = f''
        with Client(self.token) as self.client:
            self.accounts = self.client.users.get_accounts()
            for account in self.accounts.accounts:
                result += f'{account.name}\n\n'
                
                portfolio = self.client.operations.get_portfolio(account_id=account.id)
                for pos in portfolio.positions:
                    result += f'--------------------\n'
                    result += f'{self.getAssetName(client=self.client, figi = pos.figi)}({pos.ticker} - {pos.current_price.units + pos.current_price.nano / 1e9} руб./шт.)\n{pos.quantity.units} шт. | {pos.quantity.units * (pos.current_price.units + pos.current_price.nano / 1e9)}'
                
        return result
    

    async def find_on_MOEX(self, client, ticker):
        client = self.client
        shares = self.client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)
        for s in shares.instruments:
            if s.ticker == ticker.upper():
                
                return s
        return None
            

    async def tickerSearch(self, ticker):
        with Client(self.token) as self.client:
            instrument = self.find_on_MOEX(self.client, ticker)
            if instrument is None:
                raise ValueError("Инструмент не найден")
            prices = self.client.market_data.get_last_prices(instrument_id=[instrument.uid])

            lastprice = prices.last_prices[0].price
            price = lastprice.units + lastprice.nano / 1e9
            return instrument.name, price
        


if __name__ == "__main__":
    print(Management("t.GRvEmbvr3RPfnQ3Xh2vSFNrjlqQdR4oSMNZwsgQbBTV5tKFxk5PHtucYHSM761VeTL-HT5LjOTeExdnGhDu48g").getCase())
    print(Management("t.GRvEmbvr3RPfnQ3Xh2vSFNrjlqQdR4oSMNZwsgQbBTV5tKFxk5PHtucYHSM761VeTL-HT5LjOTeExdnGhDu48g").tickerSearch("SBER")[1])