import asyncio
import requests
from thuc_don_Viet import goi_y_mon_an, lay_cong_thuc_mon_an
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from kiem_tra_the_trang import parse_user_input, xu_ly_chi_so, xu_ly_muc_tieu_can_nang
from xay_dung_thuc_don import tao_thuc_don_tang_can_trong_ngay, tao_thuc_don_giam_can_trong_ngay, \
    tao_thuc_don_tang_can_7_ngay, tao_thuc_don_giam_can_7_ngay, xu_ly_mon_khong_thich, khoi_phuc_mon_an_lai, \
    hien_thi_danh_sach_mon_khong_thich
import json
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
    await update.message.reply_text("👨‍🍳 Xin chào! Tôi có thể giúp gì cho bạn?")

def doc_du_lieu_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("File không tồn tại.")
        return {}
    except json.JSONDecodeError:
        print("Lỗi khi giải mã JSON.")
        return {}


mon_an_tang_can = doc_du_lieu_json('thuc_don_tang_can.json')

mon_an_giam_can = doc_du_lieu_json('thuc_don_giam_can.json')


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

    if user_message.startswith("tính chỉ số"):
        thong_tin = parse_user_input(user_message)
        await xu_ly_chi_so(thong_tin, update, context)
        return

    if "muốn giảm cân" in user_message:
        await xu_ly_muc_tieu_can_nang("giam_can", context, update)
        return

    elif "muốn tăng cân" in user_message:
        await xu_ly_muc_tieu_can_nang("tang_can", context, update)
        return

    if "thực đơn giảm cân trong ngày" in user_message:
        context.user_data["che_do"] = "giam_can"
        context.user_data["loai_thuc_don"] = "trong_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_giam_can_trong_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn giảm cân trong 7 ngày" in user_message:
        context.user_data["che_do"] = "giam_can"
        context.user_data["loai_thuc_don"] = "7_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_giam_can_7_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn tăng cân trong ngày" in user_message:
        context.user_data["che_do"] = "tang_can"
        context.user_data["loai_thuc_don"] = "trong_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_tang_can_trong_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn tăng cân trong 7 ngày" in user_message:
        context.user_data["che_do"] = "tang_can"
        context.user_data["loai_thuc_don"] = "7_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_tang_can_7_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    if "không muốn ăn" in user_message:
        await xu_ly_mon_khong_thich(user_message, context, update,
                                    mon_an_giam_can, mon_an_tang_can)
        return

    if "muốn ăn lại" in user_message:
        await khoi_phuc_mon_an_lai(user_message, context, update.message.reply_text)
        return

    if "danh sách món không thích" in user_message:
        await hien_thi_danh_sach_mon_khong_thich(context, update.message.reply_text)
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
TOKEN = '7580452820:AAGs0QugQJ8DpW9_rWbjaMTtxlR1xF6mipk'
#TOKEN = '7964158551:AAEN2Z9m6KNpK7DCQmVZtRPgbmVdGYQUt-I'

# Khởi tạo bot và chạy
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tra_loi))
    print("🤖 Bot đang chạy...")
    app.run_polling()