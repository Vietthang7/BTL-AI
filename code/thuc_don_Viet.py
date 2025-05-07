import json
import requests
def goi_ollama_de_lay_cong_thuc(ten_mon, model='gemma2'):
    prompt = f"Hãy viết cách làm chi tiết và nguyên liệu cho món ăn: {ten_mon}."
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    if response.ok:
        return response.json()["response"].strip()
    else:
        return "⚠️ Không thể kết nối với mô hình Ollama. Vui lòng kiểm tra lại."

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
        # Ghép tất cả nguyên liệu của món ăn thành 1 chuỗi để so sánh dễ hơn
        nguyen_lieu_mot_mon = " ".join(thong_tin.get('nguyen_lieu', [])).lower()

        # Kiểm tra xem từng nguyên liệu người dùng nhập có xuất hiện trong chuỗi trên không
        if all(nl.lower() in nguyen_lieu_mot_mon for nl in danh_sach_nguyen_lieu):
            ket_qua.append(f"👉 {ten_mon.title()} \n ")

    if ket_qua:
        return "🍽 Bạn có thể nấu:\n" + "\n".join(ket_qua)
    else:
        return "❌ Không tìm thấy món phù hợp với nguyên liệu bạn đưa ra."


def lay_cong_thuc_mon_an(ten_mon):
    ten_mon = ten_mon.strip().lower()  # Chuẩn hóa đầu vào
    for mon_ten, thong_tin in mon_an_data.items():
        if mon_ten.strip().lower() == ten_mon:
            nguyen_lieu = "\n- " + "\n- ".join(thong_tin.get("nguyen_lieu", []))
        return (
            f"📌 {ten_mon.title()}\n\n"
            f"📝 Nguyên liệu:{nguyen_lieu}\n\n"
            f"📋 Cách làm:\n{mon['cach_lam']}"
        )
    else:
        # Gọi mô hình Ollama nếu không có trong thư viện
        return f"🤖 Bạn có thể nấu :\n\n{goi_ollama_de_lay_cong_thuc(ten_mon)}"
