import streamlit as st
import pandas as pd
import os
from utils import centered_button


def render_history_tab(DB_FILE, COLUMNS_ORDER):
    st.subheader("📋 سجل العمليات والتقارير الزمني")
    if st.session_state.history_list:
        st.table(pd.DataFrame(st.session_state.history_list).reindex(columns=COLUMNS_ORDER))
        st.markdown("<br>", unsafe_allow_html=True)

        if centered_button("🗑 مسح السجل نهائياً", key="btn_clear"):
            st.session_state.history_list = []
            st.session_state.latest_scan_results = None
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    else:
        st.warning("السجل فارغ حالياً.")