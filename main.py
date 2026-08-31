import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

KEYS = {
    "1_day": ["KEY-1DAY-ABC1234", "KEY-1DAY-XYZ5678"],
    "7_days": ["KEY-7DAY-WEEK999"]
}

PRICES = {"1_day": "₹150", "7_days": "₹700"}
UPI_ID = "yourupiid@upi"  # यहाँ अपनी UPI ID डालें

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"1 Day Key - {PRICES['1_day']}", callback_data='buy_1_day')],
        [InlineKeyboardButton(f"7 Days Key - {PRICES['7_days']}", callback_data='buy_7_days')]
    ]
    await update.message.reply_text("🔥 **BGMI Key Store** 🔥\n\nप्लांस चुनें:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        plan = query.data.replace("buy_", "")
        text = f"🛒 **प्लान:** {plan.upper()}\n💰 **कीमत:** {PRICES[plan]}\n💳 **UPI:** `{UPI_ID}`\n\nपेमेंट करके नीचे बटन दबाएं:"
        keyboard = [[InlineKeyboardButton("✅ Payment Done", callback_data=f"claim_{plan}")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data.startswith("claim_"):
        plan = query.data.replace("claim_", "")
        if KEYS.get(plan) and len(KEYS[plan]) > 0:
            key = KEYS[plan].pop(0)
            await query.edit_message_text(f"🎉 **आपकी Key:** `{key}`", parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ स्टॉक खत्म हो गया है! एडमिन से बात करें।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
  
