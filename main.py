import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Render के लिए डमी सर्वर
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

# बॉट सेटिंग्स
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 1187949807
ADMIN_USERNAME = "@Loaded_VIVEKR"
UPI_ID = "vivektg700@ybl"

USERS = set()
USER_KEYS = {}

# 5 प्रोडक्ट्स (आपके पसंदीदा नाम और कलर्स के अनुसार)
PRODUCTS = {
    "vision": {
        "name": "Vision",
        "emoji": "🟩",
        "plans": {"1_day": {"name": "Vision 1 Day", "price": "200"}, "7_days": {"name": "Vision 7 Days", "price": "700"}}
    },
    "lethal": {
        "name": "Lethal",
        "emoji": "🟥",
        "plans": {"1_day": {"name": "Lethal 1 Day", "price": "200"}, "7_days": {"name": "Lethal 7 Days", "price": "700"}}
    },
    "rage_cheat": {
        "name": "Rage Cheat",
        "emoji": "🟨",
        "plans": {"1_day": {"name": "Rage Cheat 1 Day", "price": "250"}, "7_days": {"name": "Rage Cheat 7 Days", "price": "800"}}
    },
    "king_ios": {
        "name": "King iOS",
        "emoji": "🟧",
        "plans": {"1_day": {"name": "King iOS 1 Day", "price": "300"}, "7_days": {"name": "King iOS 7 Days", "price": "1000"}}
    },
    "win_ios": {
        "name": "Win iOS",
        "emoji": "🩷",
        "plans": {"1_day": {"name": "Win iOS 1 Day", "price": "150"}, "7_days": {"name": "Win iOS 7 Days", "price": "500"}}
    }
}

# Key Stock
KEYS = {
    "vision_1_day": ["VIS-1D-1111", "VIS-1D-2222"],
    "vision_7_days": ["VIS-7D-9999"],
    "lethal_1_day": ["LET-1D-3333"],
    "lethal_7_days": ["LET-7D-8888"],
    "rage_cheat_1_day": ["RAG-1D-4444"],
    "rage_cheat_7_days": ["RAG-7D-7777"],
    "king_ios_1_day": ["KNG-1D-5555"],
    "king_ios_7_days": ["KNG-7D-6666"],
    "win_ios_1_day": ["WIN-1D-0000"],
    "win_ios_7_days": ["WIN-7D-1111"]
}

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🛍 Buy Licence", "🔑 My Licences"],
        ["🔄 Reset Licence", "📞 Support", "🌟 Status"]
    ],
    resize_keyboard=True
)

async def set_commands(application: Application):
    commands = [
        BotCommand("start", "Open bot menu"),
        BotCommand("buy", "Select a product to buy"),
        BotCommand("mykeys", "Show my purchased keys"),
        BotCommand("reset", "Reset licence"),
        BotCommand("support", "Get support contact"),
        BotCommand("status", "Check server status")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USERS.add(user_id)
    welcome_text = "👋 <b>Welcome to BGMI Key Store!</b>\n\nUse /buy to view available licenses."
    await update.message.reply_text(welcome_text, reply_markup=MAIN_KEYBOARD, parse_mode="HTML")

async def show_product_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("🟩 Vision", callback_data='prod_vision')],
        [InlineKeyboardButton("🟥 Lethal", callback_data='prod_lethal')],
        [InlineKeyboardButton("🟨 Rage Cheat", callback_data='prod_rage_cheat')],
        [InlineKeyboardButton("🟧 King iOS", callback_data='prod_king_ios')],
        [InlineKeyboardButton("🩷 Win iOS", callback_data='prod_win_ios')]
    ]
    text = "<b>Select a product to buy:</b>"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def show_my_keys(update: Update, user_id: int):
    keys = USER_KEYS.get(user_id, [])
    if keys:
        key_list = "\n".join([f"• <code>{k}</code>" for k in keys])
        await update.message.reply_text(f"🔑 <b>आपकी खरीदे गए Keys:</b>\n\n{key_list}", parse_mode="HTML")
    else:
        await update.message.reply_text("No licenses found yet.", parse_mode="HTML")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    USERS.add(user_id)

    if text == "🛍 Buy Licence":
        await show_product_menu(update)
    elif text == "🔑 My Licences":
        await show_my_keys(update, user_id)
    elif text == "🔄 Reset Licence":
        await update.message.reply_text(f"🔄 <b>Key Reset:</b> एडमिन से संपर्क करें: {ADMIN_USERNAME}", parse_mode="HTML")
    elif text == "📞 Support":
        await update.message.reply_text(f"📞 <b>Support:</b> एडमिन से संपर्क करें:\n{ADMIN_USERNAME}", parse_mode="HTML")
    elif text == "🌟 Status":
        await update.message.reply_text("🟢 <b>Server Status:</b> All Hacks are 100% Safe & Working!", parse_mode="HTML")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("prod_"):
        prod_key = data.replace("prod_", "")
        prod = PRODUCTS.get(prod_key)
        keyboard = []
        for p_key, p_val in prod["plans"].items():
            keyboard.append([InlineKeyboardButton(f"{prod['emoji']} {p_val['name']} - ₹{p_val['price']}", callback_data=f"buy_{prod_key}_{p_key}")])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="main_buy_menu")])
        await query.edit_message_text(f"✨ <b>{prod['emoji']} {prod['name']} Plans</b> ✨\n\nप्लांस चुनें:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "main_buy_menu":
        await show_product_menu(update)

    elif data.startswith("buy_"):
        parts = data.split("_")
        prod_key = "_".join(parts[1:-2]) if len(parts) > 3 else parts[1]
        plan_key = "_".join(parts[-2:])
        
        prod = PRODUCTS.get(prod_key)
        plan_info = prod["plans"].get(plan_key)
        amount = plan_info["price"]
        item_name = plan_info["name"]
        
        order_id = os.urandom(3).hex().upper()
        
        upi_url = f"upi://pay?pa={UPI_ID}&pn=VisionShop&am={amount}&cu=INR"
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_url)}"

        caption_text = (
            f"✨ <b>{item_name}</b> ✨\n"
            f"📦 <b>Order:</b> <code>{order_id}</code>\n"
            f"💰 <b>Amount:</b> {amount}₹\n"
            f"⏳ Waiting for payment ⏳\n\n"
            f"💳 <b>UPI ID:</b> <code>{UPI_ID}</code>"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Done Payment", callback_data=f"claim_{prod_key}_{plan_key}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")]
        ]

        await query.delete_message()
        await context.bot.send_photo(
            chat_id=user_id,
            photo=qr_image_url,
            caption=caption_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif data == "cancel_order":
        await query.delete_message()
        await context.bot.send_message(chat_id=user_id, text="❌ Order Cancelled.")

    elif data.startswith("claim_"):
        stock_key = data.replace("claim_", "")
        if KEYS.get(stock_key) and len(KEYS[stock_key]) > 0:
            key = KEYS[stock_key].pop(0)
            if user_id not in USER_KEYS:
                USER_KEYS[user_id] = []
            USER_KEYS[user_id].append(key)
            await query.edit_message_caption(caption=f"🎉 <b>आपकी Key:</b> <code>{key}</code>\n\n(यह Key आपके 'My Licences' में सेव हो गई है)", parse_mode="HTML")
        else:
            await query.edit_message_caption(caption=f"❌ स्टॉक खत्म हो गया है! एडमिन से संपर्क करें: {ADMIN_USERNAME}", parse_mode="HTML")

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
    app = Application.builder().token(BOT_TOKEN).post_init(set_commands).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", lambda u, c: show_product_menu(u)))
    app.add_handler(CommandHandler("mykeys", lambda u, c: show_my_keys(u, u.effective_user.id)))
    app.add_handler(CommandHandler("reset", lambda u, c: u.message.reply_text(f"🔄 <b>Key Reset:</b> एडमिन से संपर्क करें: {ADMIN_USERNAME}", parse_mode="HTML")))
    app.add_handler(CommandHandler("support", lambda u, c: u.message.reply_text(f"📞 <b>Support:</b> एडमिन से संपर्क करें:\n{ADMIN_USERNAME}", parse_mode="HTML")))
    app.add_handler(CommandHandler("status", lambda u, c: u.message.reply_text("🟢 <b>Server Status:</b> All Hacks are 100% Safe & Working!", parse_mode="HTML")))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button))
    
    app.run_polling()

if __name__ == "__main__":
    main()
    
