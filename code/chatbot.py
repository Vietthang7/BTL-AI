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
import os
# Import các module AI mới
from ai_modules import MessageClassifier, FoodRecommender

# Khởi tạo mô hình AI
message_classifier = MessageClassifier()
food_recommender = FoodRecommender()

# Hàm gọi Ollama model Local (Gemma2)
async def hoi_ollama(prompt, model='gemma2', max_retries=3, delay=2):
    print("DEBUG: Calling Ollama")
    
    for attempt in range(max_retries):
        try:
            # Sử dụng asyncio.to_thread để không chặn luồng chính
            def make_request():
                return requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=30
                )
                
            response = await asyncio.to_thread(make_request)
            
            if response.ok:
                data = response.json()
                return data.get("response", "🤖 Không có phản hồi.")
            else:
                print(f"Lỗi kết nối Ollama lần {attempt + 1}/{max_retries}: Status code {response.status_code}")
        except Exception as e:
            print(f"Lỗi kết nối Ollama lần {attempt + 1}/{max_retries}: {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"Thử lại sau {delay} giây...")
            await asyncio.sleep(delay)
    
    return f"❌ Không thể kết nối với Ollama sau {max_retries} lần thử."


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
        # Trích xuất nguyên liệu từ tin nhắn
        nguyen_lieu_str = user_message.replace("gợi ý món", "").replace("từ", "").replace("với", "").strip()
        
        # Tách nguyên liệu bằng nhiều cách
        nguyen_lieu = []
        if "," in nguyen_lieu_str:
            nguyen_lieu = [nl.strip() for nl in nguyen_lieu_str.split(',') if nl.strip()]
        elif "và" in nguyen_lieu_str:
            nguyen_lieu = [nl.strip() for nl in nguyen_lieu_str.split('và') if nl.strip()]
        else:
            # Nếu không có dấu phân cách, coi như một nguyên liệu
            nguyen_lieu = [nguyen_lieu_str]
        
        if nguyen_lieu:
            # In ra debug
            print(f"DEBUG: Nguyên liệu được tìm: {nguyen_lieu}")
            
            # Đọc dữ liệu từ file thuc_don.json
            try:
                with open('thuc_don.json', 'r', encoding='utf-8') as f:
                    thuc_don = json.load(f)
                    print(f"DEBUG: Đọc thành công thuc_don.json với {len(thuc_don)} món")
            except FileNotFoundError:
                try:
                    with open('code/thuc_don.json', 'r', encoding='utf-8') as f:
                        thuc_don = json.load(f)
                        print(f"DEBUG: Đọc thành công code/thuc_don.json với {len(thuc_don)} món")
                except FileNotFoundError:
                    await update.message.reply_text("❌ Không tìm thấy file thực đơn.")
                    return
            
            # Tìm món phù hợp - CẢI TIẾN: Tìm linh hoạt hơn
            mon_an_phu_hop = []
            
            for ten_mon, chi_tiet in thuc_don.items():
                nguyen_lieu_mon = " ".join(str(item).lower() for item in chi_tiet.get('nguyen_lieu', []))
                
                # Cải tiến: Thay vì kiểm tra chính xác, kiểm tra một phần
                matches = 0
                for nl in nguyen_lieu:
                    nl_lower = nl.lower()
                    # Kiểm tra xem nguyên liệu có trong danh sách không
                    if any(nl_lower in str(ing).lower() for ing in chi_tiet.get('nguyen_lieu', [])):
                        matches += 1
                
                # Nếu tìm thấy tất cả nguyên liệu thì thêm vào kết quả
                if matches == len(nguyen_lieu):
                    mon_an_phu_hop.append(f"👉 {ten_mon.title()}")
            
            if mon_an_phu_hop:
                ai_reply = "🍽 Bạn có thể nấu:\n" + "\n".join(mon_an_phu_hop)
            else:
                # Nếu không tìm thấy món phù hợp, thử tìm món có ít nhất một nguyên liệu
                mon_mot_phan = []
                for ten_mon, chi_tiet in thuc_don.items():
                    nguyen_lieu_mon = " ".join(str(item).lower() for item in chi_tiet.get('nguyen_lieu', []))
                    
                    for nl in nguyen_lieu:
                        nl_lower = nl.lower()
                        if any(nl_lower in str(ing).lower() for ing in chi_tiet.get('nguyen_lieu', [])):
                            mon_mot_phan.append(f"👉 {ten_mon.title()} (có {nl})")
                            break
                
                if mon_mot_phan:
                    ai_reply = "🍽 Không tìm thấy món với tất cả nguyên liệu, nhưng bạn có thể thử:\n" + "\n".join(mon_mot_phan[:5])
                else:
                    # Nếu không tìm thấy món phù hợp
                    ai_reply = "❌ Không tìm thấy món phù hợp với nguyên liệu bạn đưa ra.\n\n"
                    ai_reply += "🤖 Gợi ý thêm từ AI:\n"
                    
                    # Gợi ý cơ bản
                    if any("gà" in nl.lower() for nl in nguyen_lieu):
                        ai_reply += "1. Gà luộc\n2. Gà xào sả ớt\n3. Súp gà\n"
                    elif any("nấm" in nl.lower() for nl in nguyen_lieu):
                        ai_reply += "1. Nấm xào tỏi\n2. Canh nấm\n3. Nấm kho tiêu\n"
                    else:
                        ai_reply += "1. Món hấp\n2. Món xào\n3. Món luộc\n"
            
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text("Vui lòng cho tôi biết bạn có những nguyên liệu nào? (ví dụ: thịt gà, rau muống)")
        return
        # Cải tiến chức năng gợi ý món ăn với k-NN
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
    if ("món tương tự" in user_message or "món giống" in user_message or "món như" in user_message) and food_recommender.is_trained:
        print(f"DEBUG: chay vao day")
        try:
            # Trích xuất tên món từ tin nhắn
            ten_mon = user_message.replace("món tương tự", "").replace("món giống", "").replace("món như", "").strip()
            print(f"DEBUG: Tìm món tương tự với '{ten_mon}'")
            
            # Kiểm tra xem tên món có trong danh sách không
            if not ten_mon:
                await update.message.reply_text("Vui lòng cho biết tên món bạn muốn tìm món tương tự? Ví dụ: món tương tự cơm gà")
                return
                
            similar_foods = food_recommender.recommend_similar(ten_mon, n=5)
            
            if similar_foods:
                reply = f"🍲 Món ăn tương tự với {ten_mon}:\n\n"
                for i, food in enumerate(similar_foods, 1):
                    reply += f"{i}. {food.title()}\n"
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text(f"❌ Không tìm thấy món tương tự với {ten_mon}. Vui lòng kiểm tra lại tên món.")
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

# Lệnh reset models và khởi tạo lại
async def reset_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh để xóa và huấn luyện lại các mô hình AI từ đầu"""
    await update.message.reply_text("🔄 Đang xóa và huấn luyện lại các mô hình AI...")
    
    try:
        # Xóa các file model cũ
        model_files = ["models/message_classifier.pkl", "models/food_recommender.pkl"]
        for file in model_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Đã xóa {file}")
        
        # Import train_models và chạy huấn luyện
        from train_models import train_message_classifier, train_food_recommender
        
        # Chạy huấn luyện bất đồng bộ
        await asyncio.to_thread(train_message_classifier)
        await asyncio.to_thread(train_food_recommender)
        
        # Tải lại các mô hình
        global message_classifier, food_recommender
        message_classifier = MessageClassifier()
        message_classifier.load()
        food_recommender = FoodRecommender()
        food_recommender.load()
        
        await update.message.reply_text("✅ Khởi tạo lại thành công! Các mô hình AI đã được cập nhật.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi khởi tạo lại mô hình: {str(e)}")

# Thêm hàm debug
async def debug_thuc_don_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh để kiểm tra thông tin thực đơn"""
    # In ra thư mục làm việc hiện tại
    cwd = os.getcwd()
    debug_info = f"Thư mục hiện tại: {cwd}\n\n"
    
    # Thử mở file thuc_don.json
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as f:
            thuc_don = json.load(f)
            debug_info += f"✅ Đọc thành công file thuc_don.json!\n"
            debug_info += f"Số lượng món: {len(thuc_don)}\n\n"
            
            # Kiểm tra một số món cụ thể
            for mon in ["gà xào nấm", "súp gà nấm", "rau muống xào tỏi"]:
                if mon in thuc_don:
                    debug_info += f"- Có món: {mon}\n"
                    # Hiện một số nguyên liệu
                    nguyen_lieu = thuc_don[mon].get("nguyen_lieu", [])
                    if nguyen_lieu:
                        debug_info += f"  Nguyên liệu: {', '.join(nguyen_lieu[:3])}...\n"
                else:
                    debug_info += f"- Không có món: {mon}\n"
            
            # Kiểm tra các món có nguyên liệu thịt gà và nấm
            debug_info += "\nTìm món với thịt gà và nấm:\n"
            count = 0
            for ten_mon, chi_tiet in thuc_don.items():
                nguyen_lieu = " ".join(str(item).lower() for item in chi_tiet.get("nguyen_lieu", [])).lower()
                if "thịt gà" in nguyen_lieu and ("nấm" in nguyen_lieu or "nấm hương" in nguyen_lieu):
                    debug_info += f"- {ten_mon}\n"
                    count += 1
            
            if count == 0:
                debug_info += "Không tìm thấy món nào phù hợp!\n"
    
    except FileNotFoundError:
        debug_info += "\n❌ Không tìm thấy file thuc_don.json trong thư mục hiện tại\n"
        
        # Thử tìm trong thư mục code
        try:
            with open('code/thuc_don.json', 'r', encoding='utf-8') as f:
                thuc_don = json.load(f)
                debug_info += f"\n✅ Đọc thành công file code/thuc_don.json!\n"
                debug_info += f"Số lượng món: {len(thuc_don)}\n"
        except FileNotFoundError:
            debug_info += "\n❌ Không tìm thấy file code/thuc_don.json\n"
    
    except json.JSONDecodeError:
        debug_info += "\n❌ Lỗi cú pháp trong file thuc_don.json\n"
    
    await update.message.reply_text(debug_info)

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
    app.add_handler(CommandHandler("huanluyen", huan_luyen))
    app.add_handler(CommandHandler("resetmodels", reset_models))
    app.add_handler(CommandHandler("debug", debug_thuc_don_cmd))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tra_loi))
    
    print("🤖 Bot đang chạy với các mô hình AI...")
    app.run_polling()