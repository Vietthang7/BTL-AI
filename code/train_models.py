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
        ("tôi có thịt gà và nấm", "goi_y_mon"),
        ("gợi ý món từ cá", "goi_y_mon"),
        ("làm gì với thịt bò và khoai tây", "goi_y_mon"),
        ("món ăn nào phù hợp với thịt gà và nấm", "goi_y_mon"),
        ("tôi có thịt gà và nấm, nên nấu món gì", "goi_y_mon"),
        ("chế biến thịt gà với nấm như thế nào", "goi_y_mon"),
        ("gợi ý món từ cá và rau muống", "goi_y_mon"),
        ("có cá và rau muống, nấu gì ngon", "goi_y_mon"),
        ("kết hợp cá với rau muống thành món gì", "goi_y_mon"),
        ("tôi muốn nấu món từ thịt bò và nấm", "goi_y_mon"),
        ("món tương tự cơm gà", "goi_y_mon"),
        ("có món nào giống với phở bò không", "goi_y_mon"),
        ("món tương tự như cá kho tộ", "goi_y_mon"),
        
        # Loại: cong_thuc
        ("cách làm món thịt kho tàu", "cong_thuc"),
        ("hướng dẫn nấu phở bò", "cong_thuc"),
        ("công thức làm gà rang muối", "cong_thuc"),
        ("làm sao để nấu bún chả", "cong_thuc"),
        ("công thức canh chua cá lóc", "cong_thuc"),
        ("hướng dẫn làm bánh xèo", "cong_thuc"),
        ("chỉ cách làm chả giò", "cong_thuc"),
        ("hướng dẫn làm gà rang muối", "cong_thuc"),
        ("cách nấu bún bò huế", "cong_thuc"),
        ("làm sao để chiên cá giòn", "cong_thuc"),
        ("làm món cá kho rau muống thế nào", "cong_thuc"),
        ("nấu súp gà nấm ra sao", "cong_thuc"),
        ("cách nấu canh cá với rau muống", "cong_thuc"),
        ("hướng dẫn làm mì xào hải sản", "cong_thuc"),
        ("recipe món gà xào nấm", "cong_thuc"),
        ("hướng dẫn nấu cơm gà nấm", "cong_thuc"),
        
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
        ("tạo thực đơn giảm cân 7 ngày", "thuc_don"),
        ("thực đơn tăng cân không ăn hải sản", "thuc_don"),
        ("thực đơn cho người béo phì", "thuc_don"),
        
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
    # Đọc dữ liệu từ file thuc_don.json nếu có
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as f:
            mon_an_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu không có file, tạo dữ liệu mẫu
        mon_an_data = {
            "cơm gà": {"nguyen_lieu": ["gạo", "thịt gà", "hành lá", "dầu ăn", "muối", "nước mắm"]},
            "phở bò": {"nguyen_lieu": ["bánh phở", "thịt bò", "hành tây", "hành lá", "giá", "nước dùng", "gia vị"]},
            "bún chả": {"nguyen_lieu": ["bún", "thịt lợn", "nước mắm", "đường", "ớt", "tỏi", "chanh"]},
            "bánh xèo": {"nguyen_lieu": ["bột gạo", "nước cốt dừa", "nghệ", "đậu xanh", "thịt lợn", "tôm", "giá đỗ"]},
            "gỏi cuốn": {"nguyen_lieu": ["bánh tráng", "thịt lợn", "tôm", "bún", "rau sống", "húng quế", "nước mắm"]},
            "cá kho tộ": {"nguyen_lieu": ["cá", "nước mắm", "đường", "hành", "tỏi", "ớt", "tiêu"]},
            "thịt kho tàu": {"nguyen_lieu": ["thịt lợn", "trứng", "nước dừa", "nước mắm", "đường", "hành", "tỏi"]},
            "canh chua cá": {"nguyen_lieu": ["cá", "dứa", "cà chua", "đậu bắp", "bạc hà", "me", "gia vị"]},
            "gà rang muối": {"nguyen_lieu": ["thịt gà", "muối", "tiêu", "lá chanh", "ớt", "tỏi", "gừng"]},
            "chả giò": {"nguyen_lieu": ["bánh tráng", "thịt lợn", "nấm mèo", "miến", "trứng", "cà rốt", "hành"]},
            "bún bò huế": {"nguyen_lieu": ["bún", "thịt bò", "giò heo", "sả", "ớt", "mắm ruốc", "hành lá"]},
            "bò lúc lắc": {"nguyen_lieu": ["thịt bò", "ớt chuông", "hành tây", "tỏi", "nước mắm", "đường", "dầu hào"]},
            "cơm tấm sườn": {"nguyen_lieu": ["gạo", "sườn lợn", "nước mắm", "đường", "hành", "tỏi", "ớt"]},
            "nộm đu đủ": {"nguyen_lieu": ["đu đủ", "tôm khô", "ớt", "đường", "nước mắm", "chanh", "tỏi"]},
            "cá chiên xù": {"nguyen_lieu": ["cá", "bột chiên xù", "trứng", "hành lá", "nước mắm", "chanh", "ớt"]}
        }
        
        # Lưu dữ liệu mẫu vào file
        with open('thuc_don.json', 'w', encoding='utf-8') as f:
            json.dump(mon_an_data, f, ensure_ascii=False, indent=4)
    
    # Chuyển đổi định dạng dữ liệu
    foods_with_ingredients = {}
    for food_name, info in mon_an_data.items():
        foods_with_ingredients[food_name] = [ing.lower() for ing in info.get("nguyen_lieu", [])]
    
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