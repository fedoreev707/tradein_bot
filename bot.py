import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Этапы диалога
MODEL, STORAGE, CONDITION = range(3)

# Данные
MODELS = ["iPhone 11", "iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15", "iPhone 16"]
STORAGES = ["64", "128", "256", "512"]
CONDITIONS = ["Идеальное", "Хорошее", "Ниже хорошего"]

TRADEIN_PRICES = {
    ("iPhone 11", "64"): 8000,
    ("iPhone 16", "128"): 45000,
    # Добавь остальные по необходимости
}

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup([
        ["\ud83d\udcf1 Начать оценку"],
        ["\u2139\ufe0f Как работает Trade-In"],
        ["\u260e\ufe0f Связаться с менеджером"]
    ], resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)
    return ConversationHandler.END

# Обработка главного меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "\ud83d\udcf1 Начать оценку":
        return await choose_model_prompt(update, context)
    elif text == "\u2139\ufe0f Как работает Trade-In":
        await update.message.reply_text("\u2705 Вы сдаете устройство, мы его оцениваем и предлагаем сумму. Если вас устраивает — оформляем сделку.")
    elif text == "\u260e\ufe0f Связаться с менеджером":
        await update.message.reply_text("\u2709\ufe0f Напишите нам: @YourManagerUsername")
    return ConversationHandler.END

# Первый шаг оценки
async def choose_model_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup([MODELS[i:i+2] for i in range(0, len(MODELS), 2)] + [["\u274c Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Выберите модель iPhone:", reply_markup=reply_markup)
    return MODEL

async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "\u274c Отмена":
        return await start(update, context)
    context.user_data["model"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([STORAGES] + [["\u274c Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Укажите объём памяти:", reply_markup=reply_markup)
    return STORAGE

async def choose_storage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "\u274c Отмена":
        return await start(update, context)
    context.user_data["storage"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([CONDITIONS] + [["\u274c Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Какое состояние устройства?", reply_markup=reply_markup)
    return CONDITION

async def choose_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "\u274c Отмена":
        return await start(update, context)

    model = context.user_data["model"]
    storage = context.user_data["storage"]
    condition = update.message.text

    key = (model, storage)
    base_price = TRADEIN_PRICES.get(key)

    if base_price:
        if condition == "Идеальное":
            price = base_price
        elif condition == "Хорошее":
            price = int(base_price * 0.9)
        else:
            price = "\ud83d\udccc Индивидуальная оценка — обратитесь к менеджеру"
    else:
        price = "\ud83d\udccc Цены для этой конфигурации нет — индивидуальная оценка"

    await update.message.reply_text(
        f"\ud83d\udcf1 Модель: {model}\n\ud83d\udcc0 Память: {storage} ГБ\n\ud83d\udd27 Состояние: {condition}\n\n"
        f"\ud83d\udcb0 Оценка: {price}\n\nЧтобы начать заново — нажмите /start"
    )
    return ConversationHandler.END

# Главная отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await start(update, context)

def main():
    token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_model)],
            STORAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_storage)],
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_condition)]
        },
        fallbacks=[
            MessageHandler(filters.Regex("^\u274c Отмена$"), cancel)
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
