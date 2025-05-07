import re


def parse_user_input(message):
    can_nang = chieu_cao = tuoi = None
    gioi_tinh = muc_do_hd = ""

    try:
        can_nang_match = re.search(r"cân nặng\s*(\d+)", message)
        chieu_cao_match = re.search(r"chiều cao\s*(\d+)", message)
        tuoi_match = re.search(r"tuổi\s*(\d+)", message)
        gioi_tinh_match = re.search(r"giới tính\s*(nam|nữ)", message)
        muc_do_match = re.search(r"hoạt động\s*([\w\s]+)", message)

        if can_nang_match:
            can_nang = int(can_nang_match.group(1))
        if chieu_cao_match:
            chieu_cao = int(chieu_cao_match.group(1)) / 100
        if tuoi_match:
            tuoi = int(tuoi_match.group(1))
        if gioi_tinh_match:
            gioi_tinh = gioi_tinh_match.group(1).lower()
        if muc_do_match:
            muc_do_hd = muc_do_match.group(1).strip().lower()

        return {
            "can_nang": can_nang,
            "chieu_cao": chieu_cao,
            "tuoi": tuoi,
            "gioi_tinh": gioi_tinh,
            "muc_do": muc_do_hd
        }
    except Exception as e:
        return f"Lỗi khi phân tích đầu vào: {e}"


async def xu_ly_chi_so(thong_tin, update, context):
    required_fields = {
        "can_nang": "cân nặng",
        "chieu_cao": "chiều cao",
        "gioi_tinh": "giới tính (nam/nữ)",
        "tuoi": "tuổi",
        "muc_do": "mức độ hoạt động (ít, vừa, nhiều)"
    }

    missing_fields = [label for key, label in required_fields.items()
                      if key not in thong_tin or not thong_tin[key]]

    if missing_fields:
        await update.message.reply_text(
            f"Bạn chưa cung cấp đầy đủ thông tin để tính chỉ số.\n"
            f"Vui lòng bổ sung: {', '.join(missing_fields)}."
        )
        return

    bmi = tinh_bmi(thong_tin["can_nang"], thong_tin["chieu_cao"])
    bmr = tinh_bmr(thong_tin["gioi_tinh"], thong_tin["can_nang"], thong_tin["chieu_cao"], thong_tin["tuoi"])
    tdee = tinh_tdee(bmr, thong_tin["muc_do"])
    ket_luan = danh_gia_bmi(bmi)

    context.user_data["ket_luan"] = ket_luan
    context.user_data["tdee"] = tdee

    ket_qua = f"""📊 Kết quả chỉ số:
• BMI: {bmi} ({ket_luan})
• BMR: {round(bmr)} kcal/ngày
• TDEE: {round(tdee)} kcal/ngày
"""
    await update.message.reply_text(ket_qua)


def tinh_bmi(can_nang, chieu_cao_m):
    return round(can_nang / (chieu_cao_m ** 2), 2)


def danh_gia_bmi(bmi):
    if bmi < 18.5:
        return "Thiếu cân"
    elif 18.5 <= bmi < 24.9:
        return "Bình thường"
    elif 25 <= bmi < 29.9:
        return "Thừa cân"
    else:
        return "Béo phì"


def tinh_bmr(gioi_tinh, can_nang, chieu_cao_m, tuoi):
    chieu_cao_cm = chieu_cao_m * 100
    if gioi_tinh == "nam":
        return 10 * can_nang + 6.25 * chieu_cao_cm - 5 * tuoi + 5
    else:
        return 10 * can_nang + 6.25 * chieu_cao_cm - 5 * tuoi - 161


def tinh_tdee(bmr, muc_do_hoat_dong):
    muc_do_hoat_dong = muc_do_hoat_dong.lower()
    if "ít" in muc_do_hoat_dong:
        he_so = 1.2
    elif "nhẹ" in muc_do_hoat_dong:
        he_so = 1.375
    elif "vừa" in muc_do_hoat_dong:
        he_so = 1.55
    elif "nhiều" in muc_do_hoat_dong:
        he_so = 1.725
    elif "rất nhiều" in muc_do_hoat_dong:
        he_so = 1.9
    else:
        he_so = 1.2  # mặc định

    return bmr * he_so


async def xu_ly_muc_tieu_can_nang(loai, context, update):
    ket_luan = context.user_data.get("ket_luan")
    tdee = context.user_data.get("tdee")

    if loai == "giam_can":
        if ket_luan in ["Thừa cân", "Béo phì"] and tdee:
            muc_tieu_calo = round(tdee * 0.8)
            context.user_data["che_do"] = "giam_can"
            await update.message.reply_text(
                f"🎯 Bạn đang {ket_luan.lower()}. Để giảm cân, bạn nên ăn khoảng {muc_tieu_calo} kcal/ngày (giảm 20% so với TDEE)."
            )
            await update.message.reply_text(
                "📅 Bạn có muốn xây dựng thực đơn giảm cân?\n👉 Gõ *thực đơn giảm cân trong ngày* hoặc *thực đơn giảm cân trong 7 ngày* để được gợi ý."
            )
        else:
            await update.message.reply_text(
                "ℹ️ Chỉ nên giảm cân khi bạn thừa cân hoặc béo phì. Hãy tính chỉ số trước để kiểm tra thể trạng của bạn."
            )

    elif loai == "tang_can":
        if ket_luan in ["Thiếu cân", "Gầy"] and tdee:
            muc_tieu_calo = round(tdee * 1.2)
            context.user_data["che_do"] = "tang_can"
            await update.message.reply_text(
                f"🎯 Bạn đang {ket_luan.lower()}. Để tăng cân, bạn nên ăn khoảng {muc_tieu_calo} kcal/ngày (tăng 20% so với TDEE)."
            )
            await update.message.reply_text(
                "📅 Bạn có muốn xây dựng thực đơn tăng cân?\n👉 Gõ *thực đơn tăng cân trong ngày* hoặc *thực đơn tăng cân trong 7 ngày* để được gợi ý."
            )
        else:
            await update.message.reply_text(
                "ℹ️ Chỉ nên tăng cân khi bạn thiếu cân. Hãy tính chỉ số trước để kiểm tra thể trạng của bạn."
            )


