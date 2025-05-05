from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# Hàm gọi Ollama model Local (Gemma2)
def hoi_ollama(prompt):
    try:
        response = requests.post(  # Sửa lại "port" thành "post"
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
    await update.message.reply_text("👨‍🍳 Xin chào! Tôi là Chef. Bạn cần tôi giúp gì trong nhà bếp?")

# Trả lời mọi tin nhắn mà người dùng gửi
async def tra_loi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    ai_reply = hoi_ollama(user_message)
    await update.message.reply_text(ai_reply)

# Token từ BotFather
TOKEN = '7580452820:AAGs0QugQJ8DpW9_rWbjaMTtxlR1xF6mipk'  # (đổi nếu public)

# Khởi tạo bot và chạy
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tra_loi))

    print("🤖 Bot đang chạy...")
    app.run_polling()
