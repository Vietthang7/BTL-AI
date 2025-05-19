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

# Import các module AI mới
from ai_modules import MessageClassifier, FoodRecommender

# Khởi tạo mô hình AI
message_classifier = MessageClassifier()
food_recommender = FoodRecommender()

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
    
    # Tải các mô hình AI nếu chưa tải
    if not message_classifier.is_trained:
        message_classifier.load()
    if not food_recommender.is_trained:
        food_recommender.load()
    
    await update.message.reply_text(
        "👨‍🍳 Xin chào! Tôi là chatbot dinh dưỡng được nâng cấp với trí tuệ nhân tạo.\n\n"
        "Tôi có thể:\n"
        "- Gợi ý món ăn từ nguyên liệu\n"
        "- Tìm công thức nấu ăn\n"
        "- Tạo thực đơn tăng/giảm cân\n"
        "- Tính chỉ số BMI và tư vấn sức khỏe\n"
        "- Gợi ý món ăn tương tự món bạn thích\n\n"
        "Hãy cho tôi biết bạn cần giúp gì nhé!"
    )

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
    
    # --- PHẦN MỚI: Sử dụng Naive Bayes để phân loại tin nhắn ---
    if message_classifier.is_trained:
        intent = message_classifier.predict(user_message)
    else:
        # Nếu mô hình chưa được huấn luyện, dùng logic cũ
        intent = "unknown"
    
    # Xử lý dựa trên phân loại tin nhắn
    if intent == "goi_y_mon":
        # Cải tiến chức năng gợi ý món ăn với k-NN
        if "gợi ý món" in user_message:
            # Giữ logic cũ nhưng bổ sung kết quả từ k-NN
            nguyen_lieu = user_message.replace("gợi ý món", "").strip().split(",")
            nguyen_lieu = [nl.strip() for nl in nguyen_lieu if nl.strip()]
            
            # Logic cũ
            ai_reply = goi_y_mon_an(nguyen_lieu)
            
            # Bổ sung kết quả từ mô hình k-NN
            if food_recommender.is_trained:
                knn_suggestions = food_recommender.recommend_from_ingredients(nguyen_lieu, n=3)
                if knn_suggestions:
                    ai_reply += "\n\n🤖 Gợi ý thêm từ AI:\n"
                    for i, food in enumerate(knn_suggestions, 1):
                        ai_reply += f"{i}. {food.title()}\n"
            
            await update.message.reply_text(ai_reply)
            return
    
    elif intent == "cong_thuc":
        if "cách làm món" in user_message:
            ten_mon = user_message.replace("cách làm món", "").strip()
            ai_reply = lay_cong_thuc_mon_an(ten_mon)
            
            # --- PHẦN MỚI: Gợi ý món tương tự ---
            if food_recommender.is_trained:
                similar_foods = food_recommender.recommend_similar(ten_mon, n=2)
                if similar_foods:
                    ai_reply += "\n\n👉 Bạn cũng có thể thích:\n"
                    for similar in similar_foods:
                        ai_reply += f"- {similar.title()}\n"
            
            await update.message.reply_text(ai_reply)
            return
    
    # Giữ lại logic xử lý cũ cho các intent khác
    if "tính chỉ số" in user_message or intent == "chi_so_suc_khoe":
        thong_tin = parse_user_input(user_message)
        await xu_ly_chi_so(thong_tin, update, context)
        return

    if "muốn giảm cân" in user_message or (intent == "tang_giam_can" and "giảm" in user_message):
        await xu_ly_muc_tieu_can_nang("giam_can", context, update)
        return

    elif "muốn tăng cân" in user_message or (intent == "tang_giam_can" and "tăng" in user_message):
        await xu_ly_muc_tieu_can_nang("tang_can", context, update)
        return

    if "thực đơn giảm cân trong ngày" in user_message or (intent == "thuc_don" and "giảm" in user_message and "ngày" in user_message):
        context.user_data["che_do"] = "giam_can"
        context.user_data["loai_thuc_don"] = "trong_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_giam_can_trong_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn giảm cân trong 7 ngày" in user_message or (intent == "thuc_don" and "giảm" in user_message and "7" in user_message):
        context.user_data["che_do"] = "giam_can"
        context.user_data["loai_thuc_don"] = "7_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_giam_can_7_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn tăng cân trong ngày" in user_message or (intent == "thuc_don" and "tăng" in user_message and "ngày" in user_message):
        context.user_data["che_do"] = "tang_can"
        context.user_data["loai_thuc_don"] = "trong_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_tang_can_trong_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    elif "thực đơn tăng cân trong 7 ngày" in user_message or (intent == "thuc_don" and "tăng" in user_message and "7" in user_message):
        context.user_data["che_do"] = "tang_can"
        context.user_data["loai_thuc_don"] = "7_ngay"
        mon_khong_thich = context.user_data.get("mon_khong_thich", [])
        thuc_don = tao_thuc_don_tang_can_7_ngay(mon_khong_thich)
        await update.message.reply_text(thuc_don)
        return

    if "không muốn ăn" in user_message or (intent == "thiet_lap" and ("không" in user_message and "ăn" in user_message)):
        await xu_ly_mon_khong_thich(user_message, context, update,
                                    mon_an_giam_can, mon_an_tang_can)
        return

    if "muốn ăn lại" in user_message or (intent == "thiet_lap" and "lại" in user_message):
        await khoi_phuc_mon_an_lai(user_message, context, update.message.reply_text)
        return

    if "danh sách món không thích" in user_message or (intent == "thiet_lap" and "danh sách" in user_message):
        await hien_thi_danh_sach_mon_khong_thich(context, update.message.reply_text)
        return
        
    # --- PHẦN MỚI: Chức năng gợi ý món tương tự ---
    if "món tương tự" in user_message and food_recommender.is_trained:
        try:
            ten_mon = user_message.replace("món tương tự", "").strip()
            similar_foods = food_recommender.recommend_similar(ten_mon, n=5)
            
            if similar_foods:
                reply = f"🍲 Món ăn tương tự với {ten_mon}:\n\n"
                for i, food in enumerate(similar_foods, 1):
                    reply += f"{i}. {food.title()}\n"
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text(f"❌ Không tìm thấy món tương tự với {ten_mon}.")
            return
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi khi tìm món tương tự: {str(e)}")
            return

    # Dùng Ollama cho các trường hợp khác
    context.user_data.setdefault('history', [])
    context.user_data['history'].append(user_message)
    recent_history = context.user_data['history'][-5:]
    prompt = "\n".join(recent_history)
    ai_reply = await asyncio.to_thread(hoi_ollama, prompt)
    await update.message.reply_text(ai_reply)

# Thêm lệnh huấn luyện mô hình
async def huan_luyen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh để huấn luyện lại các mô hình AI"""
    await update.message.reply_text("🔄 Đang huấn luyện lại các mô hình AI...")
    
    try:
        # Import train_models và chạy huấn luyện
        from train_models import train_message_classifier, train_food_recommender
        
        # Chạy huấn luyện bất đồng bộ để không chặn bot
        await asyncio.to_thread(train_message_classifier)
        await asyncio.to_thread(train_food_recommender)
        
        # Tải lại các mô hình
        message_classifier.load()
        food_recommender.load()
        
        await update.message.reply_text("✅ Huấn luyện thành công! Các mô hình AI đã được cập nhật.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi huấn luyện mô hình: {str(e)}")

# Token từ BotFather
TOKEN = '7433569751:AAGPj8iRnKUiHi6Z5f6FNyyOhRyxqk3DbZc'
#TOKEN = '7964158551:AAEN2Z9m6KNpK7DCQmVZtRPgbmVdGYQUt-I'

# Khởi tạo bot và chạy
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Tải các mô hình AI nếu có
    try:
        message_classifier.load()
        print("✅ Đã tải mô hình phân loại tin nhắn")
    except Exception as e:
        print(f"⚠️ Không thể tải mô hình phân loại tin nhắn: {e}")
    
    try:
        food_recommender.load()
        print("✅ Đã tải mô hình gợi ý món ăn")
    except Exception as e:
        print(f"⚠️ Không thể tải mô hình gợi ý món ăn: {e}")
    
    # Thêm handlers
    app.add_handler(CommandHandler("start", bat_dau))
    app.add_handler(CommandHandler("huanluyen", huan_luyen))  # Thêm lệnh huấn luyện
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tra_loi))
    
    print("🤖 Bot đang chạy với các mô hình AI...")
    app.run_polling()