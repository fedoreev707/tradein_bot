import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

MODEL, STORAGE, CONDITION = range(3)

MODELS = ["iPhone 11", "iPhone 12", "iPhone 12 mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
          "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
          "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
          "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
          "iPhone 16"]

STORAGES = ["64", "128", "256", "512"]
CONDITIONS = ["Идеальное", "Хорошее", "Ниже хорошего"]

TRADEIN_PRICES = {
    ("iPhone 11", "64"): 8000,
    ("iPhone 11", "128"): 10000,
    ("iPhone 12", "64"): 12000,
    ("iPhone 12", "128"): 15000,
    ("iPhone 12 Pro", "128"): 18000,
    ("iPhone 12 Pro", "256"): 22000,
    ("iPhone 12 Pro Max", "128"): 20000,
    ("iPhone 12 Pro Max", "256"): 22000,
    ("iPhone 13", "128"): 23000,
    ("iPhone 13", "256"): 25000,
    ("iPhone 13 Pro", "128"): 30000,
    ("iPhone 13 Pro", "256"): 32000,
    ("iPhone 13 Pro Max", "128"): 30000,
    ("iPhone 13 Pro Max", "256"): 35000,
    ("iPhone 13 Pro Max", "512"): 35000,
    ("iPhone 14", "128"): 27000,
    ("iPhone 14 Pro", "128"): 40000,
    ("iPhone 14 Pro", "256"): 43000,
    ("iPhone 14 Pro Max", "128"): 40000,
    ("iPhone 14 Pro Max", "256"): 45000,
    ("iPhone 15", "128"): 38000,
    ("iPhone 15", "256"): 42000,
    ("iPhone 15 Pro", "128"): 50000,
    ("iPhone 15 Pro", "256"): 55000,
    ("iPhone 15 Pro Max", "256"): 60000,
    ("iPhone 15 Pro Max", "512"): 65000,
    ("iPhone 16", "128"): 45000,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup([MODELS[i:i+2] for i in range(0, len(MODELS), 2)], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Привет! Выбери модель iPhone:", reply_markup=reply_markup)
    return MODEL

async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["model"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([STORAGES], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Укажи объём памяти (в ГБ):", reply_markup=reply_markup)
    return STORAGE

async def choose_storage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["storage"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([CONDITIONS], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Укажи состояние устройства:", reply_markup=reply_markup)
    return CONDITION

async def choose_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            price = "📌 Индивидуальная оценка — обратитесь к менеджеру"
    else:
        price = "📌 Цены для этой конфигурации нет — индивидуальная оценка"

    await update.message.reply_text(
        f"📱 Модель: {model}\n💾 Память: {storage} ГБ\n🔧 Состояние: {condition}\n\n💰 Оценка: {price}"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Оценка отменена.")
    return ConversationHandler.END

def main():
    token = os.getenv("BOT_TOKEN")  # <- Теперь токен читается из переменной окружения
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_model)],
            STORAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_storage)],
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_condition)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
