import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

MODEL, STORAGE, CONDITION = range(3)

MODELS = [
    "iPhone 11", "iPhone 12", "iPhone 12 mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16"
]

STORAGES = ["64", "128", "256", "512"]
CONDITIONS = ["Идеальное", "Хорошее", "Ниже хорошего"]

TRADEIN_PRICES = {
    ("iPhone 11", "64"): 8000,
    ("iPhone 16", "128"): 45000,
    # ...добавь остальные значения...
}

# Начало диалога
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup(
        [MODELS[i:i + 2] for i in range(0, len(MODELS), 2)] + [["Отмена"]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Привет! Выбери модель iPhone:", reply_markup=reply_markup)
    return MODEL

# Выбор модели
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Отмена":
        return await cancel(update, context)

    context.user_data["model"] = update.message.text
    reply_markup = ReplyKeyboardMarkup(
        [STORAGES] + [["Отмена"]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Укажи объём памяти (в ГБ):", reply_markup=reply_markup)
    return STORAGE

# Выбор памяти
async def choose_storage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Отмена":
        return await cancel(update, context)

    context.user_data["storage"] = update.message.text
    reply_markup = ReplyKeyboardMarkup(
        [CONDITIONS] + [["Отмена"]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Укажи состояние устройства:", reply_markup=reply_markup)
    return CONDITION

# Выбор состояния
async def choose_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Отмена":
        return await cancel(update, context)

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

    reply_markup = ReplyKeyboardMarkup(
        [["🔁 Начать заново"]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        f"📱 Модель: {model}\n💾 Память: {storage} ГБ\n🔧 Состояние: {condition}\n\n"
        f"💰 Оценка: {price}",
        reply_markup=reply_markup
    )
    return MODEL  # Вернуться к началу при "начать заново"

# Команда отмены и перезапуск
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup(
        [MODELS[i:i + 2] for i in range(0, len(MODELS), 2)] + [["Отмена"]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Оценка отменена. Выберите модель iPhone заново:", reply_markup=reply_markup)
    return MODEL

def main():
    token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_model)],
            STORAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_storage)],
            CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_condition)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("Отмена"), cancel),
            MessageHandler(filters.Regex("🔁 Начать заново"), start),
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
