import json
import random

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


def tao_thuc_don_giam_can_7_ngay(mon_khong_thich=None):
    if mon_khong_thich is None:
        mon_khong_thich = []

    thuc_don = ""
    for i in range(7):

        sang_ds = [m for m in mon_an_giam_can["sang"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        trua_ds = [m for m in mon_an_giam_can["trua"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        toi_ds = [m for m in mon_an_giam_can["toi"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        phu_ds = [m for m in mon_an_giam_can["phu"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]


        if not all([sang_ds, trua_ds, toi_ds, phu_ds]):
            return "Không thể tạo thực đơn đủ ngày do quá nhiều món bị loại bỏ."

        sang = random.choice(sang_ds)
        trua = random.choice(trua_ds)
        toi = random.choice(toi_ds)
        phu = random.choice(phu_ds)

        thuc_don += f"📅 Ngày {i + 1}:\n"
        thuc_don += f"• Bữa sáng: {sang}\n"
        thuc_don += f"• Bữa trưa: {trua}\n"
        thuc_don += f"• Bữa tối: {toi}\n"
        thuc_don += f"• Bữa phụ: {phu}\n\n"

    return thuc_don

def tao_thuc_don_tang_can_7_ngay(mon_khong_thich=None):
    if mon_khong_thich is None:
        mon_khong_thich = []

    thuc_don = ""
    for i in range(7):

        sang_ds = [m for m in mon_an_tang_can["sang"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        trua_ds = [m for m in mon_an_tang_can["trua"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        toi_ds = [m for m in mon_an_tang_can["toi"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]
        phu_ds = [m for m in mon_an_tang_can["phu"] if all(mt.lower() not in m.lower() for mt in mon_khong_thich)]

        if not all([sang_ds, trua_ds, toi_ds, phu_ds]):
            return "Không thể tạo thực đơn đủ ngày do quá nhiều món bị loại bỏ."

        sang = random.choice(sang_ds)
        trua = random.choice(trua_ds)
        toi = random.choice(toi_ds)
        phu = random.choice(phu_ds)

        thuc_don += f"📅 Ngày {i + 1}:\n"
        thuc_don += f"• Bữa sáng: {sang}\n"
        thuc_don += f"• Bữa trưa: {trua}\n"
        thuc_don += f"• Bữa tối: {toi}\n"
        thuc_don += f"• Bữa phụ: {phu}\n\n"

    return thuc_don


def tao_thuc_don_tang_can_trong_ngay(mon_khong_thich=None):
    mon_khong_thich = mon_khong_thich or []

    def random_loai(trong_loai):
        lua_chon = [mon for mon in mon_an_tang_can[trong_loai] if mon not in mon_khong_thich]
        return random.choice(lua_chon) if lua_chon else "Không có món phù hợp"

    return (
        "📅 Thực đơn tăng cân trong ngày:\n"
        f"• Bữa sáng: {random_loai('sang')}\n"
        f"• Bữa phụ: {random_loai('phu')}\n"
        f"• Bữa trưa: {random_loai('trua')}\n"
        f"• Bữa tối: {random_loai('toi')}"
    )

def tao_thuc_don_giam_can_trong_ngay(mon_khong_thich=None):
    mon_khong_thich = mon_khong_thich or []

    def random_loai(trong_loai):
        lua_chon = [mon for mon in mon_an_giam_can[trong_loai] if mon not in mon_khong_thich]
        return random.choice(lua_chon) if lua_chon else "Không có món phù hợp"

    return (
        "📅 Thực đơn giảm cân trong ngày:\n"
        f"• Bữa sáng: {random_loai('sang')}\n"
        f"• Bữa phụ: {random_loai('phu')}\n"
        f"• Bữa trưa: {random_loai('trua')}\n"
        f"• Bữa tối: {random_loai('toi')}"
    )

async def xu_ly_mon_khong_thich(user_message, context, update,
                               mon_an_giam_can, mon_an_tang_can):
    mon_khong_thich = context.user_data.get("mon_khong_thich", [])
    che_do = context.user_data.get("che_do")
    loai_thuc_don = context.user_data.get("loai_thuc_don", "trong_ngay")  # mặc định trong ngày

    # Lấy chuỗi sau "không muốn ăn"
    phan_mon = user_message.lower().split("không muốn ăn")[-1]
    danh_sach_ten_mon = [m.strip() for m in phan_mon.replace(",", "+").split("+") if m.strip()]
    tim_duoc_mon_nao = False
    
    # Danh sách để lưu các món đã thông báo
    da_thong_bao = set()

    # Tập hợp tất cả các món
    tat_ca_mon = (
        mon_an_giam_can["sang"] + mon_an_giam_can["trua"] +
        mon_an_giam_can["toi"] + mon_an_giam_can["phu"] +
        mon_an_tang_can["sang"] + mon_an_tang_can["trua"] +
        mon_an_tang_can["toi"] + mon_an_tang_can["phu"]
    )

    for ten_mon_khong_thich in danh_sach_ten_mon:
        da_tim_duoc = False
        
        # Kiểm tra nếu món này đã có trong danh sách không thích
        if ten_mon_khong_thich in mon_khong_thich:
            if ten_mon_khong_thich not in da_thong_bao:
                await update.message.reply_text(f"Món {ten_mon_khong_thich} đã bị loại trước đó.")
                da_thong_bao.add(ten_mon_khong_thich)
            da_tim_duoc = True
            tim_duoc_mon_nao = True
            continue
            
        for mon in tat_ca_mon:
            if ten_mon_khong_thich in mon.lower():
                if ten_mon_khong_thich not in mon_khong_thich and ten_mon_khong_thich not in da_thong_bao:
                    mon_khong_thich.append(ten_mon_khong_thich)
                    await update.message.reply_text(f"Đã ghi nhớ bạn không muốn ăn: {ten_mon_khong_thich}")
                    da_thong_bao.add(ten_mon_khong_thich)
                da_tim_duoc = True
                tim_duoc_mon_nao = True
                break  # Thoát sau khi tìm thấy món đầu tiên chứa từ khóa
                
        if not da_tim_duoc:
            await update.message.reply_text(f"Không xác định được món: {ten_mon_khong_thich}")

    context.user_data["mon_khong_thich"] = mon_khong_thich

    if not tim_duoc_mon_nao:
        return

    # Gợi ý lại thực đơn phù hợp
    if che_do == "giam_can":
        if loai_thuc_don == "trong_ngay":
            thuc_don = tao_thuc_don_giam_can_trong_ngay(mon_khong_thich)
        else:
            thuc_don = tao_thuc_don_giam_can_7_ngay(mon_khong_thich)
    elif che_do == "tang_can":
        if loai_thuc_don == "trong_ngay":
            thuc_don = tao_thuc_don_tang_can_trong_ngay(mon_khong_thich)
        else:
            thuc_don = tao_thuc_don_tang_can_7_ngay(mon_khong_thich)
    else:
        await update.message.reply_text("ℹBạn chưa chọn chế độ *tăng cân* hoặc *giảm cân*.")
        return

    await update.message.reply_text(f"📋 Thực đơn mới không có món bạn không thích:\n{thuc_don}")
async def khoi_phuc_mon_an_lai(user_message, context, send_message_func):
    mon_khong_thich = context.user_data.get("mon_khong_thich", [])
    tim_duoc_mon = False

    # Tách tên món từ câu lệnh người dùng
    phan_mon = user_message.lower().split("muốn ăn lại")[-1].strip()
    ten_mon_muon_khoi_phuc = phan_mon.split("+")[0].strip()

    for mon in mon_khong_thich:
        if ten_mon_muon_khoi_phuc in mon.lower():
            mon_khong_thich.remove(mon)
            context.user_data["mon_khong_thich"] = mon_khong_thich
            await send_message_func(f"Đã bỏ hạn chế món: {mon}. Món này có thể xuất hiện lại trong thực đơn.")
            tim_duoc_mon = True
            break

    if not tim_duoc_mon:
        await send_message_func(
            "Không tìm thấy món này trong danh sách đã loại trừ. Vui lòng kiểm tra lại tên món.")

async def hien_thi_danh_sach_mon_khong_thich(context, send_message_func):
    mon_khong_thich = context.user_data.get("mon_khong_thich", [])
    if mon_khong_thich:
        danh_sach = "\n".join(f"- {mon}" for mon in mon_khong_thich)
        await send_message_func(f"📋 Bạn đã loại các món sau khỏi thực đơn:\n{danh_sach}")
    else:
        await send_message_func("Hiện tại không có món nào bị loại khỏi thực đơn.")