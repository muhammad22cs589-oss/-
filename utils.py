import streamlit as st

def centered_button(button_text, key=None):
    """دالة مساعدة لإنشاء زر موسط في منتصف الشاشة بدلاً من تكرار الكود"""
    _, col, _ = st.columns([1, 2, 1])
    with col:
        return st.button(button_text, use_container_width=True, key=key)