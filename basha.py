# =========================================
# Ranim Store Pro - Ultimate Admin System
# منظومة الإدارة الاحترافية الكاملة
# =========================================

import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid
import qrcode
import io
import base64
import pandas as pd

# =========================================
# إعداد الصفحة
# =========================================

st.set_page_config(
    page_title="Ranim Store Admin",
    page_icon="🛍️",
    layout="wide"
)

# =========================================
# Supabase
# =========================================

SUPABASE_URL = "https://xwwlffppepiwdiekqylr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3d2xmZnBwZXBpd2RpZWtxeWxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2NDcxMjksImV4cCI6MjA5NTIyMzEyOX0.bpWm7U4Z9JybPrEBPWmHhTRGZsq2CaaI7AVnuWKTZNg"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================================
# تصميم الواجهة
# =========================================

st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
}

.stMetric {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
}

h1,h2,h3 {
    color: #111827;
}

div.stButton > button {
    border-radius: 12px;
    height: 45px;
    font-weight: bold;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# المستخدمين
# =========================================

DEFAULT_USERS = {
    "Bashir": {"password": "B2026", "role": "admin"},
    "Ahmed": {"password": "A2026", "role": "admin"}
}

def load_users_from_supabase():
    try:
        rows = supabase.table("users").select("*").execute().data
        if rows:
            return {r["username"]: {"password": r["password"], "role": r.get("role", "staff")} for r in rows}
    except Exception:
        pass
    return DEFAULT_USERS

def save_user_to_supabase(username, password, role):
    try:
        existing = supabase.table("users").select("*").eq("username", username).execute().data
        if existing:
            supabase.table("users").update({"password": password, "role": role}).eq("username", username).execute()
        else:
            supabase.table("users").insert({"username": username, "password": password, "role": role}).execute()
    except Exception:
        pass

if "users" not in st.session_state:
    st.session_state["users"] = load_users_from_supabase()

if "logged_user" not in st.session_state:
    st.session_state["logged_user"] = None

# =========================================
# إعدادات المتجر
# =========================================

if "store_settings" not in st.session_state:
    try:
        rows = supabase.table("store_settings").select("*").execute().data
        if rows:
            r = rows[0]
            st.session_state["store_settings"] = {
                "store_name":      r.get("store_name", "متجر رنيم"),
                "welcome_message": r.get("welcome_message", "أهلاً بكم في متجرنا"),
                "whatsapp_number": r.get("whatsapp_number", "218910000000"),
                "logo_url":        r.get("logo_url", "")
            }
        else:
            raise Exception("empty")
    except Exception:
        st.session_state["store_settings"] = {
            "store_name": "متجر رنيم",
            "welcome_message": "أهلاً بكم في متجرنا",
            "whatsapp_number": "218910000000",
            "logo_url": ""
        }

# =========================================
# دالة رأس المال
# =========================================

def calculate_capital(
    price_yuan,
    weight,
    pack_cost,
    bag_cost,
    dollar_rate,
    shipping_rate
):

    product_cost_lyd = (
        price_yuan * 0.14
    ) * dollar_rate

    shipping_cost_lyd = (
        weight * shipping_rate
    ) * dollar_rate

    total = (
        product_cost_lyd
        + shipping_cost_lyd
        + pack_cost
        + bag_cost
    )

    return round(total, 2)

# =========================================
# تسجيل العمليات المالية
# =========================================

def add_financial_log(
    action_type,
    amount,
    note,
    user_name
):

    supabase.table(
        "financial_logs"
    ).insert({

        "action_type": action_type,
        "amount": amount,
        "note": note,
        "user_name": user_name,
        "created_at": str(datetime.now())

    }).execute()

# =========================================
# توليد QR Code
# =========================================

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"

# =========================================
# إرسال واتساب
# =========================================

def send_whatsapp(phone, message):
    encoded = message.replace("\n", "%0A").replace(" ", "%20")
    url = f"https://wa.me/{phone}?text={encoded}"
    return url

# =========================================
# تسجيل الدخول
# =========================================

if st.session_state["logged_user"] is None:

    st.markdown("""
    <div style='text-align:center;padding:40px'>
        <h1>🛍️ منظومة متجر رنيم</h1>
        <h3>نظام الإدارة الاحترافي</h3>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input(
        "اسم المستخدم"
    )

    password = st.text_input(
        "الرمز السري",
        type="password"
    )

    if st.button("تسجيل الدخول"):

        users = st.session_state["users"]

        if username in users:
            user_data = users[username]
            # دعم الصيغتين القديمة والجديدة
            if isinstance(user_data, dict):
                stored_pass = user_data["password"]
            else:
                stored_pass = user_data

            if stored_pass == password:
                st.session_state["logged_user"] = username
                st.success("تم تسجيل الدخول")
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
        else:
            st.error("بيانات الدخول غير صحيحة")

# =========================================
# داخل النظام
# =========================================

else:

    current_user = st.session_state["logged_user"]

    # صلاحية المستخدم
    user_data = st.session_state["users"].get(current_user, {})
    if isinstance(user_data, dict):
        current_role = user_data.get("role", "staff")
    else:
        current_role = "admin"

    # =====================================
    # القائمة الجانبية
    # =====================================

    st.sidebar.title("⚙️ لوحة التحكم")

    st.sidebar.success(
        f"مرحباً {current_user} | {current_role}"
    )

    if st.sidebar.button("🚪 تسجيل الخروج"):

        st.session_state["logged_user"] = None
        st.rerun()

    # القائمة حسب الصلاحية
    if current_role == "admin":
        menu = [
            "الرئيسية",
            "إضافة منتج",
            "المنتجات",
            "تسجيل عملية بيع",
            "الخزائن والمحافظ",
            "إدارة رأس المال",
            "الطلبات",
            "البحث",
            "سجل العمليات",
            "السجل المالي",
            "سجل المبيعات",
            "إحصائيات متقدمة",
            "إدارة المستخدمين",
            "إعدادات المتجر",
            "تصدير البيانات",
            "نسخ احتياطي"
        ]
    else:
        menu = [
            "الرئيسية",
            "المنتجات",
            "تسجيل عملية بيع",
            "الطلبات",
            "البحث",
            "سجل المبيعات"
        ]

    choice = st.sidebar.selectbox(
        "القائمة",
        menu
    )

    # =====================================
    # الرئيسية
    # =====================================

    if choice == "الرئيسية":

        st.title("🛍️ لوحة الإدارة")

        products = supabase.table(
            "products"
        ).select("*").execute().data

        transactions = supabase.table(
            "transactions"
        ).select("*").execute().data

        orders = supabase.table(
            "orders"
        ).select("*").execute().data

        total_profit = sum(
            t["profit"]
            for t in transactions
        ) if transactions else 0

        new_orders = len([
            o for o in orders
            if o.get("status") == "جديد"
        ]) if orders else 0

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("📦 المنتجات", len(products))

        with c2:
            st.metric("🧾 المبيعات", len(transactions))

        with c3:
            st.metric(
                "📈 الأرباح",
                f"{round(total_profit,2)} د.ل"
            )

        with c4:
            st.metric("🆕 طلبات جديدة", new_orders)

        # إشعارات طلبات جديدة
        if new_orders > 0:
            st.warning(
                f"⚠️ لديك {new_orders} طلب جديد في انتظار المراجعة!"
            )

        st.divider()

        # آخر المبيعات
        st.subheader("📋 آخر المبيعات")
        if transactions:
            last5 = transactions[-5:][::-1]
            for t in last5:
                st.info(
                    f"🛒 {t['product_name']} | "
                    f"الكمية: {t['quantity']} | "
                    f"الربح: {t['profit']} د.ل | "
                    f"البائع: {t['seller']}"
                )

    # =====================================
    # إضافة منتج
    # =====================================

    elif choice == "إضافة منتج":

        st.header("➕ إضافة منتج")

        p_name = st.text_input("اسم المنتج")

        qty = st.number_input(
            "الكمية",
            min_value=1,
            step=1
        )

        price_yuan = st.number_input(
            "السعر باليوان",
            min_value=0.0
        )

        weight = st.number_input(
            "الوزن",
            min_value=0.0
        )

        pack_cost = st.number_input(
            "التغليف",
            min_value=0.0
        )

        bag_cost = st.number_input(
            "الكيس",
            min_value=0.0
        )

        dollar_rate = st.number_input(
            "الدولار",
            value=7.1
        )

        shipping_rate = st.number_input(
            "الشحن",
            value=12.5
        )

        max_order_qty = st.number_input(
            "الحد الأقصى للطلب الواحد (تلقائي = الكمية)",
            min_value=1,
            value=int(qty),
            step=1
        )

        purchase_source = st.radio(
            "مصدر الشراء",
            ["cash", "bank"]
        )

        capital = calculate_capital(
            price_yuan,
            weight,
            pack_cost,
            bag_cost,
            dollar_rate,
            shipping_rate
        )

        st.info(f"💰 رأس المال: {capital}")

        selling_price = st.number_input(
            "سعر البيع",
            min_value=0.0
        )

        uploaded_file = st.file_uploader(
            "صورة المنتج",
            type=["png","jpg","jpeg"]
        )

        if st.button("حفظ المنتج"):

            image_url = ""

            if uploaded_file:

                file_name = f"{uuid.uuid4()}.jpg"
                file_bytes = uploaded_file.getvalue()

                supabase.storage.from_(
                    "products"
                ).upload(file_name, file_bytes)

                image_url = (
                    f"{SUPABASE_URL}"
                    f"/storage/v1/object/public/"
                    f"products/{file_name}"
                )

            existing = supabase.table(
                "products"
            ).select("*").eq(
                "name", p_name
            ).execute().data

            if existing:

                old_qty = existing[0]["quantity"]

                supabase.table(
                    "products"
                ).update({
                    "quantity": old_qty + qty,
                    "fixed_capital": capital,
                    "selling_price": selling_price,
                    "image_url": image_url,
                    "max_order_qty": max_order_qty
                }).eq("name", p_name).execute()

            else:

                supabase.table(
                    "products"
                ).insert({
                    "name": p_name,
                    "quantity": qty,
                    "fixed_capital": capital,
                    "selling_price": selling_price,
                    "image_url": image_url,
                    "max_order_qty": max_order_qty
                }).execute()

            # خصم من رأس المال تلقائياً
            existing_capital = supabase.table(
                "capital_accounts"
            ).select("*").eq(
                "account_type", purchase_source
            ).execute().data

            if existing_capital:
                current_bal = existing_capital[0]["balance"]
                new_bal = current_bal - (capital * qty)
                supabase.table(
                    "capital_accounts"
                ).update({
                    "balance": new_bal
                }).eq(
                    "account_type", purchase_source
                ).execute()

            add_financial_log(
                "إضافة بضاعة",
                capital * qty,
                p_name,
                current_user
            )

            st.success("تم حفظ المنتج")

    # =====================================
    # المنتجات
    # =====================================

    elif choice == "المنتجات":

        st.header("📦 المنتجات")

        products = supabase.table(
            "products"
        ).select("*").execute().data

        if products:

            for product in products:

                with st.expander(product["name"]):

                    col_img, col_qr = st.columns(2)

                    with col_img:
                        if product.get("image_url"):
                            st.image(
                                product["image_url"],
                                width=200
                            )

                    with col_qr:
                        st.markdown("**QR Code المنتج:**")
                        qr_data = (
                            f"المنتج: {product['name']}\n"
                            f"السعر: {product['selling_price']} د.ل"
                        )
                        qr_img = generate_qr(qr_data)
                        st.markdown(
                            f'<img src="{qr_img}" width="150"/>',
                            unsafe_allow_html=True
                        )

                    new_qty = st.number_input(
                        "الكمية",
                        value=product["quantity"],
                        key=f"qty_{product['id']}"
                    )

                    new_price = st.number_input(
                        "سعر البيع",
                        value=float(product["selling_price"]),
                        key=f"price_{product['id']}"
                    )

                    new_max = st.number_input(
                        "الحد الأقصى للطلب (تلقائي = الكمية)",
                        value=int(product.get("max_order_qty") or product["quantity"]),
                        min_value=1,
                        key=f"max_{product['id']}"
                    )

                    # استبدال الصورة
                    new_image = st.file_uploader(
                        "استبدال الصورة",
                        type=["png","jpg","jpeg"],
                        key=f"img_{product['id']}"
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button(
                            "حفظ التعديل",
                            key=f"save_{product['id']}"
                        ):
                            update_data = {
                                "quantity": new_qty,
                                "selling_price": new_price,
                                "max_order_qty": new_max
                            }

                            if new_image:
                                file_name = f"{uuid.uuid4()}.jpg"
                                supabase.storage.from_(
                                    "products"
                                ).upload(
                                    file_name,
                                    new_image.getvalue()
                                )
                                update_data["image_url"] = (
                                    f"{SUPABASE_URL}/storage/v1/object/public/products/{file_name}"
                                )

                            supabase.table(
                                "products"
                            ).update(update_data).eq(
                                "id", product["id"]
                            ).execute()

                            st.success("تم التعديل")

                    with c2:
                        if st.button(
                            "🗑️ حذف المنتج",
                            key=f"delete_{product['id']}"
                        ):
                            st.session_state[
                                f"confirm_delete_{product['id']}"
                            ] = True

                    # تأكيد الحذف
                    if st.session_state.get(
                        f"confirm_delete_{product['id']}"
                    ):
                        st.warning("⚠️ هل أنت متأكد من الحذف؟")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            if st.button(
                                "نعم، احذف",
                                key=f"yes_{product['id']}"
                            ):
                                supabase.table(
                                    "products"
                                ).delete().eq(
                                    "id", product["id"]
                                ).execute()
                                st.success("تم الحذف")
                                st.rerun()
                        with cc2:
                            if st.button(
                                "إلغاء",
                                key=f"no_{product['id']}"
                            ):
                                st.session_state[
                                    f"confirm_delete_{product['id']}"
                                ] = False

    # =====================================
    # البيع
    # =====================================

    elif choice == "تسجيل عملية بيع":

        st.header("💵 تسجيل عملية بيع")

        products = supabase.table(
            "products"
        ).select("*").execute().data

        available_products = [
            p for p in products
            if p["quantity"] > 0
        ]

        names = [p["name"] for p in available_products]

        selected = st.selectbox("اختر المنتج", names)

        qty_sell = st.number_input(
            "الكمية",
            min_value=1,
            step=1
        )

        payment_method = st.radio(
            "طريقة الدفع",
            ["cash", "bank"]
        )

        if st.button("إتمام البيع"):

            product = next(
                (p for p in available_products if p["name"] == selected),
                None
            )

            if product:

                if qty_sell > product["quantity"]:
                    st.error("الكمية غير كافية")

                else:

                    total_sale = (
                        product["selling_price"] * qty_sell
                    )

                    total_capital = (
                        product["fixed_capital"] * qty_sell
                    )

                    profit = round(total_sale - total_capital, 2)

                    new_qty = product["quantity"] - qty_sell

                    supabase.table(
                        "products"
                    ).update({
                        "quantity": new_qty
                    }).eq(
                        "id", product["id"]
                    ).execute()

                    users_count = len(st.session_state["users"])
                    share = round(profit / users_count, 2)

                    for user in st.session_state["users"]:

                        existing_wallet = supabase.table(
                            "wallets"
                        ).select("*").eq(
                            "partner_name", user
                        ).execute().data

                        if existing_wallet:
                            current_balance = existing_wallet[0]["balance"]
                            supabase.table(
                                "wallets"
                            ).update({
                                "balance": current_balance + share
                            }).eq(
                                "partner_name", user
                            ).execute()

                    # تحديث رأس المال (إضافة إيراد)
                    existing_capital = supabase.table(
                        "capital_accounts"
                    ).select("*").eq(
                        "account_type", payment_method
                    ).execute().data

                    if existing_capital:
                        current_bal = existing_capital[0]["balance"]
                        supabase.table(
                            "capital_accounts"
                        ).update({
                            "balance": current_bal + total_sale
                        }).eq(
                            "account_type", payment_method
                        ).execute()

                    supabase.table(
                        "transactions"
                    ).insert({
                        "product_name": selected,
                        "quantity": qty_sell,
                        "total": total_sale,
                        "capital": total_capital,
                        "profit": profit,
                        "payment_method": payment_method,
                        "seller": current_user,
                        "created_at": str(datetime.now())
                    }).execute()

                    add_financial_log(
                        "بيع",
                        total_sale,
                        f"{selected} x{qty_sell}",
                        current_user
                    )

                    st.success(f"✅ تم البيع | الربح: {profit} د.ل")

    # =====================================
    # المحافظ والخزائن
    # =====================================

    elif choice == "الخزائن والمحافظ":

        st.header("💰 المحافظ")

        wallets_raw = supabase.table("wallets").select("*").execute().data

        # إزالة التكرار
        seen = set()
        wallets = []
        for w in wallets_raw:
            if w["partner_name"] not in seen:
                seen.add(w["partner_name"])
                wallets.append(w)

        if wallets:
            cols = st.columns(len(wallets))
            for i, wallet in enumerate(wallets):
                with cols[i]:
                    st.metric(f"👤 {wallet['partner_name']}", f"{wallet['balance']} د.ل")

        st.divider()

        tab_withdraw, tab_add = st.tabs(["💸 سحب من المحفظة", "➕ إضافة للمحفظة"])

        with tab_withdraw:

            users_names = list(st.session_state["users"].keys())
            selected_user = st.selectbox("المستخدم", users_names, key="withdraw_user")
            withdraw_amount = st.number_input("المبلغ", min_value=0.0, key="withdraw_amount")

            if st.button("سحب"):

                existing = supabase.table(
                    "wallets"
                ).select("*").eq(
                    "partner_name", selected_user
                ).execute().data

                if existing:
                    current_balance = existing[0]["balance"]
                    if withdraw_amount > current_balance:
                        st.error("الرصيد غير كافي")
                    else:
                        supabase.table("wallets").update({
                            "balance": current_balance - withdraw_amount
                        }).eq("partner_name", selected_user).execute()

                        add_financial_log(
                            "سحب من المحفظة",
                            withdraw_amount,
                            selected_user,
                            current_user
                        )
                        st.success("تم السحب")
                        st.rerun()

        with tab_add:

            users_names2 = list(st.session_state["users"].keys())
            add_user = st.selectbox("المستخدم", users_names2, key="add_wallet_user")
            add_amount = st.number_input("مبلغ الإضافة", min_value=0.0, key="add_wallet_amount")
            add_note = st.text_input("ملاحظة", key="add_wallet_note")

            if st.button("إضافة للمحفظة"):
                existing = supabase.table("wallets").select("*").eq(
                    "partner_name", add_user
                ).execute().data

                if existing:
                    supabase.table("wallets").update({
                        "balance": existing[0]["balance"] + add_amount
                    }).eq("partner_name", add_user).execute()
                else:
                    supabase.table("wallets").insert({
                        "partner_name": add_user,
                        "balance": add_amount
                    }).execute()

                add_financial_log(
                    "إضافة للمحفظة",
                    add_amount,
                    add_note or add_user,
                    current_user
                )
                st.success("✅ تمت الإضافة")
                st.rerun()

    # =====================================
    # رأس المال
    # =====================================

    elif choice == "إدارة رأس المال":

        st.header("🏦 إدارة رأس المال")

        capitals = supabase.table(
            "capital_accounts"
        ).select("*").execute().data

        if capitals:
            for capital in capitals:
                st.info(
                    f"{capital['account_type']} "
                    f"| "
                    f"{capital['balance']} د.ل"
                )

        st.divider()

        action = st.radio("العملية", ["إضافة", "سحب"])
        account_type = st.selectbox("الخزنة", ["cash", "bank"])
        amount = st.number_input("المبلغ", min_value=0.0)

        if st.button("تنفيذ العملية"):

            existing = supabase.table(
                "capital_accounts"
            ).select("*").eq(
                "account_type", account_type
            ).execute().data

            if existing:
                current_balance = existing[0]["balance"]

                if action == "إضافة":
                    new_balance = current_balance + amount
                else:
                    if amount > current_balance:
                        st.error("الرصيد غير كافي")
                        st.stop()
                    new_balance = current_balance - amount

                supabase.table(
                    "capital_accounts"
                ).update({
                    "balance": new_balance
                }).eq(
                    "account_type", account_type
                ).execute()

                add_financial_log(
                    action,
                    amount,
                    account_type,
                    current_user
                )

                st.success("تم التنفيذ")

    # =====================================
    # الطلبات
    # =====================================

    elif choice == "الطلبات":

        st.header("📦 إدارة الطلبات")

        tab1, tab2 = st.tabs(["عرض الطلبات", "إضافة طلب جديد"])

        with tab1:

            # فلاتر البحث
            st.subheader("🔍 بحث وفلترة")
            fc1, fc2, fc3, fc4 = st.columns(4)

            with fc1:
                search_name = st.text_input("بالاسم")
            with fc2:
                search_phone = st.text_input("برقم الهاتف")
            with fc3:
                search_city = st.text_input("بالمدينة")
            with fc4:
                search_status = st.selectbox(
                    "بالحالة",
                    ["الكل", "جديد", "قيد التجهيز", "تم الشحن", "تم التسليم", "ملغي"]
                )

            orders = supabase.table(
                "orders"
            ).select("*").execute().data

            # تطبيق الفلاتر
            if orders:
                if search_name:
                    orders = [o for o in orders if search_name.lower() in o.get("customer_name","").lower()]
                if search_phone:
                    orders = [o for o in orders if search_phone in o.get("phone","")]
                if search_city:
                    orders = [o for o in orders if search_city.lower() in o.get("city","").lower()]
                if search_status != "الكل":
                    orders = [o for o in orders if o.get("status") == search_status]

            st.divider()

            # إحصائيات الطلبات
            all_orders = supabase.table("orders").select("*").execute().data
            if all_orders:
                oc1, oc2, oc3, oc4 = st.columns(4)
                with oc1:
                    st.metric("🆕 جديد", len([o for o in all_orders if o.get("status") == "جديد"]))
                with oc2:
                    st.metric("⚙️ قيد التجهيز", len([o for o in all_orders if o.get("status") == "قيد التجهيز"]))
                with oc3:
                    st.metric("✅ مكتمل", len([o for o in all_orders if o.get("status") == "تم التسليم"]))
                with oc4:
                    st.metric("❌ ملغي", len([o for o in all_orders if o.get("status") == "ملغي"]))

            st.divider()

            if orders:
                for order in orders:

                    status_color = {
                        "جديد": "🔵",
                        "قيد التجهيز": "🟡",
                        "تم الشحن": "🟠",
                        "تم التسليم": "🟢",
                        "ملغي": "🔴"
                    }.get(order.get("status", "جديد"), "⚪")

                    with st.expander(
                        f"{status_color} {order.get('customer_name')} | {order.get('product_name')} | {order.get('status','جديد')}"
                    ):
                        ic1, ic2 = st.columns(2)

                        with ic1:
                            st.write(f"👤 **الاسم:** {order.get('customer_name')}")
                            st.write(f"📞 **الهاتف:** {order.get('phone')}")
                            st.write(f"🏙️ **المدينة:** {order.get('city')}")
                            st.write(f"📍 **العنوان:** {order.get('address')}")

                        with ic2:
                            st.write(f"🛒 **المنتج:** {order.get('product_name')}")
                            st.write(f"📦 **الكمية:** {order.get('quantity')}")
                            st.write(f"💰 **الإجمالي:** {order.get('total_price', 0)} د.ل")
                            st.write(f"📝 **ملاحظات:** {order.get('notes', '-')}")

                        # تغيير الحالة
                        new_status = st.selectbox(
                            "تغيير الحالة",
                            ["جديد", "قيد التجهيز", "تم الشحن", "تم التسليم", "ملغي"],
                            index=["جديد", "قيد التجهيز", "تم الشحن", "تم التسليم", "ملغي"].index(
                                order.get("status", "جديد")
                            ),
                            key=f"status_{order['id']}"
                        )

                        sc1, sc2, sc3 = st.columns(3)

                        with sc1:
                            if st.button("💾 حفظ الحالة", key=f"save_status_{order['id']}"):

                                supabase.table("orders").update({
                                    "status": new_status,
                                    "managed_by": current_user
                                }).eq("id", order["id"]).execute()

                                # إذا تم التسليم، احسب الربح
                                if new_status == "تم التسليم" and order.get("status") != "تم التسليم":

                                    products_list = supabase.table("products").select("*").eq(
                                        "name", order.get("product_name")
                                    ).execute().data

                                    if products_list:
                                        p = products_list[0]
                                        total_sale = order.get("total_price", 0)
                                        total_cap = p["fixed_capital"] * order.get("quantity", 1)
                                        profit = round(total_sale - total_cap, 2)

                                        # خصم الكمية من المخزون
                                        new_stock = max(0, p["quantity"] - order.get("quantity", 1))
                                        supabase.table("products").update({
                                            "quantity": new_stock
                                        }).eq("id", p["id"]).execute()

                                        users_count = len(st.session_state["users"])
                                        share = round(profit / users_count, 2)

                                        for user in st.session_state["users"]:
                                            w = supabase.table("wallets").select("*").eq(
                                                "partner_name", user
                                            ).execute().data
                                            if w:
                                                supabase.table("wallets").update({
                                                    "balance": w[0]["balance"] + share
                                                }).eq("partner_name", user).execute()

                                        supabase.table("transactions").insert({
                                            "product_name": order.get("product_name"),
                                            "quantity": order.get("quantity"),
                                            "total": total_sale,
                                            "capital": total_cap,
                                            "profit": profit,
                                            "payment_method": "cash",
                                            "seller": current_user,
                                            "created_at": str(datetime.now())
                                        }).execute()

                                        add_financial_log(
                                            "إتمام طلب",
                                            total_sale,
                                            order.get("product_name"),
                                            current_user
                                        )

                                st.success("تم تحديث الحالة")
                                st.rerun()

                        with sc2:
                            # واتساب للزبون
                            wa_msg = (
                                f"مرحباً {order.get('customer_name')}،\n"
                                f"طلبك: {order.get('product_name')} x{order.get('quantity')}\n"
                                f"الحالة: {new_status}\n"
                                f"شكراً لتعاملكم مع متجر رنيم 🛍️"
                            )
                            wa_url = send_whatsapp(
                                order.get("phone", ""),
                                wa_msg
                            )
                            st.markdown(
                                f'<a href="{wa_url}" target="_blank">'
                                f'<button style="background:#25D366;color:white;border:none;'
                                f'padding:8px 16px;border-radius:8px;cursor:pointer;width:100%">'
                                f'📱 واتساب الزبون</button></a>',
                                unsafe_allow_html=True
                            )

                        with sc3:
                            if st.button("🗑️ حذف", key=f"del_order_{order['id']}"):
                                supabase.table("orders").delete().eq(
                                    "id", order["id"]
                                ).execute()
                                st.success("تم الحذف")
                                st.rerun()

            else:
                st.info("لا توجد طلبات")

        with tab2:

            st.subheader("➕ إضافة طلب جديد")

            products = supabase.table("products").select("*").execute().data
            product_names = [p["name"] for p in products if p["quantity"] > 0]

            o_name = st.text_input("اسم الزبون")
            o_phone = st.text_input("رقم الهاتف")
            o_city = st.text_input("المدينة")
            o_address = st.text_area("أقرب نقطة دالة / العنوان التفصيلي")
            o_product = st.selectbox("المنتج", product_names)
            o_qty = st.number_input("الكمية", min_value=1, step=1)
            o_notes = st.text_area("ملاحظات إضافية")

            # حساب السعر الإجمالي
            selected_product = next(
                (p for p in products if p["name"] == o_product), None
            )
            if selected_product:
                o_total = selected_product["selling_price"] * o_qty
                st.info(f"💰 الإجمالي: {o_total} د.ل")

            if st.button("✅ تأكيد الطلب"):

                if not o_name or not o_phone:
                    st.error("يرجى إدخال الاسم والهاتف")
                else:
                    supabase.table("orders").insert({
                        "customer_name": o_name,
                        "phone": o_phone,
                        "city": o_city,
                        "address": o_address,
                        "product_name": o_product,
                        "quantity": o_qty,
                        "total_price": o_total if selected_product else 0,
                        "notes": o_notes,
                        "status": "جديد",
                        "managed_by": current_user,
                        "created_at": str(datetime.now())
                    }).execute()

                    # إرسال واتساب للإدارة
                    settings = st.session_state["store_settings"]
                    wa_number = settings["whatsapp_number"]
                    wa_msg = (
                        f"🛍️ طلب جديد!\n"
                        f"👤 الاسم: {o_name}\n"
                        f"📞 الهاتف: {o_phone}\n"
                        f"🏙️ المدينة: {o_city}\n"
                        f"📍 العنوان: {o_address}\n"
                        f"🛒 المنتج: {o_product}\n"
                        f"📦 الكمية: {o_qty}\n"
                        f"💰 الإجمالي: {o_total if selected_product else 0} د.ل\n"
                        f"📝 ملاحظات: {o_notes}"
                    )
                    wa_url = send_whatsapp(wa_number, wa_msg)

                    st.success("✅ تم تأكيد الطلب")
                    st.markdown(
                        f'<a href="{wa_url}" target="_blank">'
                        f'<button style="background:#25D366;color:white;border:none;'
                        f'padding:10px 20px;border-radius:8px;cursor:pointer">'
                        f'📱 إرسال إشعار واتساب للإدارة</button></a>',
                        unsafe_allow_html=True
                    )

    # =====================================
    # البحث
    # =====================================

    elif choice == "البحث":

        st.header("🔍 البحث في النظام")

        search_section = st.radio(
            "ابحث في",
            ["المنتجات", "المبيعات", "الطلبات", "السجل المالي"]
        )

        search_query = st.text_input("كلمة البحث")

        if search_query:

            if search_section == "المنتجات":
                data = supabase.table("products").select("*").execute().data
                results = [
                    p for p in data
                    if search_query.lower() in p["name"].lower()
                ]
                st.subheader(f"النتائج ({len(results)})")
                for r in results:
                    st.info(
                        f"📦 {r['name']} | "
                        f"الكمية: {r['quantity']} | "
                        f"السعر: {r['selling_price']} د.ل"
                    )

            elif search_section == "المبيعات":
                data = supabase.table("transactions").select("*").execute().data
                results = [
                    t for t in data
                    if search_query.lower() in t["product_name"].lower()
                    or search_query.lower() in t.get("seller","").lower()
                ]
                st.subheader(f"النتائج ({len(results)})")
                for r in results:
                    st.info(
                        f"🛒 {r['product_name']} | "
                        f"الكمية: {r['quantity']} | "
                        f"الربح: {r['profit']} د.ل | "
                        f"البائع: {r['seller']}"
                    )

            elif search_section == "الطلبات":
                data = supabase.table("orders").select("*").execute().data
                results = [
                    o for o in data
                    if search_query.lower() in o.get("customer_name","").lower()
                    or search_query in o.get("phone","")
                    or search_query.lower() in o.get("city","").lower()
                    or search_query.lower() in o.get("product_name","").lower()
                ]
                st.subheader(f"النتائج ({len(results)})")
                for r in results:
                    st.info(
                        f"👤 {r.get('customer_name')} | "
                        f"📞 {r.get('phone')} | "
                        f"🛒 {r.get('product_name')} | "
                        f"📌 {r.get('status')}"
                    )

            elif search_section == "السجل المالي":
                data = supabase.table("financial_logs").select("*").execute().data
                results = [
                    l for l in data
                    if search_query.lower() in l.get("action_type","").lower()
                    or search_query.lower() in l.get("note","").lower()
                    or search_query.lower() in l.get("user_name","").lower()
                ]
                st.subheader(f"النتائج ({len(results)})")
                for r in results:
                    st.info(
                        f"🧾 {r['action_type']} | "
                        f"💰 {r['amount']} د.ل | "
                        f"👤 {r['user_name']}"
                    )

    # =====================================
    # سجل العمليات
    # =====================================

    elif choice == "سجل العمليات":

        st.header("📋 سجل العمليات")

        logs = supabase.table(
            "financial_logs"
        ).select("*").execute().data

        if logs:
            # فلتر بالمستخدم
            users_filter = ["الكل"] + list(st.session_state["users"].keys())
            selected_filter = st.selectbox("فلترة بالمستخدم", users_filter)

            if selected_filter != "الكل":
                logs = [l for l in logs if l.get("user_name") == selected_filter]

            st.info(f"إجمالي العمليات: {len(logs)}")

            for log in reversed(logs):
                st.info(f"""
🧾 **العملية:** {log['action_type']}
💰 **القيمة:** {log['amount']} د.ل
📝 **الملاحظة:** {log['note']}
👤 **المستخدم:** {log['user_name']}
🕒 {log['created_at']}
""")
        else:
            st.info("لا توجد عمليات مسجلة")

    # =====================================
    # السجل المالي
    # =====================================

    elif choice == "السجل المالي":

        st.header("📚 السجل المالي")

        logs = supabase.table(
            "financial_logs"
        ).select("*").execute().data

        if logs:
            for log in reversed(logs):
                st.info(f"""
🧾 العملية: {log['action_type']}
💰 القيمة: {log['amount']}
📝 الملاحظة: {log['note']}
👤 المستخدم: {log['user_name']}
🕒 {log['created_at']}
""")

    # =====================================
    # سجل المبيعات
    # =====================================

    elif choice == "سجل المبيعات":

        st.header("📑 سجل المبيعات")

        sales = supabase.table(
            "transactions"
        ).select("*").execute().data

        if sales:
            total = sum(s["profit"] for s in sales)
            st.success(f"📈 إجمالي الأرباح: {round(total, 2)} د.ل")

            for sale in reversed(sales):
                st.info(f"""
🛒 المنتج: {sale['product_name']}
📦 الكمية: {sale['quantity']}
💰 الإجمالي: {sale['total']}
📈 الربح: {sale['profit']}
👤 البائع: {sale['seller']}
🕒 {sale['created_at']}
""")

    # =====================================
    # إحصائيات متقدمة
    # =====================================

    elif choice == "إحصائيات متقدمة":

        st.header("📊 إحصائيات متقدمة")

        transactions = supabase.table("transactions").select("*").execute().data
        orders = supabase.table("orders").select("*").execute().data
        products = supabase.table("products").select("*").execute().data

        if transactions:
            df = pd.DataFrame(transactions)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["date"] = df["created_at"].dt.date

            # أفضل المنتجات
            st.subheader("🏆 أفضل المنتجات مبيعاً")
            best = df.groupby("product_name")["quantity"].sum().sort_values(ascending=False)
            st.bar_chart(best)

            # أرباح يومية
            st.subheader("📈 الأرباح اليومية")
            daily = df.groupby("date")["profit"].sum()
            st.line_chart(daily)

            # أداء المستخدمين
            st.subheader("👤 أداء البائعين")
            sellers = df.groupby("seller")["profit"].sum().sort_values(ascending=False)
            st.bar_chart(sellers)

            # ملخص أرقام
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("إجمالي الأرباح", f"{round(df['profit'].sum(), 2)} د.ل")
            with sc2:
                st.metric("إجمالي المبيعات", f"{round(df['total'].sum(), 2)} د.ل")
            with sc3:
                st.metric("عدد العمليات", len(df))

        else:
            st.info("لا توجد بيانات كافية للإحصائيات")

        # إحصائيات الطلبات
        if orders:
            st.divider()
            st.subheader("📦 إحصائيات الطلبات")
            df_orders = pd.DataFrame(orders)
            status_counts = df_orders["status"].value_counts()
            st.bar_chart(status_counts)

    # =====================================
    # إدارة المستخدمين
    # =====================================

    elif choice == "إدارة المستخدمين":

        if current_role != "admin":
            st.error("⛔ ليس لديك صلاحية لهذا القسم")
        else:
            st.header("👥 إدارة المستخدمين")

            st.subheader("المستخدمون الحاليون")

            for user, data in st.session_state["users"].items():
                if isinstance(data, dict):
                    role = data.get("role", "staff")
                    st.info(f"👤 {user} | الدور: {role}")
                else:
                    st.info(f"👤 {user}")

            st.divider()

            st.subheader("➕ إضافة مستخدم")

            new_user = st.text_input("اسم المستخدم")
            new_token = st.text_input("الرمز السري")
            new_role = st.selectbox("الصلاحية", ["admin", "staff"])

            if st.button("إضافة المستخدم"):

                st.session_state["users"][new_user] = {
                    "password": new_token,
                    "role": new_role
                }

                save_user_to_supabase(new_user, new_token, new_role)

                existing_wallet = supabase.table(
                    "wallets"
                ).select("*").eq(
                    "partner_name", new_user
                ).execute().data

                if not existing_wallet:
                    supabase.table("wallets").insert({
                        "partner_name": new_user,
                        "balance": 0
                    }).execute()

                st.success("تم إضافة المستخدم")

            st.divider()

            st.subheader("🔑 تغيير كلمة المرور")
            change_user = st.selectbox(
                "المستخدم",
                list(st.session_state["users"].keys())
            )
            new_pass = st.text_input("كلمة المرور الجديدة", type="password")

            if st.button("تحديث كلمة المرور"):
                if isinstance(st.session_state["users"][change_user], dict):
                    st.session_state["users"][change_user]["password"] = new_pass
                    role = st.session_state["users"][change_user].get("role", "staff")
                else:
                    st.session_state["users"][change_user] = {
                        "password": new_pass,
                        "role": "staff"
                    }
                    role = "staff"
                save_user_to_supabase(change_user, new_pass, role)
                st.success("تم التحديث")

    # =====================================
    # إعدادات المتجر
    # =====================================

    elif choice == "إعدادات المتجر":

        if current_role != "admin":
            st.error("⛔ ليس لديك صلاحية لهذا القسم")
        else:
            st.header("⚙️ إعدادات المتجر")
            st.caption("كل تغيير هنا يظهر فوراً في متجر الزبائن")

            settings = st.session_state["store_settings"]

            tab1, tab2, tab3, tab4 = st.tabs([
                "🏪 المعلومات الأساسية",
                "🎨 التصميم والألوان",
                "📦 إدارة المنتجات في المتجر",
                "🔧 إعدادات متقدمة"
            ])

            # ── تاب 1: المعلومات الأساسية ──
            with tab1:
                st.subheader("🏪 معلومات المتجر")

                new_name = st.text_input(
                    "اسم المتجر",
                    value=settings.get("store_name", "RANIM")
                )
                new_welcome = st.text_input(
                    "الجملة الترحيبية (تظهر تحت الاسم)",
                    value=settings.get("welcome_message", "مجوهرات فاخرة تليق بك")
                )
                new_wa = st.text_input(
                    "رقم واتساب الإدارة (مع كود الدولة بدون +)",
                    value=settings.get("whatsapp_number", "218910000000")
                )
                new_btn_text = st.text_input(
                    "نص زر إضافة للسلة",
                    value=settings.get("btn_text", "🛒 أضف للسلة")
                )

                st.divider()
                st.subheader("🖼️ شعار المتجر")
                current_logo = settings.get("logo_url", "")
                if current_logo:
                    st.image(current_logo, width=140)
                    st.caption("الشعار الحالي")

                logo_file = st.file_uploader("رفع شعار جديد", type=["png","jpg","jpeg"])
                new_logo  = current_logo
                if logo_file:
                    try:
                        logo_name = f"logo_{uuid.uuid4()}.png"
                        supabase.storage.from_("products").upload(logo_name, logo_file.getvalue())
                        new_logo = f"{SUPABASE_URL}/storage/v1/object/public/products/{logo_name}"
                        st.image(new_logo, width=140)
                        st.success("✅ تم رفع الشعار")
                    except Exception as e:
                        st.error(f"خطأ: {e}")

                if st.button("💾 حفظ المعلومات الأساسية"):
                    settings.update({
                        "store_name":      new_name,
                        "welcome_message": new_welcome,
                        "whatsapp_number": new_wa,
                        "logo_url":        new_logo,
                        "btn_text":        new_btn_text
                    })
                    st.session_state["store_settings"] = settings
                    try:
                        ex = supabase.table("store_settings").select("*").execute().data
                        if ex:
                            supabase.table("store_settings").update(settings).eq("id", ex[0]["id"]).execute()
                        else:
                            supabase.table("store_settings").insert(settings).execute()
                    except Exception:
                        pass
                    st.success("✅ تم الحفظ — يظهر فوراً في متجر الزبائن")
                    st.rerun()

            # ── تاب 2: التصميم والألوان ──
            with tab2:
                st.subheader("🎨 تخصيص الألوان")

                col_a, col_b = st.columns(2)
                with col_a:
                    new_primary = st.color_picker(
                        "اللون الرئيسي (الأزرار والعناوين)",
                        value=settings.get("color_primary", "#c9848a")
                    )
                    new_bg = st.color_picker(
                        "لون الخلفية",
                        value=settings.get("color_bg", "#f9eced")
                    )
                with col_b:
                    new_accent = st.color_picker(
                        "لون التمييز (الأسعار)",
                        value=settings.get("color_accent", "#c9a96e")
                    )
                    new_text_color = st.color_picker(
                        "لون النصوص",
                        value=settings.get("color_text", "#4a2c2e")
                    )

                st.divider()
                st.subheader("👁️ معاينة الألوان")
                st.markdown(f"""
                <div style="background:{new_bg};padding:20px;border-radius:12px;text-align:center">
                    <div style="color:{new_text_color};font-size:1.4rem;font-weight:700;margin-bottom:8px">
                        {settings.get('store_name','RANIM')}
                    </div>
                    <div style="color:{new_primary};margin-bottom:12px">
                        {settings.get('welcome_message','مجوهرات فاخرة')}
                    </div>
                    <span style="background:{new_primary};color:white;padding:8px 20px;border-radius:10px;margin-left:8px">
                        {settings.get('btn_text','🛒 أضف للسلة')}
                    </span>
                    <span style="color:{new_accent};font-weight:700;margin-right:8px">150 د.ل</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button("💾 حفظ الألوان"):
                    settings.update({
                        "color_primary": new_primary,
                        "color_accent":  new_accent,
                        "color_bg":      new_bg,
                        "color_text":    new_text_color
                    })
                    st.session_state["store_settings"] = settings
                    try:
                        ex = supabase.table("store_settings").select("*").execute().data
                        if ex:
                            supabase.table("store_settings").update(settings).eq("id", ex[0]["id"]).execute()
                        else:
                            supabase.table("store_settings").insert(settings).execute()
                    except Exception:
                        pass
                    st.success("✅ تم حفظ الألوان")
                    st.rerun()

            # ── تاب 3: إدارة إظهار المنتجات ──
            with tab3:
                st.subheader("📦 تحكم في إظهار المنتجات في المتجر")
                st.caption("يمكنك إخفاء أي منتج من متجر الزبائن دون حذفه")

                products_all = supabase.table("products").select("*").execute().data
                if products_all:
                    for product in products_all:
                        col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                        with col_p1:
                            st.write(f"📦 **{product['name']}** | المخزون: {product['quantity']} | السعر: {product['selling_price']} د.ل")
                        with col_p2:
                            visible = product.get("visible", True)
                            status_label = "🟢 ظاهر" if visible else "🔴 مخفي"
                            st.write(status_label)
                        with col_p3:
                            btn_label = "إخفاء" if visible else "إظهار"
                            if st.button(btn_label, key=f"vis_{product['id']}"):
                                supabase.table("products").update({
                                    "visible": not visible
                                }).eq("id", product["id"]).execute()
                                st.success(f"تم {'إخفاء' if visible else 'إظهار'} المنتج")
                                st.rerun()
                else:
                    st.info("لا توجد منتجات")

            # ── تاب 4: إعدادات متقدمة ──
            with tab4:
                st.subheader("🔧 إعدادات متقدمة")

                # وضع الصيانة
                st.markdown("#### 🚧 وضع الصيانة")
                maintenance = settings.get("maintenance_mode", False)
                new_maintenance = st.toggle(
                    "تفعيل وضع الصيانة (يوقف المتجر مؤقتاً عن الزبائن)",
                    value=maintenance
                )
                maintenance_msg = st.text_input(
                    "رسالة الصيانة للزبائن",
                    value=settings.get("maintenance_msg", "المتجر تحت الصيانة، نعود قريباً 🌸")
                )

                st.divider()

                # رسالة ترحيب مخصصة
                st.markdown("#### 💬 رسالة ترحيب مخصصة")
                custom_banner = st.text_area(
                    "نص البانر (يظهر أسفل الهيرو مباشرة)",
                    value=settings.get("custom_banner", ""),
                    placeholder="مثال: 🎉 عرض خاص — خصم 10% على جميع المنتجات هذا الأسبوع!"
                )

                st.divider()

                # معاينة رابط المتجر
                st.markdown("#### 🔗 روابط المنظومتين")
                st.info("شارك هذه الروابط مع زبائنك وفريق العمل")
                st.code("http://192.168.0.15:8502   ← متجر الزبائن")
                st.code("http://192.168.0.15:8503   ← لوحة الإدارة")
                st.caption("للوصول من أي مكان في العالم استخدم ngrok: pip install pyngrok")

                if st.button("💾 حفظ الإعدادات المتقدمة"):
                    settings.update({
                        "maintenance_mode": new_maintenance,
                        "maintenance_msg":  maintenance_msg,
                        "custom_banner":    custom_banner
                    })
                    st.session_state["store_settings"] = settings
                    try:
                        ex = supabase.table("store_settings").select("*").execute().data
                        if ex:
                            supabase.table("store_settings").update(settings).eq("id", ex[0]["id"]).execute()
                        else:
                            supabase.table("store_settings").insert(settings).execute()
                    except Exception:
                        pass
                    st.success("✅ تم الحفظ")
                    st.rerun()

    # =====================================
    # تصدير البيانات
    # =====================================

    elif choice == "تصدير البيانات":

        if current_role != "admin":
            st.error("⛔ ليس لديك صلاحية لهذا القسم")
        else:
            st.header("📤 تصدير البيانات")

            export_choice = st.selectbox(
                "اختر البيانات للتصدير",
                ["المنتجات", "المبيعات", "الطلبات", "السجل المالي"]
            )

            table_map = {
                "المنتجات": "products",
                "المبيعات": "transactions",
                "الطلبات": "orders",
                "السجل المالي": "financial_logs"
            }

            if st.button("📥 تحميل Excel"):
                data = supabase.table(
                    table_map[export_choice]
                ).select("*").execute().data

                if data:
                    df = pd.DataFrame(data)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name=export_choice)
                    output.seek(0)

                    st.download_button(
                        label=f"⬇️ تحميل {export_choice}.xlsx",
                        data=output.getvalue(),
                        file_name=f"{export_choice}_{datetime.now().date()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("لا توجد بيانات للتصدير")

    # =====================================
    # نسخ احتياطي
    # =====================================

    elif choice == "نسخ احتياطي":

        if current_role != "admin":
            st.error("⛔ ليس لديك صلاحية لهذا القسم")
        else:
            st.header("💾 نسخ احتياطي")

            st.info(
                "هذا القسم يتيح لك تحميل نسخة كاملة من جميع بيانات النظام دفعة واحدة"
            )

            if st.button("📦 تحميل نسخة احتياطية كاملة (Excel)"):

                tables = {
                    "المنتجات": "products",
                    "المبيعات": "transactions",
                    "الطلبات": "orders",
                    "السجل المالي": "financial_logs",
                    "المحافظ": "wallets",
                    "رأس المال": "capital_accounts"
                }

                output = io.BytesIO()

                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    for sheet_name, table_name in tables.items():
                        try:
                            data = supabase.table(
                                table_name
                            ).select("*").execute().data
                            if data:
                                df = pd.DataFrame(data)
                                df.to_excel(
                                    writer,
                                    index=False,
                                    sheet_name=sheet_name
                                )
                        except Exception:
                            pass

                output.seek(0)

                st.download_button(
                    label="⬇️ تحميل النسخة الاحتياطية",
                    data=output.getvalue(),
                    file_name=f"backup_ranim_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.success("✅ جاهز للتحميل!")