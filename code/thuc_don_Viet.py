mon_an_data = {
    "trứng chiên": {
        "nguyen_lieu": ["trứng", "dầu ăn", "nước mắm"],
        "cach_lam": "1. Đập trứng vào bát, thêm chút nước mắm.\n2. Đánh đều trứng.\n3. Cho dầu vào chảo, khi dầu nóng thì đổ trứng vào.\n4. Chiên đến khi vàng đều hai mặt là xong."
    },
    "canh chua": {
        "nguyen_lieu": ["cá", "cà chua", "dứa", "me", "rau thơm"],
        "cach_lam": "1. Xào cà chua với chút dầu.\n2. Thêm nước, me và cá vào nấu chín.\n3. Thêm dứa và gia vị, đun thêm vài phút.\n4. Rắc rau thơm trước khi tắt bếp."
    },
    "rau muống xào tỏi": {
        "nguyen_lieu": ["rau muống", "tỏi", "dầu ăn", "muối"],
        "cach_lam": "1. Rửa sạch rau muống, để ráo.\n2. Phi tỏi với dầu.\n3. Cho rau vào xào nhanh tay trên lửa lớn.\n4. Nêm muối và đảo đều cho rau chín tới."
    }
}

def goi_y_mon_an(danh_sach_nguyen_lieu):
    ket_qua = []
    for ten_mon, thong_tin in mon_an_data.items():
        if all(nl in thong_tin['nguyen_lieu'] for nl in danh_sach_nguyen_lieu):
            ket_qua.append(f"👉 {ten_mon.title()}")
    if ket_qua:
        return "🍽 Bạn có thể nấu:\n" + "\n".join(ket_qua)
    else:
        return "❌ Không tìm thấy món phù hợp với nguyên liệu bạn đưa ra."

def lay_cong_thuc_mon_an(ten_mon):
    mon = mon_an_data.get(ten_mon.lower())
    if mon:
        return f"📌 {ten_mon.title()}\n\n📋 Cách làm:\n{mon['cach_lam']}"
    else:
        return "❌ Xin lỗi, tôi chưa có cách làm cho món này."
