import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Dummy Web Server (Render के Port Error को रोकने के लिए)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# बैकग्राउंड में सर्वर स्टार्ट करें
threading.Thread(target=run_dummy_server, daemon=True).start()

# टेलीग्राम बॉट कॉन्फ़िगरेशन
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# BGMI Keys स्टॉक
KEYS = {
    "1_day": ["KEY-1DAY-ABC1234", "KEY-1DAY-XYZ5678"],
    "7_days": ["KEY-7DAY-WEEK999"]
}

# प्लांस की कीमतें
PRICES = {"1_day": "₹200", "7_days": "₹700"}

# आपकी UPI ID
UPI_ID = "vivektg700@ybl"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"1 Day Key - {PRICES['1_day']}", callback_data='buy_1_day')],
        [InlineKeyboardButton(f"7 Days Key - {PRICES['7_days']}", callback_data='buy_7_days')]
    ]
    await update.message.reply_text(
        "🔥 *BGMI Key Store* 🔥\n\nप्लांस चुनें:", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        plan = query.data.replace("buy_", "")
        text = f"🛒 *प्लान:* {plan.upper()}\n💰 *कीमत:* {PRICES[plan]}\n💳 *UPI:* `{UPI_ID}`\n\nपेमेंट करके नीचे बटन दबाएं:"
        keyboard = [[InlineKeyboardButton("✅ Payment Done", callback_data=f"claim_{plan}")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data.startswith("claim_"):
        plan = query.data.replace("claim_", "")
        if KEYS.get(plan) and len(KEYS[plan]) > 0:
            key = KEYS[plan].pop(0)
            await query.edit_message_text(f"🎉 *आपकी Key:* `{key}`", parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ स्टॉक खत्म हो गया है! एडमिन से बात करें।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
    
