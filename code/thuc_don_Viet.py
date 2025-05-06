import json

# Hàm để đọc dữ liệu từ file JSON
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

# Đọc dữ liệu từ file thuc_don.json
mon_an_data = doc_du_lieu_json('thuc_don.json')

def goi_y_mon_an(danh_sach_nguyen_lieu):
    ket_qua = []
    for ten_mon, thong_tin in mon_an_data.items():
        if all(nl in thong_tin['nguyen_lieu'] for nl in danh_sach_nguyen_lieu):
            ket_qua.append(f"👉 {ten_mon.title()} \n Cách làm:\n{thong_tin['cach_lam']}")
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
