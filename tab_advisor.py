import streamlit as st
from ai_engine import agri_chat
from utils import centered_button


def render_advisor_tab():
    st.subheader("🤖 المستشار الزراعي الشامل")
    q = st.text_input("اسأل أي سؤال حول الزراعة في العراق:")

    if centered_button("إرسال الاستفسار", key="btn_adv"):
        if q:
            with st.spinner("جاري صياغة الإجابة..."):
                res_chat = agri_chat(q)
                if res_chat.startswith("❌") or res_chat.startswith("⚠️"):
                    st.error(res_chat)
                else:
                    st.write(res_chat)
        else:
            st.warning("يرجى كتابة السؤال أولاً.")