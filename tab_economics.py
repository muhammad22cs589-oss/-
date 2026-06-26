import streamlit as st
from ai_engine import calculate_economics
from utils import centered_button


def render_economics_tab():
    st.subheader("💰 دراسة الجدوى الاقتصادية")
    cost_dunum = st.number_input("تكلفة الدونم الواحد الافتراضية (بالدينار العراقي)", value=200000, key="eco_cost")
    price_ton = st.number_input("سعر بيع الطن الواحد المتوقع (بالدينار العراقي)", value=500000, key="eco_price")

    prod_data = st.session_state.cached_production
    st.markdown("<br>", unsafe_allow_html=True)

    if centered_button("تشغيل التحليل المالي والمحاكاة التقديرية", key="eco_btn"):
        profit, status = calculate_economics(prod_data['area'], prod_data['yield'], cost_dunum, price_ton)
        st.metric("الصافي التقديري المتوقع", f"{profit:,} دينار عراقي", delta=status,
                  delta_color="normal" if profit >= 0 else "inverse")