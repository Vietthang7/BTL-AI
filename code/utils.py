import json

def goi_y_mon_an_cai_tien(nguyen_lieu_list):
    """Hàm gợi ý món ăn cải tiến, xử lý nhiều nguyên liệu"""
    
    # Đọc dữ liệu từ file thuc_don.json
    try:
        with open('thuc_don.json', 'r', encoding='utf-8') as file:
            thuc_don = json.load(file)
    except FileNotFoundError:
        # Thử tìm trong thư mục code nếu đang chạy từ thư mục gốc
        with open('code/thuc_don.json', 'r', encoding='utf-8') as file:
            thuc_don = json.load(file)
    
    # Danh sách món ăn phù hợp
    mon_an_phu_hop = {}
    
    # Chuẩn hóa danh sách nguyên liệu người dùng
    nguyen_lieu_list = [nl.lower().strip() for nl in nguyen_lieu_list if nl.strip()]
    
    # Duyệt qua từng món trong thực đơn
    for ten_mon, chi_tiet in thuc_don.items():
        nguyen_lieu_mon = [nl.lower() for nl in chi_tiet.get('nguyen_lieu', [])]
        
        # Đếm số nguyên liệu khớp
        so_nguyen_lieu_khop = sum(1 for nl in nguyen_lieu_list if any(nl in nl_mon for nl_mon in nguyen_lieu_mon))
        
        # Nếu ít nhất một nguyên liệu khớp, thêm vào danh sách
        if so_nguyen_lieu_khop > 0:
            mon_an_phu_hop[ten_mon] = so_nguyen_lieu_khop
    
    # Sắp xếp theo số nguyên liệu khớp giảm dần
    mon_an_phu_hop = dict(sorted(mon_an_phu_hop.items(), key=lambda x: x[1], reverse=True))
    
    # Nếu không có món nào phù hợp
    if not mon_an_phu_hop:
        # Gợi ý các món cơ bản từ nguyên liệu đó
        goi_y = "❌ Không tìm thấy món phù hợp với nguyên liệu bạn đưa ra.\n\n"
        goi_y += "🍳 Gợi ý thêm từ AI:\n"
        
        # Thêm một số món cơ bản dựa vào từng nguyên liệu
        for nl in nguyen_lieu_list:
            if "thịt gà" in nl:
                goi_y += "1. Gà luộc\n2. Gà xào sả ớt\n3. Súp gà\n"
                break
            elif "thịt bò" in nl:
                goi_y += "1. Bò xào cần tây\n2. Bò hầm rau củ\n3. Bò lúc lắc\n"
                break
            elif "cá" in nl:
                goi_y += "1. Cá kho tộ\n2. Cá chiên\n3. Canh chua cá\n"
                break
            elif "rau muống" in nl:
                goi_y += "1. Rau muống luộc\n2. Rau muống xào tỏi\n3. Canh rau muống\n"
                break
        
        return goi_y
    
    # Ngược lại, trả về kết quả
    goi_y = "👨‍🍳 Gợi ý món ăn từ " + ", ".join(nguyen_lieu_list) + ":\n\n"
    
    # Lấy top 5 món ăn phù hợp nhất
    for i, (ten_mon, _) in enumerate(list(mon_an_phu_hop.items())[:5], 1):
        goi_y += f"{i}. {ten_mon.title()}\n"
    
    return goi_y