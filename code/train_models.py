import json
from ai_modules import MessageClassifier, FoodRecommender

def train_message_classifier():
    """Huấn luyện mô hình phân loại tin nhắn"""
    # Tạo dữ liệu huấn luyện
    training_data = [
        # Loại: goi_y_mon
        ("gợi ý món ăn với thịt gà", "goi_y_mon"),
        ("gợi ý món với cà chua", "goi_y_mon"),
        ("có thể nấu gì với thịt bò và rau", "goi_y_mon"),
        ("gợi ý cho tôi món ăn từ cá", "goi_y_mon"),
        ("làm gì với tôm và rau muống", "goi_y_mon"),
        ("món ăn nào làm từ nấm", "goi_y_mon"),
        ("dùng đậu phụ làm món gì", "goi_y_mon"),
        
        # Loại: cong_thuc
        ("cách làm món thịt kho tàu", "cong_thuc"),
        ("hướng dẫn nấu phở bò", "cong_thuc"),
        ("công thức làm gà rang muối", "cong_thuc"),
        ("làm sao để nấu bún chả", "cong_thuc"),
        ("công thức canh chua cá lóc", "cong_thuc"),
        ("hướng dẫn làm bánh xèo", "cong_thuc"),
        ("chỉ cách làm chả giò", "cong_thuc"),
        
        # Loại: chi_so_suc_khoe
        ("tính chỉ số bmi", "chi_so_suc_khoe"),
        ("tính chỉ số bmi cho nam cao 1m75 nặng 70kg", "chi_so_suc_khoe"),
        ("chỉ số bmi của tôi thế nào", "chi_so_suc_khoe"),
        ("tôi nặng 65kg cao 1m65", "chi_so_suc_khoe"),
        ("tính chỉ số cơ thể cho tôi", "chi_so_suc_khoe"),
        ("bmi của người cao 1m60 nặng 55kg", "chi_so_suc_khoe"),
        
        # Loại: tang_giam_can
        ("tôi muốn giảm cân", "tang_giam_can"),
        ("làm sao để tăng cân", "tang_giam_can"),
        ("tôi muốn tăng cân", "tang_giam_can"),
        ("chế độ giảm cân", "tang_giam_can"),
        ("phương pháp tăng cân", "tang_giam_can"),
        ("cần giảm 5kg", "tang_giam_can"),
        
        # Loại: thuc_don
        ("thực đơn giảm cân trong ngày", "thuc_don"),
        ("thực đơn tăng cân trong 7 ngày", "thuc_don"),
        ("thực đơn giảm cân trong 7 ngày", "thuc_don"),
        ("thực đơn tăng cân trong ngày", "thuc_don"),
        ("cho tôi thực đơn ăn kiêng", "thuc_don"),
        ("thực đơn cho người tập gym", "thuc_don"),
        
        # Loại: thiet_lap
        ("tôi không muốn ăn thịt heo", "thiet_lap"),
        ("tôi không thích ăn rau muống", "thiet_lap"),
        ("danh sách món không thích", "thiet_lap"),
        ("tôi muốn ăn lại thịt gà", "thiet_lap"),
        ("tôi không ăn được hải sản", "thiet_lap"),
        ("tôi bị dị ứng với tôm", "thiet_lap"),
        
        # Loại: khac (chung chung)
        ("xin chào", "khac"),
        ("bạn là ai", "khac"),
        ("cảm ơn bạn", "khac"),
        ("hôm nay thời tiết thế nào", "khac"),
        ("tôi cần giúp đỡ", "khac"),
        ("tạm biệt", "khac")
    ]
    
    # Tách thành hai danh sách
    messages = [item[0] for item in training_data]
    categories = [item[1] for item in training_data]
    
    # Huấn luyện và lưu mô hình
    classifier = MessageClassifier()
    classifier.train(messages, categories)
    classifier.save()
    print("Đã huấn luyện và lưu mô hình phân loại tin nhắn!")
    
def train_food_recommender():
    """Huấn luyện mô hình gợi ý món ăn"""
    # Tạo dữ liệu món ăn và nguyên liệu
    foods_with_ingredients = {}
    
    # Thử đọc từ file cong_thuc.json trước
    try:
        with open('cong_thuc.json', 'r', encoding='utf-8') as f:
            cong_thuc = json.load(f)
            
        for food_name, info in cong_thuc.items():
            if "nguyen_lieu" in info:
                if isinstance(info["nguyen_lieu"], list):
                    foods_with_ingredients[food_name] = [ing.lower().split(" ")[0] for ing in info["nguyen_lieu"]]
                else:
                    # Nếu nguyên liệu không phải là list
                    foods_with_ingredients[food_name] = [info["nguyen_lieu"].lower()]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Không tìm thấy file cong_thuc.json hoặc file không hợp lệ.")
    
    # Đọc thêm dữ liệu từ thuc_don.json nếu có
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as f:
            mon_an_data = json.load(f)
            
        for food_name, info in mon_an_data.items():
            foods_with_ingredients[food_name] = [ing.lower() for ing in info.get("nguyen_lieu", [])]
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu không có file, tạo dữ liệu mẫu như trước
        if not foods_with_ingredients:  # Chỉ tạo mẫu nếu chưa có dữ liệu từ cong_thuc.json
            # Mã tạo dữ liệu mẫu giữ nguyên...
            pass
    
    # Huấn luyện và lưu mô hình
    recommender = FoodRecommender()
    recommender.train(foods_with_ingredients)
    recommender.save()
    print("Đã huấn luyện và lưu mô hình gợi ý món ăn!")
if __name__ == "__main__":
    # Tạo thư mục models nếu chưa có
    import os
    os.makedirs('models', exist_ok=True)
    
    train_message_classifier()
    train_food_recommender()
    print("Hoàn thành huấn luyện các mô hình!")