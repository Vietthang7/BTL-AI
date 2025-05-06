import asyncio
import requests
from thuc_don_Viet import goi_y_mon_an, lay_cong_thuc_mon_an
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Hàm gọi Ollama model Local (Gemma2)
def hoi_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma2",
                "prompt": prompt,
                "stream": False
            }
        )
        data = response.json()
        return data.get("response", "🤖 Không có phản hồi.")
    except Exception as e:
        return f"❌ Lỗi khi gọi Ollama: {e}"


# Lệnh /start
async def bat_dau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []  # Reset lịch sử khi bắt đầu
    await update.message.reply_text("👨‍🍳 Xin chào! Tôi là Chef. Bạn cần tôi giúp gì trong nhà bếp?")


# Trả lời mọi tin nhắn mà người dùng gửi
async def tra_loi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()

    # Nếu là gợi ý món ăn
    if user_message.startswith("gợi ý món"):
        nguyen_lieu = user_message.replace("gợi ý món", "").strip().split(",")
        nguyen_lieu = [nl.strip() for nl in nguyen_lieu if nl.strip()]
        ai_reply = goi_y_mon_an(nguyen_lieu)
        await update.message.reply_text(ai_reply)
        return

    elif user_message.startswith("cách làm món"):
        ten_mon = user_message.replace("cách làm món", "").strip()
        ai_reply = lay_cong_thuc_mon_an(ten_mon)
        await update.message.reply_text(ai_reply)
        return

    # Dùng Ollama nếu không phải gợi ý món
    else:
        context.user_data.setdefault('history', [])
        context.user_data.setdefault('history', [])
        context.user_data['history'].append(user_message)
        recent_history = context.user_data['history'][-5:]
        prompt = "\n".join(recent_history)
        ai_reply = await asyncio.to_thread(hoi_ollama, prompt)
        await update.message.reply_text(ai_reply)

# Token từ BotFather
#TOKEN = '7580452820:AAGs0QugQJ8DpW9_rWbjaMTtxlR1xF6mipk'
TOKEN = '7964158551:AAEN2Z9m6KNpK7DCQmVZtRPgbmVdGYQUt-I'

# Khởi tạo bot và chạy
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tra_loi))
    print("🤖 Bot đang chạy...")
    app.run_polling()