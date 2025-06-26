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
    # ... остальные цены ...
    ("iPhone 16", "128"): 45000,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = ReplyKeyboardMarkup(
        [MODELS[i:i+2] for i in range(0, len(MODELS), 2)] + [["Отмена"]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text("Привет! Выбери модель iPhone:", reply_markup=reply_markup)
    return MODEL

async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Отмена":
        return await cancel(update, context)

    context.user_data["model"] = text
    reply_markup = ReplyKeyboardMarkup(
        [STORAGES] + [["Назад", "Отмена"]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text("Укажи объём памяти (в ГБ):", reply_markup=reply_markup)
    return STORAGE

async def choose_storage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Отмена":
        return await cancel(update, context)
    if text == "Назад":
        # Вернуться к выбору модели
        reply_markup = ReplyKeyboardMarkup(
            [MODELS[i:i+2] for i in range(0, len(MODELS), 2)] + [["Отмена"]],
            one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text("Выбери модель iPhone:", reply_markup=reply_markup)
        return MODEL

    context.user_data["storage"] = text
    reply_markup = ReplyKeyboardMarkup(
        [CONDITIONS] + [["Назад", "Отмена"]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text("Укажи состояние устройства:", reply_markup=reply_markup)
    return CONDITION

async def choose_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Отмена":
        return await cancel(update, context)
    if text == "Назад":
        # Вернуться к выбору памяти
        reply_markup = ReplyKeyboardMarkup(
            [STORAGES] + [["Назад", "Отмена"]],
            one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text("Укажи объём памяти (в ГБ):", reply_markup=reply_markup)
        return STORAGE

    model = context.user_data["model"]
    storage = context.user_data["storage"]
    condition = text

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
        f"📱 Модель: {model}\n💾 Память: {storage} ГБ\n🔧 Состояние: {condition}\n\n💰 Оценка: {price}\n\n"
        "Если хотите начать заново, нажмите /start"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Оценка отменена. Чтобы начать заново, нажмите /start")
    return ConversationHandler.END

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
            MessageHandler(filters.Regex("^Отмена$"), cancel),
            MessageHandler(filters.Regex("^Назад$"), lambda update, context: cancel(update, context)),  # Защита на всякий случай
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
