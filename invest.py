from t_tech.invest import *
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from datetime import datetime, date
import os
BOT = os.getenv("BOT_TOKEN")
ADMINS = [6251262108, 7114090399]
TOKEN = os.getenv("T_TECH_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
cache = None
diff = 10
def clientConnect():
    with Client(TOKEN) as client:
        return client


def checkUser(id):
    return id in ADMINS

def acc_init(): 
    with Client(TOKEN) as client:
        accs = client.users.get_accounts()
        accounts = {i.id:{
            "name": i.name,
        }
        for i in accs.accounts
        }
        return accounts

def getAssetName(figi, client):
    name = client.instruments.get_instrument_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)
    return name.instrument.name


def getAssets(accounts: object):
    with Client(TOKEN) as client:
        
        for id in accounts:
            portfolio = client.operations.get_portfolio(account_id=id)
            
            assets = {
                pos.instrument_uid:{
                    "name":getAssetName(pos.figi, client=client),
                    "amount": pos.quantity.units,
                    "price":pos.current_price.units + pos.current_price.nano / 1e9,
                    "figi": pos.figi
                }
                for pos in portfolio.positions
            }
            for pos in portfolio.positions:
                print(pos.quantity.units, pos.instrument_uid, pos.instrument_type, pos.figi, pos.current_nkd, getAssetName(pos.figi, client=client))
    return assets



print(acc_init())    

getAssets(acc_init())
print(getAssets(acc_init()))
         
class turnOnTrcking():
    def __init__(self):
        """
        :param client: Профиль пользователя
        :param assets: Активы пользователя
        :type assets: object
        :param accounts: Все счета пользователя
        :type accounts: object
        :param interval: Интервал отслеживания в секундах
        :type interval: int
        """
        self.state = False
        self.task = None
        self.client = clientConnect()
        self.accounts = acc_init()
        self.assets = getAssets(self.accounts)
        global diff

    
        
    async def tracking(self):
        sended = False
        try:

            while True: 
                prices = getPrices(self.assets)
                print(pricesCompare(prices))
                await asyncio.sleep(self.interval)
                if pricesCompare(prices) != False and sended != True:
                    await self.app.bot.send_message(ADMINS[0], f'⚠️ ВНИМАНИЕ! Обнаружено изменение цены на {diff} руб.\n\n{pricesCompare(prices)}')
                    sended = True
                    await self.turnOff()
        except asyncio.CancelledError:
            print("task stopped")
            raise


    async def turnOn(self, interval: int, app):
        self.app = app
        if self.task and not self.task.done():
            self.interval = interval
            
            return
        
        self.interval = interval
        self.task = asyncio.create_task(self.tracking())
        
        
        

    async def turnOff(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try: 
                await self.task
            except asyncio.CancelledError:
                pass

            self.task = None
            


            
async def sendMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = '123'
        # for i in content:
        #     result += f'{content[i]["name"]} | {content[i]["price"]}\n\n'

        await context.bot.send_message(ADMINS[0], result)       
        
def pricesCompare(tracked_price: object):
    global cache, diff
    for i in tracked_price:
        if tracked_price[i]["price"] - cache[i]["price"] >= diff:
            return f'{tracked_price[i]["name"]} | {cache[i]["price"]} -> {tracked_price[i]["price"]}'
            
        else: 
            return False

def getPrices(assets):
    global cache
    with Client(TOKEN) as client:
        uids = list(assets.keys())
        
        prices = client.market_data.get_last_prices(instrument_id=uids)
        if cache is None:
            cache = {i.instrument_uid:{
                   "name":getAssetName(i.figi, client),
                   "price": i.price.units + i.price.nano / 1e9
                   }
                   for i in prices.last_prices}
        
        # for i in prices.last_prices:
        #     price = i.price.units + i.price.nano / 1e9
        #     print(price)

        changes = {i.instrument_uid:{
                   "name":getAssetName(i.figi, client),
                   "price": i.price.units + i.price.nano / 1e9
                   }
                   for i in prices.last_prices}
        return changes


TRACK = turnOnTrcking()








async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not(checkUser(update.effective_user.id)):
        await update.message.reply_text(f"У вас недостаточно прав для использования данной команды!")
        return 0
    
    result = ''
    assets = getAssets(acc_init())
    port_price = 0
    for i in assets:
        result += f'{assets[i]["name"]} | {assets[i]["amount"]} шт. | {assets[i]["price"]} руб./шт.\n'
        result += f'---------------\n'
        port_price += assets[i]["price"] * assets[i]["amount"]
    result += f'\nЦена портфеля: {port_price} руб.'

    await update.message.reply_text(f'Здравствуйте {update.effective_user.first_name}! Вот Ваши активы:')
    await update.message.reply_text(result)





async def trackingManage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not(checkUser(update.effective_user.id)):
        await update.message.reply_text(f"У вас недостаточно прав для использования данной команды!")
        return 0
    
    args = context.args
    args[0] = args[0].upper()
    if args[0] == "ON" and len(args) == 2:
        
        await TRACK.turnOn(int(args[1]), context.application)
        await update.message.reply_text(f'✅ Отслеживание включено! ({args[1]})')
        
    elif args[0] == "OFF":
        await TRACK.turnOff()
        await update.message.reply_text(f'💤 Отслеживание выключено!')




async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not(checkUser(update.effective_user.id)):
        await update.message.reply_text(f"У вас недостаточно прав для использования данной команды!")
        return 0
    menu = [[InlineKeyboardButton("Список счетов", callback_data = "portList")]]
    markup = InlineKeyboardMarkup(menu)
    await update.message.reply_text(f'М Е Н Ю', reply_markup=markup)




async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not(checkUser(update.effective_user.id)):
        await update.message.reply_text(f"У вас недостаточно прав для использования данной команды!")
        return 0
    result =''
    global cache
    if cache is not None:
        for i in cache:
            result += f'{cache[i]["name"]} | {cache[i]["price"]}\n\n'
    else: 
        result += f"Память пуста"
    await update.message.reply_text(result)




async def changeDiff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not(checkUser(update.effective_user.id)):
        await update.message.reply_text(f"У вас недостаточно прав для использования данной команды!")
        return 0
    global diff
    args = context.args
    if len(args) !=1:
        await update.message.reply_text(f'❌Неверная команда\n✅changedif [seconds]')
        return
    diff = int(args[0])
    await update.message.reply_text(f'✅Расхождение цен изменено на {diff} руб.')


app = ApplicationBuilder().token("8196098239:AAH5Qay0ez6LGOdKkofohiaa15IJkYcHqCY").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("track", trackingManage))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("memory", memory))
app.add_handler(CommandHandler("changedif", changeDiff))
if __name__ == "__main__":
    print("W O R K I N G ")
    
    app.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        url_path=TOKEN,
        webhook_url=f'{WEBHOOK_URL}/{BOT}'
    )
    getPrices(getAssets(acc_init()))
    
    print("S T O P E D ")