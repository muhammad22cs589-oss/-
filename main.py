import streamlit as st

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            ._viewerBadge_1qs0b_1 {display: none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

import pandas as pd
import os

# 1. استدعاء ملفات التبويبات
from tab_production import render_production_tab
from tab_diagnosis import render_diagnosis_tab
from tab_advisor import render_advisor_tab
from tab_history import render_history_tab
from tab_economics import render_economics_tab
from about import show_about_page
from tab_admin import render_admin_tab

# 2. إعداد الصفحة
st.set_page_config(page_title="نظام الزراعة الذكية المستدامة في العراق", layout="centered")

# 3. قراءة الـ CSS من الملف الخارجي
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 4. إعداد الجلسة وقائمة الأعمدة (مطابقة للملف الأصلي تماماً)
DB_FILE = "session_data.csv"
COLUMNS_ORDER = [
    "تاريخ",
    "محافظة",
    "محصول",
    "مساحة (دونم)",
    "تربة",
    "ري",
    "نوع السماد",
    "السماد (كغم/دونم)",
    "مطر",
    "حرارة",
    "رطوبة",
    "انتاج",
    "دقة"
]

if 'history_list' not in st.session_state:
    st.session_state.history_list = []
    if os.path.exists(DB_FILE):
        try:
            st.session_state.history_list = pd.read_csv(DB_FILE).reindex(columns=COLUMNS_ORDER).dropna(
                subset=["محافظة"]).to_dict('records')
        except:
            pass

if 'cached_production' not in st.session_state:
    st.session_state.cached_production = {"area": 100.0, "yield": 131.64, "crop": "حنطة", "city": "الموصل"}

if 'latest_scan_results' not in st.session_state:
    st.session_state.latest_scan_results = None

# 5. العنوان الرئيسي للمشروع
st.title("🌿 نظام الزراعة الذكية المستدامة في العراق")
st.markdown("---")

# 6. شريط التبويبات الرئيسي (يحتوي على الواجهات الأساسية + تبويب الإدارة الشامل)
tabs = st.tabs([
    "📊 الإنتاج والطقس",
    "🔍 تشخيص الأمراض",
    "🤖 المستشار الذكي",
    "📋 سجل العمليات",
    "💰 المستشار الاقتصادي",
    "⚙️ المزيد"  # التبويب الرئيسي للإدارة وحول التطبيق
])

# 7. توزيع المحتوى على التبويبات الـ 5 الأساسية للمزارع
with tabs[0]: render_production_tab(DB_FILE)
with tabs[1]: render_diagnosis_tab()
with tabs[2]: render_advisor_tab()
with tabs[3]: render_history_tab(DB_FILE, COLUMNS_ORDER)
with tabs[4]: render_economics_tab()

# 8. التبويب السادس والأخير: يحتوي بداخله على قوائم فرعية تماماً مثل القائمة الأساسية!
with tabs[5]:
    st.markdown("<br>", unsafe_allow_html=True)

    # 💡 هنا الفكرة الذكية: إنشاء شريط قوائم (تبويبات) فرعي أنيق ومرتب
    admin_sub_tabs = st.tabs([
        "⚙️ لوحة إدارة الملفات (MLOps)",
        "ℹ️ حول التطبيق وفريق العمل"
    ])

    # القائمة الفرعية الأولى: لوحة الإدارة
    with admin_sub_tabs[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        render_admin_tab()

    # القائمة الفرعية الثانية: حول التطبيق
    with admin_sub_tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        show_about_page()
