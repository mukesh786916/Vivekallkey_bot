import os
import requests # API कॉल के लिए
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
# यहाँ आपको अपने UPI Gateway की API KEY डालनी होगी (उदा. UPIGateway.com से)
UPI_GATEWAY_API_KEY = "rzp_test_TWQXloR3nXr2kd" 

# (बाकी PRODUCTS, KEYS, MAIN_KEYBOARD पुराने कोड जैसा ही रहेगा...)
# ...

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("buy_"):
        parts = data.split("_")
        prod_key = "_".join(parts[1:-2]) if len(parts) > 3 else parts[1]
        plan_key = "_".join(parts[-2:])
        
        prod = PRODUCTS.get(prod_key)
        plan_info = prod["plans"].get(plan_key)
        amount = plan_info["price"]
        item_name = plan_info["name"]
        
        # यूनीक आर्डर आईडी (यही सर्वर से वेरीफाई होगी)
        order_id = f"ORDER_{user_id}_{os.urandom(3).hex().upper()}"
        
        # ⚠️ यहाँ पर Payment Gateway की API को कॉल करके असली लिंक जनरेट किया जाता है
        # यह सिर्फ एक उदाहरण है:
        upi_url = f"upi://pay?pa=vivektg700@ybl&pn=VisionShop&tr={order_id}&am={amount}&cu=INR"
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_url)}"

        caption_text = (
            f"✨ <b>{item_name}</b> ✨\n"
            f"📦 <b>Order ID:</b> <code>{order_id}</code>\n"
            f"💰 <b>Amount:</b> ₹{amount}\n\n"
            f"⚠️ <b>ध्यान दें:</b> पेमेंट करने के बाद 'Check Payment' बटन पर क्लिक करें। बॉट ऑटोमैटिक वेरीफाई करके Key दे देगा।"
        )
        
        # अब स्क्रीनशॉट नहीं मांगेंगे, सीधा सर्वर से चेक करेंगे
        keyboard = [
            [InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"verify_{order_id}_{prod_key}_{plan_key}")],
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

    # ऑटोमैटिक वेरिफिकेशन सिस्टम
    elif data.startswith("verify_"):
        parts = data.split("_")
        order_id = parts[1]
        stock_key = "_".join(parts[2:])

        # ⚠️ यहाँ असली जादू होता है: बॉट Payment Gateway के सर्वर से पूछेगा कि पैसा आया या नहीं
        # नीचे दिया गया URL आपके Gateway Provider पर निर्भर करेगा
        check_api_url = f"https://api.yourgateway.com/check_status?order_id={order_id}"
        
        try:
            # सर्वर से पेमेंट का स्टेटस चेक करना
            # response = requests.get(check_api_url, headers={"Authorization": UPI_GATEWAY_API_KEY})
            # result = response.json()
            
            # मान लेते हैं अभी टेस्टिंग के लिए पेमेंट 'FAILED' है (क्योंकि असली API नहीं लगी है)
            payment_status = "FAILED" # अगर असली API लगेगी तो यह "SUCCESS" हो जाएगा
            
            if payment_status == "SUCCESS":
                # पैसा आ गया, अब ऑटोमैटिक Key दे दो
                if KEYS.get(stock_key) and len(KEYS[stock_key]) > 0:
                    key = KEYS[stock_key].pop(0)
                    await query.edit_message_caption(
                        caption=f"✅ <b>पेमेंट वेरीफाइड!</b>\n\n🎉 <b>आपकी Key:</b> <code>{key}</code>\n\n(Enjoy!)", 
                        parse_mode="HTML"
                    )
                else:
                    await query.edit_message_caption(caption="✅ पेमेंट मिल गया, लेकिन स्टॉक खत्म है! एडमिन से संपर्क करें।")
            else:
                # फेक या पेंडिंग पेमेंट
                await query.answer("❌ पेमेंट अभी तक प्राप्त नहीं हुआ है! कृपया पेमेंट करने के बाद ट्राई करें।", show_alert=True)
                
        except Exception as e:
            await query.answer("सर्वर में कुछ दिक्कत है, बाद में प्रयास करें।", show_alert=True)

# (main function पुराने जैसा ही रहेगा)
