import ttech, sqlite3, funcs, security, investment
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from datetime import datetime, date
import os

BOT = os.getenv("BOT_TOKEN")
CHANEL = -1003848702995
admChk = funcs.adminCheck
flag = {"status" : False, "dataType" : None}

msgs = ["Чтобы использовать функции бота, подпишитесь на канал. Там интересно и полезно 😊. Как подпишишьсяб нажми /start",
        "Добро пожаловать! Я InvestHelper! Я здесь, чтобы помогать тебе с финансами 😊\nВот что я могу"]

subKbd = [[InlineKeyboardButton("Подписаться ✅", url='https://t.me/+7-nEZdgvOXMwYzEy')]]
back = [[InlineKeyboardButton("◀️ НАЗАД", callback_data="back")]]

back2 = [[InlineKeyboardButton("◀️ НАЗАД", callback_data="back")], [InlineKeyboardButton("🔍 Поиск по тикеру", callback_data="tickerSearch")],[InlineKeyboardButton("🗑️ Удалить портфель", callback_data="delCase")]]

mainMenu = [[InlineKeyboardButton("🔑 Ключевая ставка", callback_data="keyrate"), InlineKeyboardButton("💵 Курсы валют", callback_data="currency")],
            [InlineKeyboardButton("📈 Инфляция", callback_data="inflation"), InlineKeyboardButton("🪙 МосБиржа (MOEX)", callback_data="moex")],
            [InlineKeyboardButton("📊 Инвестиционный калькулятор", callback_data="calc")],
            [InlineKeyboardButton("💼 Добавить портфель T-Инвестиций", callback_data="add-port")]]

mainMenu2 = [[InlineKeyboardButton("🔑 Ключевая ставка", callback_data="keyrate"), InlineKeyboardButton("💵 Курсы валют", callback_data="currency")],
            [InlineKeyboardButton("📈 Инфляция", callback_data="inflation"), InlineKeyboardButton("🪙 МосБиржа (MOEX)", callback_data="moex")],
            [InlineKeyboardButton("📊 Инвестиционный калькулятор", callback_data="calc")],
            [InlineKeyboardButton("💼 Ваш портфель T-Инвестиций", callback_data="port")]]


async def subCheck(id, bot):
    try:
        member = await bot.get_chat_member(chat_id = CHANEL, user_id = id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    except Exception as e:
        print(f'Ошибка\n{e}')
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    funcs.saveUser(uid, update.effective_user.first_name, update.effective_user.username)

    
    if not await subCheck(uid, context.bot):
        markup = InlineKeyboardMarkup(subKbd)
        await update.message.reply_text(msgs[0], reply_markup=markup)
        return 0
    
    if investment.tokenCheck(uid):
        markup = InlineKeyboardMarkup(mainMenu2)
    else:
        markup = InlineKeyboardMarkup(mainMenu)

    
    await update.message.reply_text(msgs[1], reply_markup=markup)
    


async def calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    summ = int(args[0])
    percent = int(args[2])/100
    term = int(args[1])
    mrk = InlineKeyboardMarkup(back)
    result = round(summ * (((1 + percent/12)**(12*term) - 1)/(percent/12)), 2)
    invest = summ * 12 * term
    percents = result - invest
    await update.message.reply_text(f'В конце срока вы получите:\n📈{result:,}₽\n\nВложенные средства:\n💵{invest:,}₽\n\nПолучено процентов:\n✨{percents:,}₽'.replace(",", " "), reply_markup=mrk)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = update.effective_user.id
    chat = update.effective_chat.id
    now = datetime.now().strftime("%d.%m.%Y")
    mrk = InlineKeyboardMarkup(back)
    portmrk = InlineKeyboardMarkup(back2)

    if not await subCheck(uid, context.bot):
        markup = InlineKeyboardMarkup(subKbd)
        await context.bot.send_message(chat_id=chat, text=msgs[0], reply_markup=markup)
        return 0
    
    if data == "back":
        flag["dataType"] = ''
        flag["status"] = False

        if investment.tokenCheck(uid):
            markup = InlineKeyboardMarkup(mainMenu2)
        else:
            markup = InlineKeyboardMarkup(mainMenu)

        await query.edit_message_text(msgs[1], reply_markup=markup)

    elif data == "keyrate":
        keyrate = ttech.getRateKey()
        await query.edit_message_text(f'Текущая ключевая ставка ЦБРФ:\n\n{keyrate}\n\n{now}', reply_markup=mrk)

    elif data == "currency":
        await query.edit_message_text(f'{ttech.getCurrrency()}', reply_markup=mrk)

    elif data == "inflation":
        await query.edit_message_text(f'{ttech.getInflation()}', reply_markup=mrk)

    elif data == "calc":
        await query.edit_message_text(f'Для рассчета введите команду:\n\n/calc [Ежемесячная сумма пополнений] [срок инвестирования] [годовая ставка]', reply_markup=mrk)

    elif data == "add-port":
        await query.edit_message_text(f'Отправьте свой API-токен из Т-Инвестиций', reply_markup=mrk)
        flag["dataType"] = 'token'
        flag["status"] = True

    elif data == "moex":
        await query.edit_message_text(f'{ttech.moex()}', reply_markup=mrk)

    elif data == "port":
        await query.edit_message_text(investment.Management(funcs.dbConnect("SELECT token FROM ports WHERE uid = ?", (uid,))[0][0]).getCase(), reply_markup=portmrk)

    elif data == "delCase":
        if funcs.dbConnect("DELETE FROM ports WHERE uid = ?", (uid,)):
            await query.edit_message_text(f'✅ Портфель успешно удален\nДля обеспечения безопасности удалите токен в аккаунте Т-Инвестиции', reply_markup=mrk)
        else:
            await query.edit_message_text(f'❌ При выполнении запроса произошла ошибка!\nПопробуйте еще раз', reply_markup=mrk)

    elif data == "tickerSearch":
        flag["dataType"] = "ticker"
        flag["status"] = True
        await query.edit_message_text(f'Введите тикер')









async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mrk = InlineKeyboardMarkup(back)
    portmrk = InlineKeyboardMarkup(back2)
    if flag["dataType"] == "token" and flag["status"] == True:
        text = update.message.text
        if text[:2] != 't.' and len(text) < 88:
            await update.message.reply_text(f'Неверный токен!', reply_markup=mrk)
            return
        
        result = investment.addToken(text, user.id)
        if result == True:
            await update.message.reply_text(f'Портфель добавлен!', reply_markup=mrk)
            flag["dataType"] = ''
            flag["status"] = False
        else:
            update.message.reply_text(f'Произошла ошибка!\n\n{result}', reply_markup=mrk)

    elif flag["dataType"] == "ticker" and flag["status"] == True:
        text = update.message.text
        result = investment.Management(funcs.dbConnect("SELECT token FROM ports WHERE uid = ?", (user.id,))[0][0]).tickerSearch(text)
        await update.message.reply_text(f'Атив: {result[0]}\nЦена: {result[1]}', reply_markup=mrk)
        




async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    security.dataSecure()
    if funcs.adminCheck(update.effective_user.id):
        await update.message.reply_document("data.txt")
    else: 
        await update.message.reply_text(f'У вас недостаточно прав для использования данной команды!')





app = ApplicationBuilder().token(BOT).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("calc", calculation))
app.add_handler(CommandHandler("data", data))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))




if __name__ == "__main__":
    print("W O R K I N G ")
    
    app.run_polling()
    
    
    print("S T O P E D ")