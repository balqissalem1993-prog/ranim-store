# =========================================
# Ranim Jewelry - Customer Store
# =========================================

import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="Ranim Jewelry 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SUPABASE_URL = "https://xwwlffppepiwdiekqylr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3d2xmZnBwZXBpd2RpZWtxeWxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2NDcxMjksImV4cCI6MjA5NTIyMzEyOX0.bpWm7U4Z9JybPrEBPWmHhTRGZsq2CaaI7AVnuWKTZNg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================
# جلب البيانات
# =========================================
def get_settings():
    try:
        rows = supabase.table("store_settings").select("*").execute().data
        if rows: return rows[0]
    except: pass
    return {
        "store_name":        "RANIM",
        "welcome_message":   "مجوهرات فاخرة تليق بك",
        "whatsapp_number":   "218910000000",
        "logo_url":          "",
        "btn_text":          "🛒 أضف للسلة",
        "color_primary":     "#c9848a",
        "color_accent":      "#c9a96e",
        "color_bg":          "#f9eced",
        "color_text":        "#4a2c2e",
        "maintenance_mode":  False,
        "maintenance_msg":   "المتجر تحت الصيانة، نعود قريباً 🌸",
        "custom_banner":     ""
    }

def get_products():
    try: return supabase.table("products").select("*").execute().data
    except: return []

settings = get_settings()

# ── وضع الصيانة ──
if settings.get("maintenance_mode", False):
    st.markdown(f"""
    <div style="min-height:100vh;background:#f9eced;display:flex;
                align-items:center;justify-content:center;text-align:center;padding:40px">
        <div>
            <div style="font-size:4rem">🌸</div>
            <div style="font-family:serif;font-size:2rem;color:#4a2c2e;margin:16px 0">
                {settings.get('store_name','RANIM')}
            </div>
            <div style="font-size:1.1rem;color:#c9848a">
                {settings.get('maintenance_msg','المتجر تحت الصيانة، نعود قريباً 🌸')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

products  = get_products()
# إظهار فقط المنتجات المتاحة وغير المخفية
available = [p for p in products if p.get("quantity",0) > 0 and p.get("visible", True) is not False]

# ── الألوان من الإعدادات ──
C_PRIMARY = settings.get("color_primary", "#c9848a")
C_ACCENT  = settings.get("color_accent",  "#c9a96e")
C_BG      = settings.get("color_bg",      "#f9eced")
C_TEXT    = settings.get("color_text",    "#4a2c2e")
BTN_TEXT  = settings.get("btn_text",      "🛒 أضف للسلة")
store_name  = settings.get("store_name",  "RANIM").upper()
welcome_msg = settings.get("welcome_message", "مجوهرات فاخرة تليق بك")
logo_url    = settings.get("logo_url",    "")
wa_number   = settings.get("whatsapp_number", "218910000000")
custom_banner = settings.get("custom_banner", "")

# =========================================
# CSS ديناميكي
# =========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Tajawal:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif !important; }}

#MainMenu, footer, header,
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {{ display: none !important; }}

.block-container {{ padding: 0 !important; max-width: 100% !important; }}

.stTextInput input, .stTextArea textarea {{
    border: 1.5px solid {C_PRIMARY} !important;
    border-radius: 10px !important;
    font-family: 'Tajawal', sans-serif !important;
}}
div.stButton > button {{
    background: linear-gradient(135deg, {C_PRIMARY}, {C_ACCENT}) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    font-family: 'Tajawal', sans-serif !important;
    width: 100% !important;
    height: 48px !important;
    letter-spacing: 1px !important;
}}
div.stButton > button:hover {{ opacity: 0.88 !important; }}
</style>
""", unsafe_allow_html=True)

# =========================================
# Session State
# =========================================
if "cart"          not in st.session_state: st.session_state["cart"]          = {}
if "order_done"    not in st.session_state: st.session_state["order_done"]    = False
if "show_checkout" not in st.session_state: st.session_state["show_checkout"] = False
if "wa_url"        not in st.session_state: st.session_state["wa_url"]        = ""

cart        = st.session_state["cart"]
total_items = sum(v["qty"] for v in cart.values())
total_price = sum(v["price"]*v["qty"] for v in cart.values())

# =========================================
# HERO
# =========================================
st.markdown(f"""
<div style="background:linear-gradient(145deg,{C_BG} 0%,{C_PRIMARY}33 60%,{C_BG} 100%);
            padding:50px 20px 30px;text-align:center;">
""", unsafe_allow_html=True)

if logo_url:
    c1,c2,c3 = st.columns([2,1,2])
    with c2: st.image(logo_url, width=140)
else:
    st.markdown("<div style='font-size:4rem;text-align:center'>🌸</div>", unsafe_allow_html=True)

st.markdown(f"""
    <div style="font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:700;
                color:{C_TEXT};letter-spacing:5px;text-align:center;margin:16px 0 8px;">
        {store_name}
    </div>
    <div style="font-size:1.05rem;color:{C_PRIMARY};letter-spacing:2px;
                text-align:center;margin-bottom:16px;">
        {welcome_msg}
    </div>
    <div style="width:80px;height:2px;
                background:linear-gradient(90deg,transparent,{C_ACCENT},transparent);
                margin:0 auto 10px;"></div>
</div>
""", unsafe_allow_html=True)

# ── بانر مخصص ──
if custom_banner:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C_PRIMARY},{C_ACCENT});
                color:white;text-align:center;padding:12px 20px;
                font-size:1rem;font-weight:600;letter-spacing:1px;">
        {custom_banner}
    </div>
    """, unsafe_allow_html=True)

# =========================================
# شريط السلة
# =========================================
st.markdown(f"""
<div style="background:{C_TEXT};color:white;padding:12px 40px;
            display:flex;justify-content:space-between;align-items:center;">
    <span style="opacity:0.8;letter-spacing:1px">🛍️ سلة التسوق</span>
    <span style="background:{C_PRIMARY};color:white;border-radius:20px;
                 padding:4px 16px;font-weight:700;">
        {total_items} منتج &nbsp;—&nbsp; {round(total_price,2)} د.ل
    </span>
</div>
""", unsafe_allow_html=True)

# =========================================
# المنتجات
# =========================================
if not st.session_state["order_done"]:

    st.markdown(f"""
    <div style="text-align:center;padding:36px 20px 8px;">
        <span style="font-family:'Playfair Display',serif;font-size:1.6rem;
                     color:{C_TEXT};letter-spacing:2px;">✨ مجموعتنا</span>
    </div>
    <div style="width:60px;height:2px;background:{C_ACCENT};margin:0 auto 28px;"></div>
    """, unsafe_allow_html=True)

    if not available:
        st.markdown(f"<p style='text-align:center;color:{C_PRIMARY};padding:40px'>لا توجد منتجات متاحة حالياً</p>", unsafe_allow_html=True)
    else:
        cols = st.columns(3, gap="large")
        for i, product in enumerate(available):
            with cols[i % 3]:
                pid       = str(product["id"])
                name      = product["name"]
                price     = product["selling_price"]
                stock     = product["quantity"]
                max_q     = int(product.get("max_order_qty") or stock)
                img       = product.get("image_url","")
                in_cart   = cart.get(pid,{}).get("qty",0)
                remaining = max_q - in_cart

                if img:
                    st.markdown(f"""
                    <div style="border-radius:20px;overflow:hidden;
                                box-shadow:0 4px 20px {C_PRIMARY}44;
                                border:1px solid {C_PRIMARY}44;
                                background:white;margin-bottom:8px;">
                        <img src="{img}" style="width:100%;height:220px;object-fit:cover;display:block;"/>
                        <div style="padding:16px 18px 6px;">
                            <div style="font-family:'Playfair Display',serif;font-size:1rem;
                                        color:{C_TEXT};font-weight:600;margin-bottom:4px;">{name}</div>
                            <div style="color:{C_ACCENT};font-weight:700;font-size:1.05rem;">{price} د.ل</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="border-radius:20px;overflow:hidden;
                                box-shadow:0 4px 20px {C_PRIMARY}44;
                                border:1px solid {C_PRIMARY}44;
                                background:white;margin-bottom:8px;">
                        <div style="height:220px;background:linear-gradient(135deg,{C_BG},{C_ACCENT}33);
                                    display:flex;align-items:center;justify-content:center;font-size:3.5rem;">🌸</div>
                        <div style="padding:16px 18px 6px;">
                            <div style="font-family:'Playfair Display',serif;font-size:1rem;
                                        color:{C_TEXT};font-weight:600;margin-bottom:4px;">{name}</div>
                            <div style="color:{C_ACCENT};font-weight:700;font-size:1.05rem;">{price} د.ل</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                c_qty, c_btn = st.columns([1,2])
                with c_qty:
                    qty_val = st.number_input(" ", min_value=1, max_value=max(1,remaining),
                                              value=1, step=1, key=f"qty_{pid}", label_visibility="collapsed")
                with c_btn:
                    if remaining > 0:
                        if st.button(BTN_TEXT, key=f"add_{pid}"):
                            if pid in st.session_state["cart"]:
                                st.session_state["cart"][pid]["qty"] += qty_val
                            else:
                                st.session_state["cart"][pid] = {"name":name,"price":price,"qty":qty_val,"max":max_q}
                            st.rerun()
                    else:
                        st.markdown(f"<small style='color:{C_PRIMARY}'>وصلت للحد الأقصى</small>", unsafe_allow_html=True)

                st.markdown("<br/>", unsafe_allow_html=True)

    # ── السلة ──
    if cart:
        st.markdown(f"<hr style='border-color:{C_PRIMARY}44;margin:10px 0'/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 8px;">
            <span style="font-family:'Playfair Display',serif;font-size:1.4rem;color:{C_TEXT};">🛍️ سلتك</span>
        </div>
        <div style="width:50px;height:2px;background:{C_ACCENT};margin:0 auto 20px;"></div>
        """, unsafe_allow_html=True)

        _,col_c,_ = st.columns([1,3,1])
        with col_c:
            st.markdown(f"<div style='background:{C_BG};border-radius:20px;padding:24px;border:1px solid {C_PRIMARY}44'>", unsafe_allow_html=True)
            for pid, item in list(cart.items()):
                item_total = round(item["price"]*item["qty"],2)
                r1,r2,r3 = st.columns([3,1,1])
                with r1: st.markdown(f"**{item['name']}** × {item['qty']}")
                with r2: st.markdown(f"<span style='color:{C_ACCENT};font-weight:700'>{item_total} د.ل</span>", unsafe_allow_html=True)
                with r3:
                    if st.button("✕", key=f"rm_{pid}"):
                        del st.session_state["cart"][pid]
                        st.rerun()

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{C_TEXT},{C_PRIMARY});color:white;
                        border-radius:14px;padding:16px 22px;display:flex;
                        justify-content:space-between;font-size:1.1rem;font-weight:700;margin-top:16px;">
                <span>الإجمالي</span><span>{round(total_price,2)} د.ل</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div><br/>", unsafe_allow_html=True)

            if st.button("✅ إتمام الطلب"):
                st.session_state["show_checkout"] = True
                st.rerun()

    # ── نموذج الطلب ──
    if st.session_state["show_checkout"] and cart:
        st.markdown(f"<hr style='border-color:{C_PRIMARY}44'/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 8px;">
            <span style="font-family:'Playfair Display',serif;font-size:1.4rem;color:{C_TEXT};">📋 بيانات التوصيل</span>
        </div>
        <div style="width:50px;height:2px;background:{C_ACCENT};margin:0 auto 20px;"></div>
        """, unsafe_allow_html=True)

        _,col_f,_ = st.columns([1,3,1])
        with col_f:
            st.markdown(f"<div style='background:white;border-radius:20px;padding:30px;box-shadow:0 4px 24px {C_PRIMARY}33;border:1px solid {C_PRIMARY}33;margin-bottom:20px;'>", unsafe_allow_html=True)
            c_name    = st.text_input("👤 الاسم الكامل")
            c_phone   = st.text_input("📞 رقم الهاتف")
            c_city    = st.text_input("🏙️ المدينة")
            c_address = st.text_area("📍 أقرب نقطة دالة / العنوان التفصيلي", height=100)
            c_notes   = st.text_area("📝 ملاحظات إضافية (اختياري)", height=70)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🌸 تأكيد الطلب الآن"):
                if not c_name or not c_phone or not c_city or not c_address:
                    st.error("يرجى ملء جميع الحقول المطلوبة")
                else:
                    items_summary = "\n".join([
                        f"• {v['name']} × {v['qty']} = {round(v['price']*v['qty'],2)} د.ل"
                        for v in cart.values()
                    ])
                    order_success = True
                    for pid, item in cart.items():
                        try:
                            res = supabase.table("orders").insert({
                                "customer_name": c_name,
                                "phone":         c_phone,
                                "city":          c_city,
                                "address":       c_address,
                                "product_name":  item["name"],
                                "quantity":      item["qty"],
                                "total_price":   round(item["price"]*item["qty"],2),
                                "notes":         c_notes,
                                "status":        "جديد",
                                "managed_by":    "customer",
                                "created_at":    str(datetime.now())
                            }).execute()
                        except Exception:
                            pass

                    wa_msg = (
                        f"🌸 طلب جديد - {store_name}\n"
                        f"{'─'*28}\n"
                        f"👤 الاسم: {c_name}\n"
                        f"📞 الهاتف: {c_phone}\n"
                        f"🏙️ المدينة: {c_city}\n"
                        f"📍 العنوان: {c_address}\n"
                        f"{'─'*28}\n"
                        f"🛒 المنتجات:\n{items_summary}\n"
                        f"{'─'*28}\n"
                        f"💰 الإجمالي: {round(total_price,2)} د.ل\n"
                        f"📝 ملاحظات: {c_notes or 'لا يوجد'}"
                    )
                    encoded = wa_msg.replace("\n","%0A").replace(" ","%20")
                    st.session_state["cart"]          = {}
                    st.session_state["show_checkout"] = False
                    st.session_state["order_done"]    = True
                    st.session_state["wa_url"]        = f"https://wa.me/{wa_number}?text={encoded}"
                    st.rerun()

# =========================================
# شاشة النجاح
# =========================================
if st.session_state["order_done"]:
    _,col_s,_ = st.columns([1,3,1])
    with col_s:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{C_BG},{C_PRIMARY}44);
                    border:2px solid {C_ACCENT};border-radius:20px;
                    padding:50px 40px;text-align:center;margin:30px 0;">
            <div style="font-size:3.5rem;margin-bottom:16px;">🌸</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.6rem;
                        color:{C_TEXT};margin-bottom:10px;">تم استلام طلبك بنجاح!</div>
            <div style="color:{C_PRIMARY};font-size:1rem;">سنتواصل معك قريباً لتأكيد التوصيل</div>
        </div>
        """, unsafe_allow_html=True)

        wa_url = st.session_state.get("wa_url","")
        if wa_url:
            st.markdown(
                f'<a href="{wa_url}" target="_blank">'
                f'<button style="background:#25D366;color:white;border:none;padding:14px;'
                f'border-radius:14px;font-size:1rem;font-weight:700;cursor:pointer;'
                f'width:100%;font-family:Tajawal,sans-serif;margin-bottom:12px;display:block">'
                f'📱 إرسال الطلب عبر واتساب</button></a>',
                unsafe_allow_html=True
            )
        if st.button("🛍️ العودة للتسوق"):
            st.session_state["order_done"] = False
            st.session_state["wa_url"]     = ""
            st.rerun()

# =========================================
# Footer
# =========================================
st.markdown(f"""
<div style="background:{C_TEXT};color:rgba(255,255,255,0.55);
            text-align:center;padding:22px;font-size:0.85rem;
            letter-spacing:1px;margin-top:40px;">
    🌸 {store_name} &nbsp;—&nbsp; جميع الحقوق محفوظة
</div>
""", unsafe_allow_html=True)