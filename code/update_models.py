import json
import os
from ai_modules import MessageClassifier, FoodRecommender

def update_food_data():
    """Cập nhật dữ liệu món ăn trong thuc_don.json"""
    # Đọc dữ liệu hiện tại
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as f:
            thuc_don = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Thử tìm trong thư mục code
        try:
            with open('code/thuc_don.json', 'r', encoding='utf-8') as f:
                thuc_don = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            thuc_don = {}
    
    # Thêm các món ăn mới
    bo_sung_mon_an = {
        "gà xào nấm": {
            "nguyen_lieu": ["thịt gà", "nấm hương", "nấm đông cô", "hành tây", "tỏi", "dầu hào", "hạt nêm", "tiêu"],
            "cach_lam": "1. Thịt gà thái miếng vừa ăn, ướp với hạt nêm, tiêu.\n2. Nấm rửa sạch, thái miếng.\n3. Phi thơm tỏi, xào gà săn, cho nấm vào đảo đều.\n4. Nêm nước mắm, dầu hào, đảo đều đến khi chín."
        },
        "súp gà nấm": {
            "nguyen_lieu": ["thịt gà", "nấm hương", "nấm đông cô", "cà rốt", "hành tây", "bột năng", "gừng", "hành lá"],
            "cach_lam": "1. Thịt gà luộc chín, xé nhỏ.\n2. Nấm và rau củ thái hạt lựu.\n3. Đun nước dùng gà, cho nấm và rau củ vào.\n4. Hoà bột năng với nước lạnh, cho vào đun khuấy đều đến khi sánh.\n5. Thêm gà xé, rắc hành lá."
        },
        "cơm gà nấm": {
            "nguyen_lieu": ["gạo", "thịt gà", "nấm hương", "nấm đông cô", "hành tây", "cà rốt", "đậu Hà Lan", "hạt nêm"],
            "cach_lam": "1. Gạo vo sạch, để ráo.\n2. Gà, nấm và rau củ thái hạt lựu.\n3. Xào thịt gà với nấm và rau củ.\n4. Trộn với gạo cùng gia vị, nấu trong nồi cơm điện."
        },
        "cá kho rau muống": {
            "nguyen_lieu": ["cá lóc", "rau muống", "nước mắm", "đường", "tỏi", "ớt", "tiêu", "dầu ăn"],
            "cach_lam": "1. Cá làm sạch, khứa nhẹ 2 bên.\n2. Rau muống rửa sạch, cắt khúc.\n3. Ướp cá với gia vị.\n4. Xếp rau muống dưới đáy nồi, đặt cá lên trên.\n5. Kho nhỏ lửa đến khi cạn nước."
        },
        "canh cá nấu rau muống": {
            "nguyen_lieu": ["cá diêu hồng", "rau muống", "cà chua", "dầu ăn", "hành tím", "gia vị"],
            "cach_lam": "1. Cá làm sạch, phi lê hoặc cắt khúc vừa ăn.\n2. Rau muống rửa sạch, cắt khúc.\n3. Phi thơm hành tím, cho cà chua vào đảo.\n4. Thêm nước, đun sôi, cho cá vào nấu.\n5. Khi cá chín, cho rau muống vào, nấu thêm 2 phút."
        }
    }
    
    # Cập nhật thực đơn
    thuc_don.update(bo_sung_mon_an)
    
    # Lưu lại file thuc_don.json
    try:
        with open('thuc_don.json', 'w', encoding='utf-8') as f:
            json.dump(thuc_don, f, ensure_ascii=False, indent=2)
        print("✅ Đã cập nhật dữ liệu món ăn thành công!")
    except Exception as e:
        # Thử lưu vào thư mục code
        with open('code/thuc_don.json', 'w', encoding='utf-8') as f:
            json.dump(thuc_don, f, ensure_ascii=False, indent=2)
        print("✅ Đã cập nhật dữ liệu món ăn trong thư mục code!")

def update_food_recommender():
    """Cập nhật mô hình gợi ý món ăn (k-NN)"""
    # Đọc dữ liệu thực đơn
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as f:
            thuc_don = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Thử tìm trong thư mục code
        try:
            with open('code/thuc_don.json', 'r', encoding='utf-8') as f:
                thuc_don = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("❌ Không tìm thấy file thuc_don.json")
            return
    
    # Chuyển đổi định dạng dữ liệu
    foods_with_ingredients = {}
    for food_name, info in thuc_don.items():
        foods_with_ingredients[food_name] = [ing.lower() for ing in info.get("nguyen_lieu", [])]
    
    # Huấn luyện và lưu mô hình
    recommender = FoodRecommender()
    recommender.train(foods_with_ingredients)
    recommender.save()
    
    print("✅ Đã cập nhật mô hình gợi ý món ăn thành công!")

def main():
    """Hàm chính để cập nhật toàn bộ dữ liệu và mô hình"""
    # Tạo thư mục models nếu chưa có
    os.makedirs('models', exist_ok=True)
    
    # Cập nhật dữ liệu và mô hình
    update_food_data()
    update_food_recommender()
    
    print("✅ Hoàn tất cập nhật dữ liệu và huấn luyện mô hình!")

if __name__ == "__main__":
    main()