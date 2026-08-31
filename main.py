import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Render के लिए पोर्ट स्कैन फ़िक्स (Dummy Server)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 1187949807 # ⚠️ यहाँ अपनी असली टेलीग्राम न्यूमेरिक ID डालें
ADMIN_USERNAME = "@Loaded_VIVEKR"  # यहाँ आपका अपना टेलीग्राम यूजरनेम डाल दिया है
# डेटाबेस (मेमोरी में स्टोरेज)
USERS = set()
USER_KEYS = {}  # {user_id: [purchased_keys]}

KEYS = {
    "1_day": ["KEY-1DAY-ABC1234", "KEY-1DAY-XYZ5678"],
    "7_days": ["KEY-7DAY-WEEK999"]
}

PRICES = {"1_day": "₹200", "7_days": "₹700"}
UPI_ID = "vivektg700@ybl"

# नीचे दिखने वाला मुख्य कीबोर्ड (Reply Keyboard)
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🛍 Buy Licence", "🔑 My Licences"],
        ["🔄 Reset Licence", "📞 Support", "🌟 Status"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USERS.add(user_id)
    
    welcome_text = "👋 <b>Welcome to BGMI Key Store!</b>\n\nनीचे दिए गए मेन्यू बटन का उपयोग करें:"
    await update.message.reply_text(welcome_text, reply_markup=MAIN_KEYBOARD, parse_mode="HTML")

async def show_buy_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton(f"1 Day Key - {PRICES['1_day']}", callback_data='buy_1_day')],
        [InlineKeyboardButton(f"7 Days Key - {PRICES['7_days']}", callback_data='buy_7_days')]
    ]
    text = "🔥 <b>BGMI Key Store</b> 🔥\n\nप्लांस चुनें:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    USERS.add(user_id)

    if text == "🛍 Buy Licence":
        await show_buy_menu(update)
    elif text == "🔑 My Licences":
        keys = USER_KEYS.get(user_id, [])
        if keys:
            key_list = "\n".join([f"• <code>{k}</code>" for k in keys])
            await update.message.reply_text(f"🔑 <b>आपकी खरीदे गए Keys:</b>\n\n{key_list}", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ आपने अभी तक कोई Key नहीं खरीदी है।")
    elif text == "🔄 Reset Licence":
        await update.message.reply_text("🔄 <b>Key Reset:</b> अगर आपकी Key डिवाइस से अनलॉक करनी है तो एडमिन से संपर्क करें।", parse_mode="HTML")
    elif text == "📞 Support":
        await update.message.reply_text("📞 <b>Support:</b> सहायता के लिए एडमिन से संपर्क करें: @your_admin_username", parse_mode="HTML")
    elif text == "🌟 Status":
        await update.message.reply_text("🟢 <b>Server Status:</b> BGMI Hack is 100% Safe & Working!", parse_mode="HTML")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data.startswith("buy_"):
        plan = query.data.replace("buy_", "")
        plan_name = "1 Day" if plan == "1_day" else "7 Days"
        
        text = (
            f"🛒 <b>प्लान:</b> {plan_name}\n"
            f"💰 <b>कीमत:</b> {PRICES[plan]}\n"
            f"💳 <b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
            f"👉 ऊपर दी गई UPI ID पर पेमेंट करें और पेमेंट पूरा होने के बाद नीचे <b>Done Payment</b> बटन दबाएं:"
        )
        keyboard = [[InlineKeyboardButton("✅ Done Payment", callback_data=f"claim_{plan}")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        
    elif query.data.startswith("claim_"):
        plan = query.data.replace("claim_", "")
        if KEYS.get(plan) and len(KEYS[plan]) > 0:
            key = KEYS[plan].pop(0)
            if user_id not in USER_KEYS:
                USER_KEYS[user_id] = []
            USER_KEYS[user_id].append(key)
            await query.edit_message_text(f"🎉 <b>आपकी Key:</b> <code>{key}</code>\n\n(यह Key आपके 'My Licences' सेक्शन में भी सेव हो गई है)", parse_mode="HTML")
        else:
            await query.edit_message_text("❌ स्टॉक खत्म हो गया है! कृपया एडमिन से संपर्क करें।")

# Broadcast फीचर (एडमिन /broadcast <मैसेज> लिखकर सभी को भेज सकता है)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("उपयोग: /broadcast <मैसेज>")
        return
    count = 0
    for uid in USERS:
        try:
            await context.bot.send_message(uid, msg, parse_mode="HTML")
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ {count} यूजर्स को मैसेज भेज दिया गया।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
    
