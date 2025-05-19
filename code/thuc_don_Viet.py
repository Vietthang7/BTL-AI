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
    # Khởi tạo biến với giá trị mặc định
    nguyen_lieu = "Không có thông tin"
    cach_lam = "Không có thông tin"
    
    ten_mon = ten_mon.lower()
    
    try:
        # Đọc dữ liệu từ file cong_thuc.json
        with open('cong_thuc.json', 'r', encoding='utf-8') as file:
            cong_thuc = json.load(file)
        
        # Tìm công thức phù hợp
        for mon, thong_tin in cong_thuc.items():
            if ten_mon in mon.lower():
                if isinstance(thong_tin["nguyen_lieu"], list):
                    nguyen_lieu = "\n- " + "\n- ".join(thong_tin["nguyen_lieu"])
                else:
                    nguyen_lieu = thong_tin["nguyen_lieu"]
                
                cach_lam = thong_tin["cach_lam"]
                break
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Lỗi khi đọc file công thức: {e}")
    
    return (f"🍲 Công thức món {ten_mon.title()}:\n\n"
            f"📝 Nguyên liệu: {nguyen_lieu}\n\n"
            f"👨‍🍳 Cách làm: {cach_lam}")
    # Khởi tạo biến nguyen_lieu với giá trị mặc định
    nguyen_lieu = "Không có thông tin"
    cach_lam = "Không có thông tin"
    
    # Tìm công thức từ cơ sở dữ liệu
    ten_mon = ten_mon.lower()
    
    try:
        # Đọc dữ liệu từ file cong_thuc.json
        with open('cong_thuc.json', 'r', encoding='utf-8') as file:
            cong_thuc = json.load(file)
        
        # Tìm công thức phù hợp
        for mon, thong_tin in cong_thuc.items():
            if ten_mon in mon.lower():
                nguyen_lieu = thong_tin.get("nguyen_lieu", "Không có thông tin nguyên liệu")
                cach_lam = thong_tin.get("cach_lam", "Không có hướng dẫn cách làm")
                break
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu không tìm thấy file hoặc file không đúng định dạng
        pass
    
    # Trả về kết quả, dù có tìm thấy công thức hay không
    return (f"🍲 Công thức món {ten_mon.title()}:\n\n"
            f"📝 Nguyên liệu: {nguyen_lieu}\n\n"
            f"👨‍🍳 Cách làm: {cach_lam}")
