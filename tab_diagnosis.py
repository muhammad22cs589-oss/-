import streamlit as st
from PIL import Image
from ai_engine import diagnose_plant_disease
from utils import centered_button


def render_diagnosis_tab():
    st.subheader("🔍 تشخيص أمراض النبات الفوري")
    up = st.file_uploader("ارفع صورة لورقة النبات المصابة", type=["jpg", "png", "jpeg"])

    if up:
        img = Image.open(up)
        st.image(img, use_container_width=True, caption="الصورة المرفوعة")

        if centered_button("بدء الفحص التشخيصي الذكي (بواسطة Gemini)", key="btn_diag"):
            with st.spinner("جاري التحليل بالذكاء الاصطناعي..."):
                res_disease = diagnose_plant_disease(img)
                if res_disease.startswith("❌") or res_disease.startswith("⚠️"):
                    st.error(res_disease)
                else:
                    st.success(res_disease)