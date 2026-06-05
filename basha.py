# =========================================
# Ranim Store Pro - Ultimate Admin System
# =========================================

import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import uuid, qrcode, io, base64
import pandas as pd

st.set_page_config(page_title="Ranim Store Admin", page_icon="🛍️", layout="wide")

SUPABASE_URL = "https://xwwlffppepiwdiekqylr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3d2xmZnBwZXBpd2RpZWtxeWxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2NDcxMjksImV4cCI6MjA5NTIyMzEyOX0.bpWm7U4Z9JybPrEBPWmHhTRGZsq2CaaI7AVnuWKTZNg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================
# CSS - RTL + تصميم محسّن
# =========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');

* { font-family: 'Tajawal', sans-serif !important; direction: rtl; }

.main, .stApp { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; }

/* المجموعات في الشريط الجانبي */
.sidebar-group {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 8px;
    margin-bottom: 8px;
}
.sidebar-group-title {
    color: #94a3b8 !important;
    font-size: 0.75rem;
    letter-spacing: 1px;
    padding: 4px 8px;
    text-transform: uppercase;
}

/* بطاقات الإحصائيات */
.stMetric {
    background: white;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* الأزرار */
div.stButton > button {
    border-radius: 10px;
    height: 42px;
    font-weight: 700;
    width: 100%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.88; }

/* حقول الإدخال */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    text-align: right !important;
    direction: rtl !important;
}

/* بطاقة إشعار */
.notif-card {
    background: white;
    border-right: 4px solid #6366f1;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

h1,h2,h3 { color: #1e293b; }
</style>
""", unsafe_allow_html=True)

# =========================================
# دوال مساعدة
# =========================================
DEFAULT_USERS = {
    "Bashir": {"password": "B2026", "role": "admin"},
    "Ahmed":  {"password": "A2026", "role": "admin"}
}

def load_users():
    try:
        rows = supabase.table("users").select("*").execute().data
        if rows:
            return {r["username"]: {"password": r["password"], "role": r.get("role","staff")} for r in rows}
    except: pass
    return DEFAULT_USERS

def save_user(username, password, role):
    try:
        ex = supabase.table("users").select("*").eq("username", username).execute().data
        if ex: supabase.table("users").update({"password": password, "role": role}).eq("username", username).execute()
        else:  supabase.table("users").insert({"username": username, "password": password, "role": role}).execute()
    except: pass

def load_settings():
    try:
        rows = supabase.table("store_settings").select("*").execute().data
        if rows: return rows[0]
    except: pass
    return {"store_name":"متجر رنيم","welcome_message":"أهلاً بكم","whatsapp_number":"218910000000","logo_url":"","btn_text":"🛒 أضف للسلة","color_primary":"#c9848a","color_accent":"#c9a96e","color_bg":"#f9eced","color_text":"#4a2c2e","maintenance_mode":False,"maintenance_msg":"","custom_banner":""}

def save_settings(s):
    try:
        ex = supabase.table("store_settings").select("*").execute().data
        if ex: supabase.table("store_settings").update(s).eq("id", ex[0]["id"]).execute()
        else:  supabase.table("store_settings").insert(s).execute()
    except: pass

def calculate_capital(price_yuan, weight, pack_cost, bag_cost, dollar_rate, shipping_rate):
    return round((price_yuan*0.14)*dollar_rate + (weight*shipping_rate)*dollar_rate + pack_cost + bag_cost, 2)

def add_log(action_type, amount, note, user_name):
    try:
        supabase.table("financial_logs").insert({
            "action_type": action_type, "amount": amount,
            "note": note, "user_name": user_name, "created_at": str(datetime.now())
        }).execute()
    except: pass

def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

def wa_link(phone, msg):
    return f"https://wa.me/{phone}?text={msg.replace(chr(10),'%0A').replace(' ','%20')}"

def get_wallet(name):
    rows = supabase.table("wallets").select("*").eq("partner_name", name).execute().data
    return rows[0] if rows else None

def ensure_wallet(name):
    if not get_wallet(name):
        supabase.table("wallets").insert({"partner_name": name, "balance": 0}).execute()

def distribute_profit(profit):
    users = st.session_state["users"]
    share = round(profit / len(users), 2) if users else 0
    for user in users:
        w = get_wallet(user)
        if w:
            supabase.table("wallets").update({"balance": w["balance"]+share}).eq("partner_name", user).execute()

# =========================================
# Session State
# =========================================
if "users"          not in st.session_state: st.session_state["users"]          = load_users()
if "logged_user"    not in st.session_state: st.session_state["logged_user"]    = None
if "store_settings" not in st.session_state: st.session_state["store_settings"] = load_settings()
if "notifications"  not in st.session_state: st.session_state["notifications"]  = []

# =========================================
# تسجيل الدخول
# =========================================
if st.session_state["logged_user"] is None:
    s = st.session_state["store_settings"]
    _, col, _ = st.columns([1,2,1])
    with col:
        if s.get("logo_url"):
            st.image(s["logo_url"], width=120)
        st.markdown(f"<h2 style='text-align:center;color:#1e293b'>🛍️ {s.get('store_name','متجر رنيم')}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#64748b'>نظام الإدارة الاحترافي</p>", unsafe_allow_html=True)
        st.divider()
        username = st.text_input("اسم المستخدم")
        password = st.text_input("الرمز السري", type="password")
        if st.button("تسجيل الدخول"):
            users = st.session_state["users"]
            if username in users:
                d = users[username]
                p = d["password"] if isinstance(d,dict) else d
                if p == password:
                    st.session_state["logged_user"] = username
                    st.rerun()
                else: st.error("بيانات غير صحيحة")
            else: st.error("بيانات غير صحيحة")

# =========================================
# داخل النظام
# =========================================
else:
    current_user = st.session_state["logged_user"]
    ud = st.session_state["users"].get(current_user, {})
    current_role = ud.get("role","staff") if isinstance(ud,dict) else "admin"
    s = st.session_state["store_settings"]

    # =====================================
    # الشريط الجانبي المنظم بمجموعات
    # =====================================
    with st.sidebar:
        if s.get("logo_url"): st.image(s["logo_url"], width=90)
        st.markdown(f"### 👤 {current_user}")
        st.caption(f"الدور: {'مدير' if current_role=='admin' else 'موظف'}")
        st.divider()

        if current_role == "admin":
            st.markdown('<div class="sidebar-group-title">📊 الرئيسية</div>', unsafe_allow_html=True)
            if st.button("🏠 لوحة التحكم",      key="nav_home"):    st.session_state["page"] = "الرئيسية"
            if st.button("🔔 الإشعارات",         key="nav_notif"):   st.session_state["page"] = "الإشعارات"
            if st.button("🎯 أهداف المبيعات",    key="nav_goals"):   st.session_state["page"] = "أهداف المبيعات"

            st.markdown("---")
            st.markdown('<div class="sidebar-group-title">🛍️ المتجر</div>', unsafe_allow_html=True)
            if st.button("➕ إضافة منتج",         key="nav_addp"):    st.session_state["page"] = "إضافة منتج"
            if st.button("📦 المنتجات",            key="nav_prods"):   st.session_state["page"] = "المنتجات"
            if st.button("💵 تسجيل بيع",          key="nav_sell"):    st.session_state["page"] = "تسجيل عملية بيع"

            st.markdown("---")
            st.markdown('<div class="sidebar-group-title">📦 الطلبات</div>', unsafe_allow_html=True)
            if st.button("📋 إدارة الطلبات",      key="nav_orders"):  st.session_state["page"] = "الطلبات"

            st.markdown("---")
            st.markdown('<div class="sidebar-group-title">💰 المالية</div>', unsafe_allow_html=True)
            if st.button("💼 المحافظ والخزائن",   key="nav_wallet"):  st.session_state["page"] = "الخزائن والمحافظ"
            if st.button("🏦 رأس المال",           key="nav_cap"):     st.session_state["page"] = "إدارة رأس المال"
            if st.button("📋 سجل العمليات",        key="nav_logs"):    st.session_state["page"] = "سجل العمليات"
            if st.button("📑 سجل المبيعات",        key="nav_sales"):   st.session_state["page"] = "سجل المبيعات"

            st.markdown("---")
            st.markdown('<div class="sidebar-group-title">📊 التقارير</div>', unsafe_allow_html=True)
            if st.button("📈 إحصائيات متقدمة",    key="nav_stats"):   st.session_state["page"] = "إحصائيات متقدمة"
            if st.button("📅 تقرير دوري",          key="nav_report"):  st.session_state["page"] = "تقرير دوري"
            if st.button("🔍 البحث",               key="nav_search"):  st.session_state["page"] = "البحث"

            st.markdown("---")
            st.markdown('<div class="sidebar-group-title">⚙️ الإعدادات</div>', unsafe_allow_html=True)
            if st.button("👥 إدارة المستخدمين",   key="nav_users"):   st.session_state["page"] = "إدارة المستخدمين"
            if st.button("⚙️ إعدادات المتجر",     key="nav_sett"):    st.session_state["page"] = "إعدادات المتجر"
            if st.button("🎁 كوبونات الخصم",       key="nav_coup"):    st.session_state["page"] = "كوبونات الخصم"
            if st.button("📤 تصدير البيانات",      key="nav_export"):  st.session_state["page"] = "تصدير البيانات"
            if st.button("💾 نسخ احتياطي",         key="nav_backup"):  st.session_state["page"] = "نسخ احتياطي"
        else:
            if st.button("🏠 الرئيسية",    key="s_home"):  st.session_state["page"] = "الرئيسية"
            if st.button("📦 المنتجات",    key="s_prods"): st.session_state["page"] = "المنتجات"
            if st.button("💵 تسجيل بيع",  key="s_sell"):  st.session_state["page"] = "تسجيل عملية بيع"
            if st.button("📋 الطلبات",    key="s_ord"):   st.session_state["page"] = "الطلبات"
            if st.button("🔍 البحث",      key="s_srch"):  st.session_state["page"] = "البحث"
            if st.button("📑 المبيعات",   key="s_sale"):  st.session_state["page"] = "سجل المبيعات"

        st.divider()
        if st.button("🚪 تسجيل الخروج", key="logout"):
            st.session_state["logged_user"] = None
            st.rerun()

    if "page" not in st.session_state:
        st.session_state["page"] = "الرئيسية"

    choice = st.session_state["page"]

    # =====================================
    # الرئيسية
    # =====================================
    if choice == "الرئيسية":
        st.title("🏠 لوحة التحكم")

        products     = supabase.table("products").select("*").execute().data
        transactions = supabase.table("transactions").select("*").execute().data
        orders       = supabase.table("orders").select("*").execute().data

        total_profit  = sum(t["profit"] for t in transactions) if transactions else 0
        new_orders    = len([o for o in orders if o.get("status")=="جديد"]) if orders else 0
        low_stock     = [p for p in products if p.get("quantity",0) < 5]

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("📦 المنتجات",    len(products))
        with c2: st.metric("🧾 المبيعات",    len(transactions))
        with c3: st.metric("📈 الأرباح",     f"{round(total_profit,2)} د.ل")
        with c4: st.metric("🆕 طلبات جديدة", new_orders)

        if new_orders > 0:
            st.warning(f"⚠️ لديك {new_orders} طلب جديد في انتظار المراجعة!")
        if low_stock:
            for p in low_stock:
                st.warning(f"⚠️ مخزون منخفض: {p['name']} — متبقي {p['quantity']} فقط!")

        st.divider()
        st.subheader("📋 آخر المبيعات")
        for t in (transactions[-5:][::-1] if transactions else []):
            st.info(f"🛒 {t['product_name']} | الكمية: {t['quantity']} | الربح: {t['profit']} د.ل | البائع: {t['seller']}")

    # =====================================
    # الإشعارات
    # =====================================
    elif choice == "الإشعارات":
        st.title("🔔 الإشعارات")

        products     = supabase.table("products").select("*").execute().data
        orders       = supabase.table("orders").select("*").execute().data
        transactions = supabase.table("transactions").select("*").execute().data

        notifs = []

        # طلبات جديدة
        new_orders = [o for o in orders if o.get("status")=="جديد"]
        if new_orders:
            notifs.append({"icon":"🆕","msg":f"لديك {len(new_orders)} طلب جديد في انتظار المراجعة","color":"#6366f1"})

        # مخزون منخفض
        low = [p for p in products if p.get("quantity",0) < 5]
        for p in low:
            notifs.append({"icon":"⚠️","msg":f"مخزون منخفض: {p['name']} — متبقي {p['quantity']} فقط","color":"#f59e0b"})

        # مبيعات اليوم
        today = datetime.now().date()
        today_sales = [t for t in transactions if str(today) in str(t.get("created_at",""))]
        if today_sales:
            total_today = sum(t["profit"] for t in today_sales)
            notifs.append({"icon":"📈","msg":f"أرباح اليوم: {round(total_today,2)} د.ل من {len(today_sales)} عملية","color":"#10b981"})

        if notifs:
            for n in notifs:
                st.markdown(f"""
                <div style="background:white;border-right:4px solid {n['color']};
                            border-radius:10px;padding:14px 18px;margin-bottom:10px;
                            box-shadow:0 2px 6px rgba(0,0,0,0.06)">
                    <span style="font-size:1.2rem">{n['icon']}</span>
                    <span style="margin-right:10px;color:#1e293b;font-weight:500">{n['msg']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ لا توجد إشعارات جديدة")

    # =====================================
    # أهداف المبيعات
    # =====================================
    elif choice == "أهداف المبيعات":
        st.title("🎯 أهداف المبيعات")

        transactions = supabase.table("transactions").select("*").execute().data

        col1, col2 = st.columns(2)
        with col1:
            monthly_goal = st.number_input("🎯 هدف الأرباح الشهري (د.ل)", min_value=0.0, value=float(st.session_state.get("monthly_goal",5000)))
            if st.button("💾 حفظ الهدف"):
                st.session_state["monthly_goal"] = monthly_goal
                st.success("تم حفظ الهدف")

        # حساب أرباح الشهر الحالي
        this_month = datetime.now().strftime("%Y-%m")
        month_sales = [t for t in transactions if this_month in str(t.get("created_at",""))]
        month_profit = sum(t["profit"] for t in month_sales) if month_sales else 0

        goal = st.session_state.get("monthly_goal", 5000)
        pct  = min(int((month_profit / goal) * 100), 100) if goal > 0 else 0

        with col2:
            st.metric("📈 أرباح هذا الشهر", f"{round(month_profit,2)} د.ل")
            st.metric("🎯 الهدف", f"{goal} د.ل")

        # شريط التقدم
        color = "#10b981" if pct >= 100 else "#6366f1" if pct >= 50 else "#f59e0b"
        st.markdown(f"""
        <div style="background:#f1f5f9;border-radius:20px;height:28px;margin:16px 0;overflow:hidden">
            <div style="background:{color};width:{pct}%;height:100%;border-radius:20px;
                        display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:700;font-size:0.9rem;transition:width 0.5s">
                {pct}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        if pct >= 100: st.balloons(); st.success("🎉 تهانينا! حققت الهدف الشهري!")
        elif pct >= 75: st.info("💪 أنت على وشك تحقيق الهدف!")
        else: st.warning(f"📊 تحتاج {round(goal-month_profit,2)} د.ل إضافية لتحقيق الهدف")

    # =====================================
    # إضافة منتج
    # =====================================
    elif choice == "إضافة منتج":
        st.header("➕ إضافة منتج")

        p_name        = st.text_input("اسم المنتج")
        qty           = st.number_input("الكمية", min_value=1, step=1, value=1)
        price_yuan    = st.number_input("السعر باليوان", min_value=0.0)
        weight        = st.number_input("الوزن", min_value=0.0)
        pack_cost     = st.number_input("التغليف", min_value=0.0)
        bag_cost      = st.number_input("الكيس", min_value=0.0)
        dollar_rate   = st.number_input("الدولار", value=7.1)
        shipping_rate = st.number_input("الشحن", value=12.5)
        max_order_qty = st.number_input("الحد الأقصى للطلب (تلقائي=الكمية)", min_value=1, value=int(qty), step=1)
        purchase_source = st.radio("مصدر الشراء", ["cash","bank"])

        capital = calculate_capital(price_yuan, weight, pack_cost, bag_cost, dollar_rate, shipping_rate)
        st.info(f"💰 رأس المال للقطعة: {capital} د.ل | الإجمالي: {round(capital*qty,2)} د.ل")

        selling_price = st.number_input("سعر البيع", min_value=0.0)
        uploaded_file = st.file_uploader("صورة المنتج", type=["png","jpg","jpeg"])

        if st.button("💾 حفظ المنتج"):
            image_url = ""
            if uploaded_file:
                fn = f"{uuid.uuid4()}.jpg"
                supabase.storage.from_("products").upload(fn, uploaded_file.getvalue())
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/products/{fn}"

            existing = supabase.table("products").select("*").eq("name", p_name).execute().data
            if existing:
                supabase.table("products").update({
                    "quantity": existing[0]["quantity"]+qty,
                    "fixed_capital": capital, "selling_price": selling_price,
                    "image_url": image_url, "max_order_qty": max_order_qty
                }).eq("name", p_name).execute()
            else:
                supabase.table("products").insert({
                    "name": p_name, "quantity": qty, "fixed_capital": capital,
                    "selling_price": selling_price, "image_url": image_url, "max_order_qty": max_order_qty
                }).execute()

            cap_row = supabase.table("capital_accounts").select("*").eq("account_type", purchase_source).execute().data
            if cap_row:
                supabase.table("capital_accounts").update({"balance": cap_row[0]["balance"]-(capital*qty)}).eq("account_type", purchase_source).execute()

            add_log("إضافة بضاعة", capital*qty, p_name, current_user)
            st.success("✅ تم حفظ المنتج")

    # =====================================
    # المنتجات
    # =====================================
    elif choice == "المنتجات":
        st.header("📦 المنتجات")
        products = supabase.table("products").select("*").execute().data

        # رابط متجر الزبائن من الإعدادات
        customer_url = st.session_state["store_settings"].get("customer_url", "https://your-store.streamlit.app")

        if products:
            for product in products:
                with st.expander(f"{product['name']} | المخزون: {product['quantity']}"):
                    col_img, col_qr = st.columns(2)
                    with col_img:
                        if product.get("image_url"): st.image(product["image_url"], width=200)
                    with col_qr:
                        st.markdown("**QR Code — يفتح المتجر مباشرة:**")
                        # QR يحتوي رابط المتجر مع اسم المنتج كبارامتر
                        product_url = f"{customer_url}?product={product['name']}"
                        qr_img = generate_qr(product_url)
                        st.markdown(f'<img src="{qr_img}" width="150"/>', unsafe_allow_html=True)
                        st.caption(f"الرابط: {product_url}")

                    new_qty   = st.number_input("الكمية",    value=product["quantity"],             key=f"qty_{product['id']}")
                    new_price = st.number_input("سعر البيع", value=float(product["selling_price"]),  key=f"price_{product['id']}")
                    new_max   = st.number_input("الحد الأقصى للطلب", value=int(product.get("max_order_qty") or product["quantity"]), min_value=1, key=f"max_{product['id']}")
                    new_image = st.file_uploader("استبدال الصورة", type=["png","jpg","jpeg"], key=f"img_{product['id']}")

                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button("💾 حفظ التعديل", key=f"save_{product['id']}"):
                            upd = {"quantity": new_qty, "selling_price": new_price, "max_order_qty": new_max}
                            if new_image:
                                fn = f"{uuid.uuid4()}.jpg"
                                supabase.storage.from_("products").upload(fn, new_image.getvalue())
                                upd["image_url"] = f"{SUPABASE_URL}/storage/v1/object/public/products/{fn}"
                            supabase.table("products").update(upd).eq("id", product["id"]).execute()
                            st.success("✅ تم التعديل"); st.rerun()
                    with c2:
                        if st.button("🗑️ حذف", key=f"delete_{product['id']}"):
                            st.session_state[f"confirm_{product['id']}"] = True

                    if st.session_state.get(f"confirm_{product['id']}"):
                        st.warning("⚠️ هل أنت متأكد؟")
                        cc1,cc2 = st.columns(2)
                        with cc1:
                            if st.button("نعم احذف", key=f"yes_{product['id']}"):
                                supabase.table("products").delete().eq("id", product["id"]).execute()
                                st.rerun()
                        with cc2:
                            if st.button("إلغاء", key=f"no_{product['id']}"):
                                st.session_state[f"confirm_{product['id']}"] = False
        else:
            st.info("لا توجد منتجات")

    # =====================================
    # تسجيل عملية بيع
    # =====================================
    elif choice == "تسجيل عملية بيع":
        st.header("💵 تسجيل عملية بيع")
        products = supabase.table("products").select("*").execute().data
        avail = [p for p in products if p["quantity"]>0]
        if not avail:
            st.warning("لا توجد منتجات متاحة")
        else:
            selected       = st.selectbox("المنتج", [p["name"] for p in avail])
            qty_sell       = st.number_input("الكمية", min_value=1, step=1)
            payment_method = st.radio("طريقة الدفع", ["cash","bank"])

            if st.button("✅ إتمام البيع"):
                product = next((p for p in avail if p["name"]==selected), None)
                if product:
                    if qty_sell > product["quantity"]: st.error("الكمية غير كافية")
                    else:
                        total_sale    = product["selling_price"] * qty_sell
                        total_capital = product["fixed_capital"]  * qty_sell
                        profit        = round(total_sale - total_capital, 2)

                        supabase.table("products").update({"quantity": product["quantity"]-qty_sell}).eq("id", product["id"]).execute()
                        distribute_profit(profit)

                        cap_row = supabase.table("capital_accounts").select("*").eq("account_type", payment_method).execute().data
                        if cap_row:
                            supabase.table("capital_accounts").update({"balance": cap_row[0]["balance"]+total_sale}).eq("account_type", payment_method).execute()

                        supabase.table("transactions").insert({
                            "product_name": selected, "quantity": qty_sell, "total": total_sale,
                            "capital": total_capital, "profit": profit, "payment_method": payment_method,
                            "seller": current_user, "created_at": str(datetime.now())
                        }).execute()
                        add_log("بيع", total_sale, f"{selected} x{qty_sell}", current_user)
                        st.success(f"✅ تم البيع | الربح: {profit} د.ل")

    # =====================================
    # المحافظ والخزائن
    # =====================================
    elif choice == "الخزائن والمحافظ":
        st.header("💰 المحافظ والخزائن")

        wallets_raw = supabase.table("wallets").select("*").execute().data
        seen, wallets = set(), []
        for w in wallets_raw:
            if w["partner_name"] not in seen:
                seen.add(w["partner_name"]); wallets.append(w)

        if wallets:
            cols = st.columns(len(wallets))
            for i,w in enumerate(wallets):
                with cols[i]: st.metric(f"👤 {w['partner_name']}", f"{w['balance']} د.ل")

        st.divider()
        tab_w, tab_a = st.tabs(["💸 سحب من المحفظة","➕ إضافة للمحفظة"])

        with tab_w:
            sel_u = st.selectbox("المستخدم", list(st.session_state["users"].keys()), key="wu")
            w_amt = st.number_input("مبلغ السحب", min_value=0.0, key="wa")
            if st.button("💸 سحب"):
                w = get_wallet(sel_u)
                if w:
                    if w_amt > w["balance"]: st.error("الرصيد غير كافي")
                    else:
                        supabase.table("wallets").update({"balance": w["balance"]-w_amt}).eq("partner_name", sel_u).execute()
                        add_log("سحب من المحفظة", w_amt, sel_u, current_user)
                        st.success("✅ تم السحب"); st.rerun()

        with tab_a:
            sel_u2 = st.selectbox("المستخدم", list(st.session_state["users"].keys()), key="au")
            a_amt  = st.number_input("مبلغ الإضافة", min_value=0.0, key="aa")
            a_note = st.text_input("ملاحظة", key="an")
            if st.button("➕ إضافة"):
                w = get_wallet(sel_u2)
                if w: supabase.table("wallets").update({"balance": w["balance"]+a_amt}).eq("partner_name", sel_u2).execute()
                else: supabase.table("wallets").insert({"partner_name": sel_u2, "balance": a_amt}).execute()
                add_log("إضافة للمحفظة", a_amt, a_note or sel_u2, current_user)
                st.success("✅ تمت الإضافة"); st.rerun()

    # =====================================
    # رأس المال
    # =====================================
    elif choice == "إدارة رأس المال":
        st.header("🏦 إدارة رأس المال")
        capitals = supabase.table("capital_accounts").select("*").execute().data
        if capitals:
            cols = st.columns(len(capitals))
            for i,c in enumerate(capitals):
                with cols[i]: st.metric(f"🏦 {c['account_type']}", f"{c['balance']} د.ل")
        st.divider()
        action       = st.radio("العملية", ["إضافة","سحب"])
        account_type = st.selectbox("الخزنة", ["cash","bank"])
        amount       = st.number_input("المبلغ", min_value=0.0)
        if st.button("✅ تنفيذ"):
            ex = supabase.table("capital_accounts").select("*").eq("account_type", account_type).execute().data
            if ex:
                bal = ex[0]["balance"]
                if action == "إضافة": new_bal = bal + amount
                else:
                    if amount > bal: st.error("الرصيد غير كافي"); st.stop()
                    new_bal = bal - amount
                supabase.table("capital_accounts").update({"balance": new_bal}).eq("account_type", account_type).execute()
                add_log(action, amount, account_type, current_user)
                st.success("✅ تم التنفيذ"); st.rerun()

    # =====================================
    # الطلبات
    # =====================================
    elif choice == "الطلبات":
        st.header("📦 إدارة الطلبات")
        tab1, tab2 = st.tabs(["📋 عرض الطلبات","➕ إضافة طلب"])

        with tab1:
            fc1,fc2,fc3,fc4 = st.columns(4)
            with fc1: sn = st.text_input("بالاسم")
            with fc2: sp = st.text_input("بالهاتف")
            with fc3: sc = st.text_input("بالمدينة")
            with fc4: ss = st.selectbox("بالحالة", ["الكل","جديد","قيد التجهيز","تم الشحن","تم التسليم","ملغي"])

            all_orders = supabase.table("orders").select("*").execute().data
            if all_orders:
                oc1,oc2,oc3,oc4 = st.columns(4)
                with oc1: st.metric("🆕 جديد",        len([o for o in all_orders if o.get("status")=="جديد"]))
                with oc2: st.metric("⚙️ قيد التجهيز", len([o for o in all_orders if o.get("status")=="قيد التجهيز"]))
                with oc3: st.metric("✅ مكتمل",        len([o for o in all_orders if o.get("status")=="تم التسليم"]))
                with oc4: st.metric("❌ ملغي",         len([o for o in all_orders if o.get("status")=="ملغي"]))

            orders = list(all_orders) if all_orders else []
            if sn: orders = [o for o in orders if sn.lower() in o.get("customer_name","").lower()]
            if sp: orders = [o for o in orders if sp in o.get("phone","")]
            if sc: orders = [o for o in orders if sc.lower() in o.get("city","").lower()]
            if ss != "الكل": orders = [o for o in orders if o.get("status")==ss]

            st.divider()
            statuses  = ["جديد","قيد التجهيز","تم الشحن","تم التسليم","ملغي"]
            color_map = {"جديد":"🔵","قيد التجهيز":"🟡","تم الشحن":"🟠","تم التسليم":"🟢","ملغي":"🔴"}

            if orders:
                for order in orders:
                    clr = color_map.get(order.get("status","جديد"),"⚪")
                    with st.expander(f"{clr} {order.get('customer_name')} | {order.get('product_name')} | {order.get('status','جديد')}"):
                        ic1,ic2 = st.columns(2)
                        with ic1:
                            st.write(f"👤 **الاسم:** {order.get('customer_name')}")
                            st.write(f"📞 **الهاتف:** {order.get('phone')}")
                            st.write(f"🏙️ **المدينة:** {order.get('city')}")
                            st.write(f"📍 **العنوان:** {order.get('address')}")
                        with ic2:
                            st.write(f"🛒 **المنتج:** {order.get('product_name')}")
                            st.write(f"📦 **الكمية:** {order.get('quantity')}")
                            st.write(f"💰 **الإجمالي:** {order.get('total_price',0)} د.ل")
                            st.write(f"📝 **ملاحظات:** {order.get('notes','-')}")

                        cur = order.get("status","جديد")
                        new_status = st.selectbox("تغيير الحالة", statuses, index=statuses.index(cur) if cur in statuses else 0, key=f"st_{order['id']}")
                        sc1,sc2,sc3 = st.columns(3)

                        with sc1:
                            if st.button("💾 حفظ الحالة", key=f"ss_{order['id']}"):
                                supabase.table("orders").update({"status": new_status,"managed_by": current_user}).eq("id", order["id"]).execute()
                                if new_status == "تم التسليم" and cur != "تم التسليم":
                                    pr = supabase.table("products").select("*").eq("name", order.get("product_name")).execute().data
                                    if pr:
                                        p = pr[0]
                                        total_sale = order.get("total_price",0)
                                        total_cap  = p["fixed_capital"] * order.get("quantity",1)
                                        profit     = round(total_sale - total_cap, 2)
                                        supabase.table("products").update({"quantity": max(0, p["quantity"]-order.get("quantity",1))}).eq("id", p["id"]).execute()
                                        distribute_profit(profit)
                                        supabase.table("transactions").insert({
                                            "product_name": order.get("product_name"), "quantity": order.get("quantity"),
                                            "total": total_sale, "capital": total_cap, "profit": profit,
                                            "payment_method": "cash", "seller": current_user, "created_at": str(datetime.now())
                                        }).execute()
                                        add_log("إتمام طلب", total_sale, order.get("product_name"), current_user)
                                st.success("✅ تم التحديث"); st.rerun()

                        with sc2:
                            msg = f"مرحباً {order.get('customer_name')}،\nطلبك: {order.get('product_name')} x{order.get('quantity')}\nالحالة: {new_status}\nشكراً لتعاملكم مع {s['store_name']} 🛍️"
                            st.markdown(f'<a href="{wa_link(order.get("phone",""), msg)}" target="_blank"><button style="background:#25D366;color:white;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;width:100%">📱 واتساب الزبون</button></a>', unsafe_allow_html=True)

                        with sc3:
                            if st.button("🗑️ حذف", key=f"do_{order['id']}"):
                                supabase.table("orders").delete().eq("id", order["id"]).execute()
                                st.rerun()
            else:
                st.info("لا توجد طلبات")

        with tab2:
            products = supabase.table("products").select("*").execute().data
            pnames   = [p["name"] for p in products if p["quantity"]>0]
            o_name    = st.text_input("اسم الزبون")
            o_phone   = st.text_input("رقم الهاتف")
            o_city    = st.text_input("المدينة")
            o_address = st.text_area("أقرب نقطة دالة / العنوان")
            o_product = st.selectbox("المنتج", pnames) if pnames else None
            o_qty     = st.number_input("الكمية", min_value=1, step=1)
            o_notes   = st.text_area("ملاحظات")
            sel_prod  = next((p for p in products if p["name"]==o_product), None) if o_product else None
            o_total   = round(sel_prod["selling_price"]*o_qty, 2) if sel_prod else 0
            if sel_prod: st.info(f"💰 الإجمالي: {o_total} د.ل")

            if st.button("✅ تأكيد الطلب"):
                if not o_name or not o_phone: st.error("يرجى إدخال الاسم والهاتف")
                else:
                    supabase.table("orders").insert({
                        "customer_name": o_name, "phone": o_phone, "city": o_city,
                        "address": o_address, "product_name": o_product, "quantity": o_qty,
                        "total_price": o_total, "notes": o_notes, "status": "جديد",
                        "managed_by": current_user, "created_at": str(datetime.now())
                    }).execute()
                    msg = f"🛍️ طلب جديد!\n👤 {o_name}\n📞 {o_phone}\n🏙️ {o_city}\n📍 {o_address}\n🛒 {o_product}\n📦 {o_qty}\n💰 {o_total} د.ل\n📝 {o_notes}"
                    st.success("✅ تم الطلب")
                    st.markdown(f'<a href="{wa_link(s["whatsapp_number"], msg)}" target="_blank"><button style="background:#25D366;color:white;border:none;padding:10px 20px;border-radius:8px;cursor:pointer">📱 إرسال إشعار واتساب</button></a>', unsafe_allow_html=True)

    # =====================================
    # البحث
    # =====================================
    elif choice == "البحث":
        st.header("🔍 البحث في النظام")
        section = st.radio("ابحث في", ["المنتجات","المبيعات","الطلبات","السجل المالي"])
        query   = st.text_input("كلمة البحث")
        if query:
            if section == "المنتجات":
                results = [p for p in supabase.table("products").select("*").execute().data if query.lower() in p["name"].lower()]
                for r in results: st.info(f"📦 {r['name']} | الكمية: {r['quantity']} | السعر: {r['selling_price']} د.ل")
            elif section == "المبيعات":
                results = [t for t in supabase.table("transactions").select("*").execute().data if query.lower() in t["product_name"].lower() or query.lower() in t.get("seller","").lower()]
                for r in results: st.info(f"🛒 {r['product_name']} | {r['quantity']} | ربح: {r['profit']} د.ل | {r['seller']}")
            elif section == "الطلبات":
                results = [o for o in supabase.table("orders").select("*").execute().data if query.lower() in o.get("customer_name","").lower() or query in o.get("phone","") or query.lower() in o.get("city","").lower()]
                for r in results: st.info(f"👤 {r.get('customer_name')} | 📞 {r.get('phone')} | 🛒 {r.get('product_name')} | 📌 {r.get('status')}")
            elif section == "السجل المالي":
                results = [l for l in supabase.table("financial_logs").select("*").execute().data if query.lower() in l.get("action_type","").lower() or query.lower() in l.get("note","").lower()]
                for r in results: st.info(f"🧾 {r['action_type']} | 💰 {r['amount']} د.ل | 👤 {r['user_name']}")
            if not results: st.info("لا توجد نتائج")

    # =====================================
    # سجل العمليات
    # =====================================
    elif choice == "سجل العمليات":
        st.header("📋 سجل العمليات")
        logs = supabase.table("financial_logs").select("*").execute().data
        if logs:
            filt = st.selectbox("فلترة بالمستخدم", ["الكل"]+list(st.session_state["users"].keys()))
            if filt != "الكل": logs = [l for l in logs if l.get("user_name")==filt]
            total_in  = sum(l["amount"] for l in logs if l["action_type"] in ["إضافة","بيع","إتمام طلب","إضافة للمحفظة"])
            total_out = sum(l["amount"] for l in logs if l["action_type"] in ["سحب","سحب من المحفظة","إضافة بضاعة"])
            mc1,mc2,mc3 = st.columns(3)
            with mc1: st.metric("إجمالي العمليات", len(logs))
            with mc2: st.metric("📥 الداخل",  f"{round(total_in,2)} د.ل")
            with mc3: st.metric("📤 الخارج", f"{round(total_out,2)} د.ل")
            st.divider()
            for l in reversed(logs):
                st.info(f"🧾 {l['action_type']} | 💰 {l['amount']} د.ل | 📝 {l['note']} | 👤 {l['user_name']} | 🕒 {l['created_at']}")
        else:
            st.info("لا توجد عمليات")

    # =====================================
    # سجل المبيعات
    # =====================================
    elif choice == "سجل المبيعات":
        st.header("📑 سجل المبيعات")
        sales = supabase.table("transactions").select("*").execute().data
        if sales:
            sm1,sm2 = st.columns(2)
            with sm1: st.success(f"📈 إجمالي الأرباح: {round(sum(s['profit'] for s in sales),2)} د.ل")
            with sm2: st.info(f"💰 إجمالي الإيرادات: {round(sum(s['total'] for s in sales),2)} د.ل")
            for sale in reversed(sales):
                st.info(f"🛒 {sale['product_name']} | الكمية: {sale['quantity']} | الإجمالي: {sale['total']} د.ل | الربح: {sale['profit']} د.ل | {sale['seller']} | 🕒 {sale['created_at']}")
        else:
            st.info("لا توجد مبيعات")

    # =====================================
    # إحصائيات متقدمة
    # =====================================
    elif choice == "إحصائيات متقدمة":
        st.header("📊 إحصائيات متقدمة")
        transactions = supabase.table("transactions").select("*").execute().data
        orders       = supabase.table("orders").select("*").execute().data
        products     = supabase.table("products").select("*").execute().data

        if transactions:
            df = pd.DataFrame(transactions)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["date"] = df["created_at"].dt.date
            sc1,sc2,sc3 = st.columns(3)
            with sc1: st.metric("إجمالي الأرباح",  f"{round(df['profit'].sum(),2)} د.ل")
            with sc2: st.metric("إجمالي المبيعات", f"{round(df['total'].sum(),2)} د.ل")
            with sc3: st.metric("عدد العمليات",    len(df))
            st.subheader("🏆 أفضل المنتجات مبيعاً")
            st.bar_chart(df.groupby("product_name")["quantity"].sum().sort_values(ascending=False))
            st.subheader("📈 الأرباح اليومية")
            st.line_chart(df.groupby("date")["profit"].sum())
            st.subheader("👤 أداء البائعين")
            st.bar_chart(df.groupby("seller")["profit"].sum().sort_values(ascending=False))
        else:
            st.info("لا توجد بيانات مبيعات")
        if orders:
            st.divider(); st.subheader("📦 إحصائيات الطلبات")
            st.bar_chart(pd.DataFrame(orders)["status"].value_counts())
        if products:
            st.divider(); st.subheader("📦 المخزون الحالي")
            st.dataframe(pd.DataFrame(products)[["name","quantity","selling_price"]], use_container_width=True)

    # =====================================
    # تقرير دوري
    # =====================================
    elif choice == "تقرير دوري":
        st.header("📅 تقرير دوري")

        period = st.radio("الفترة", ["اليوم","هذا الأسبوع","هذا الشهر"], horizontal=True)
        now    = datetime.now()

        if period == "اليوم":         start = now.replace(hour=0,minute=0,second=0)
        elif period == "هذا الأسبوع": start = now - timedelta(days=now.weekday())
        else:                          start = now.replace(day=1,hour=0,minute=0,second=0)

        transactions = supabase.table("transactions").select("*").execute().data
        filtered     = [t for t in transactions if str(t.get("created_at","")) >= str(start)]

        if filtered:
            df = pd.DataFrame(filtered)
            total_revenue = round(df["total"].sum(), 2)
            total_capital = round(df["capital"].sum(), 2)
            total_profit  = round(df["profit"].sum(), 2)
            total_qty     = int(df["quantity"].sum())

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("💰 الإيرادات",  f"{total_revenue} د.ل")
            with c2: st.metric("📦 رأس المال", f"{total_capital} د.ل")
            with c3: st.metric("📈 الأرباح",   f"{total_profit} د.ل")
            with c4: st.metric("🛒 الكمية",    total_qty)

            st.divider()
            st.subheader("🏆 أفضل المنتجات في هذه الفترة")
            best = df.groupby("product_name")[["quantity","profit"]].sum().sort_values("profit", ascending=False)
            st.dataframe(best, use_container_width=True)

            # تصدير التقرير
            st.divider()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="التقرير")
            output.seek(0)
            st.download_button(
                label=f"⬇️ تحميل تقرير {period}",
                data=output.getvalue(),
                file_name=f"report_{period}_{now.date()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info(f"لا توجد مبيعات في {period}")

    # =====================================
    # كوبونات الخصم
    # =====================================
    elif choice == "كوبونات الخصم":
        st.header("🎁 كوبونات الخصم")

        tab1, tab2 = st.tabs(["➕ إنشاء كوبون","📋 الكوبونات الحالية"])

        with tab1:
            c_code    = st.text_input("كود الكوبون (مثال: RANIM10)")
            c_type    = st.radio("نوع الخصم", ["نسبة مئوية %","مبلغ ثابت د.ل"])
            c_value   = st.number_input("قيمة الخصم", min_value=0.0)
            c_min     = st.number_input("الحد الأدنى للطلب (0 = بدون حد)", min_value=0.0)
            c_active  = st.toggle("تفعيل الكوبون", value=True)

            if st.button("💾 حفظ الكوبون"):
                try:
                    supabase.table("coupons").insert({
                        "code":       c_code.upper(),
                        "type":       "percent" if "%" in c_type else "fixed",
                        "value":      c_value,
                        "min_order":  c_min,
                        "active":     c_active,
                        "created_at": str(datetime.now())
                    }).execute()
                    st.success(f"✅ تم إنشاء الكوبون: {c_code.upper()}")
                except Exception as e:
                    st.error(f"خطأ: {e}")

        with tab2:
            try:
                coupons = supabase.table("coupons").select("*").execute().data
                if coupons:
                    for cp in coupons:
                        status = "🟢 فعّال" if cp.get("active") else "🔴 معطّل"
                        disc   = f"{cp['value']}%" if cp.get("type")=="percent" else f"{cp['value']} د.ل"
                        c1,c2,c3 = st.columns([3,1,1])
                        with c1: st.write(f"🎁 **{cp['code']}** — خصم {disc} | الحد الأدنى: {cp.get('min_order',0)} د.ل | {status}")
                        with c2:
                            if st.button("تبديل", key=f"tog_{cp['id']}"):
                                supabase.table("coupons").update({"active": not cp.get("active")}).eq("id", cp["id"]).execute()
                                st.rerun()
                        with c3:
                            if st.button("🗑️", key=f"del_cp_{cp['id']}"):
                                supabase.table("coupons").delete().eq("id", cp["id"]).execute()
                                st.rerun()
                else:
                    st.info("لا توجد كوبونات")
            except:
                st.warning("يرجى إنشاء جدول coupons في Supabase أولاً")
                st.code("""CREATE TABLE coupons (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    code text UNIQUE,
    type text,
    value numeric,
    min_order numeric DEFAULT 0,
    active boolean DEFAULT true,
    created_at text
);
GRANT ALL ON coupons TO anon;""")

    # =====================================
    # إدارة المستخدمين
    # =====================================
    elif choice == "إدارة المستخدمين":
        if current_role != "admin": st.error("⛔ ليس لديك صلاحية")
        else:
            st.header("👥 إدارة المستخدمين")

            for user,data in st.session_state["users"].items():
                role = data.get("role","staff") if isinstance(data,dict) else "admin"
                st.info(f"👤 {user} | الدور: {role}")

            st.divider()
            st.subheader("➕ إضافة مستخدم")
            new_user  = st.text_input("اسم المستخدم")
            new_token = st.text_input("الرمز السري")
            new_role  = st.selectbox("الصلاحية", ["admin","staff"])
            if st.button("إضافة"):
                st.session_state["users"][new_user] = {"password": new_token, "role": new_role}
                save_user(new_user, new_token, new_role)
                ensure_wallet(new_user)
                st.success("✅ تم إضافة المستخدم")

            st.divider()
            st.subheader("🔑 تغيير كلمة المرور")
            ch_user  = st.selectbox("المستخدم", list(st.session_state["users"].keys()))
            new_pass = st.text_input("كلمة المرور الجديدة", type="password")
            if st.button("تحديث كلمة المرور"):
                d = st.session_state["users"][ch_user]
                r = d.get("role","staff") if isinstance(d,dict) else "admin"
                st.session_state["users"][ch_user] = {"password": new_pass, "role": r}
                save_user(ch_user, new_pass, r)
                st.success("✅ تم تحديث كلمة المرور")

    # =====================================
    # إعدادات المتجر
    # =====================================
    elif choice == "إعدادات المتجر":
        if current_role != "admin": st.error("⛔ ليس لديك صلاحية")
        else:
            st.header("⚙️ إعدادات المتجر")
            st.caption("كل تغيير هنا يظهر فوراً في متجر الزبائن")

            settings = st.session_state["store_settings"]
            tab1,tab2,tab3,tab4 = st.tabs(["🏪 المعلومات","🎨 الألوان","📦 المنتجات","🔧 متقدمة"])

            with tab1:
                new_name    = st.text_input("اسم المتجر",        value=settings.get("store_name","RANIM"))
                new_welcome = st.text_input("الجملة الترحيبية",  value=settings.get("welcome_message",""))
                new_wa      = st.text_input("رقم واتساب الإدارة (بدون +)", value=settings.get("whatsapp_number",""))
                new_btn     = st.text_input("نص زر السلة",        value=settings.get("btn_text","🛒 أضف للسلة"))
                new_cust_url= st.text_input("رابط متجر الزبائن (للـ QR)", value=settings.get("customer_url","https://your-store.streamlit.app"))

                st.subheader("🖼️ الشعار")
                cur_logo = settings.get("logo_url","")
                if cur_logo: st.image(cur_logo, width=140)
                logo_file = st.file_uploader("رفع شعار جديد", type=["png","jpg","jpeg"])
                new_logo  = cur_logo
                if logo_file:
                    try:
                        fn = f"logo_{uuid.uuid4()}.png"
                        supabase.storage.from_("products").upload(fn, logo_file.getvalue())
                        new_logo = f"{SUPABASE_URL}/storage/v1/object/public/products/{fn}"
                        st.image(new_logo, width=140); st.success("✅ تم رفع الشعار")
                    except Exception as e: st.error(f"خطأ: {e}")

                if st.button("💾 حفظ المعلومات"):
                    settings.update({"store_name":new_name,"welcome_message":new_welcome,"whatsapp_number":new_wa,"logo_url":new_logo,"btn_text":new_btn,"customer_url":new_cust_url})
                    st.session_state["store_settings"] = settings
                    save_settings(settings)
                    st.success("✅ تم الحفظ"); st.rerun()

            with tab2:
                ca,cb = st.columns(2)
                with ca:
                    np = st.color_picker("اللون الرئيسي", value=settings.get("color_primary","#c9848a"))
                    nb = st.color_picker("لون الخلفية",   value=settings.get("color_bg","#f9eced"))
                with cb:
                    na = st.color_picker("لون التمييز",   value=settings.get("color_accent","#c9a96e"))
                    nt = st.color_picker("لون النصوص",    value=settings.get("color_text","#4a2c2e"))

                st.markdown(f"""
                <div style="background:{nb};padding:20px;border-radius:12px;text-align:center;margin-top:16px">
                    <div style="color:{nt};font-size:1.4rem;font-weight:700">{settings.get('store_name','RANIM')}</div>
                    <div style="color:{np};margin:8px 0">{settings.get('welcome_message','')}</div>
                    <span style="background:{np};color:white;padding:8px 20px;border-radius:10px">{settings.get('btn_text','🛒 أضف للسلة')}</span>
                    <span style="color:{na};font-weight:700;margin-right:12px">150 د.ل</span>
                </div>""", unsafe_allow_html=True)

                if st.button("💾 حفظ الألوان"):
                    settings.update({"color_primary":np,"color_accent":na,"color_bg":nb,"color_text":nt})
                    st.session_state["store_settings"] = settings
                    save_settings(settings)
                    st.success("✅ تم"); st.rerun()

            with tab3:
                prods_all = supabase.table("products").select("*").execute().data
                if prods_all:
                    for product in prods_all:
                        p1,p2,p3 = st.columns([3,1,1])
                        with p1: st.write(f"📦 **{product['name']}** | {product['quantity']} | {product['selling_price']} د.ل")
                        with p2:
                            vis = product.get("visible", True)
                            st.write("🟢 ظاهر" if vis else "🔴 مخفي")
                        with p3:
                            if st.button("إخفاء" if vis else "إظهار", key=f"vis_{product['id']}"):
                                supabase.table("products").update({"visible": not vis}).eq("id", product["id"]).execute()
                                st.rerun()

            with tab4:
                maintenance    = st.toggle("🚧 وضع الصيانة", value=settings.get("maintenance_mode",False))
                maintenance_msg= st.text_input("رسالة الصيانة", value=settings.get("maintenance_msg","المتجر تحت الصيانة 🌸"))
                custom_banner  = st.text_area("نص البانر الترحيبي", value=settings.get("custom_banner",""))

                st.divider()
                st.subheader("🔗 روابط المنظومتين")
                st.code(f"{settings.get('customer_url','https://your-store.streamlit.app')}  ← متجر الزبائن")

                if st.button("💾 حفظ الإعدادات المتقدمة"):
                    settings.update({"maintenance_mode":maintenance,"maintenance_msg":maintenance_msg,"custom_banner":custom_banner})
                    st.session_state["store_settings"] = settings
                    save_settings(settings)
                    st.success("✅ تم"); st.rerun()

    # =====================================
    # تصدير البيانات
    # =====================================
    elif choice == "تصدير البيانات":
        if current_role != "admin": st.error("⛔ ليس لديك صلاحية")
        else:
            st.header("📤 تصدير البيانات")
            export_choice = st.selectbox("اختر البيانات", ["المنتجات","المبيعات","الطلبات","السجل المالي"])
            table_map = {"المنتجات":"products","المبيعات":"transactions","الطلبات":"orders","السجل المالي":"financial_logs"}
            if st.button("📥 تحميل Excel"):
                data = supabase.table(table_map[export_choice]).select("*").execute().data
                if data:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        pd.DataFrame(data).to_excel(writer, index=False, sheet_name=export_choice)
                    output.seek(0)
                    st.download_button(label=f"⬇️ تحميل {export_choice}.xlsx", data=output.getvalue(),
                        file_name=f"{export_choice}_{datetime.now().date()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else: st.info("لا توجد بيانات")

    # =====================================
    # نسخ احتياطي
    # =====================================
    elif choice == "نسخ احتياطي":
        if current_role != "admin": st.error("⛔ ليس لديك صلاحية")
        else:
            st.header("💾 نسخ احتياطي")
            if st.button("📦 تحميل نسخة احتياطية كاملة"):
                tables = {"المنتجات":"products","المبيعات":"transactions","الطلبات":"orders","السجل المالي":"financial_logs","المحافظ":"wallets","رأس المال":"capital_accounts"}
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    for sn, tn in tables.items():
                        try:
                            data = supabase.table(tn).select("*").execute().data
                            if data: pd.DataFrame(data).to_excel(writer, index=False, sheet_name=sn)
                        except: pass
                output.seek(0)
                st.download_button(label="⬇️ تحميل النسخة الاحتياطية", data=output.getvalue(),
                    file_name=f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.success("✅ جاهز!")