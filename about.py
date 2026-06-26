import streamlit as st


def show_about_page():
    # تنسيق CSS مخصص ومحلي لضمان التوسيط الكامل ومنع أي تداخل أو تغبيش في هذه الصفحة
    st.markdown("""
        <style>
            .about-container {
                text-align: center !important;
                font-family: 'Cairo', sans-serif !important;
                direction: rtl !important;
            }
            .center-text {
                text-align: center !important;
                display: block !important;
                width: 100% !important;
            }
            .team-card {
                text-align: center !important;
                padding: 20px; 
                background-color: #ffffff; 
                border: 1px solid #e0e0e0; 
                border-radius: 16px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.03);
                transition: transform 0.3s ease;
            }
            .team-card:hover {
                transform: translateY(-5px);
            }
            .contact-card {
                text-align: center !important;
                padding: 22px; 
                border-radius: 14px; 
                height: 100%;
                box-shadow: 0 4px 10px rgba(0,0,0,0.02);
            }
            /* 🎯 الفلتر السحري لتوسيط بيانات الاتصال الأجنبية وجعل قراءتها من اليسار إلى اليمين */
            .ltr-contact {
                direction: ltr !important;
                text-align: center !important;
                display: block !important;
                font-weight: 700 !important;
                margin: 10px 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # عنوان الصفحة موسط تماماً مع لون زراعي راقٍ
    st.markdown(
        "<h2 style='text-align: center; color: #2E7D32; font-weight: 700; margin-bottom: 20px;'>عن تطبيق الزراعة الذكية العراقية</h2>",
        unsafe_allow_html=True)

    # الوصف العام للتطبيق
    st.markdown("""
        <div class='center-text'>
            <p style='text-align: center; font-size: 17px; color: #555555; line-height: 1.8; max-width: 800px; margin: 0 auto;'>
            هذا النظام تم تصميمه وبرمجته ليكون المساعد الرقمي الأول للفلاح العراقي. 
            نحن ندمج خوارزميات الذكاء الاصطناعي مع البيانات المناخية اللحظية لتقديم 
            تنبؤات بالإنتاج، تشخيص للأمراض، ودراسات جدوى تساهم في تحقيق الأمن الغذائي وتقليل الخسائر.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # لوحة الإشراف والتطوير
    st.markdown("""
        <div style='text-align: center; background-color: #F1F8E9; padding: 18px; border-radius: 12px; margin: 0 auto 35px auto; border: 1px solid #DCEDC8; max-width: 600px;'>
            <h3 style='color: #2E7D32; margin: 0; font-size: 20px; font-weight: 600;'>✨ تم التطوير بواسطة: فريق التنمية ✨</h3>
            <h4 style='color: #558B2F; margin: 8px 0 0 0; font-size: 16px; font-weight: 500;'>بإشراف: د. ياسر علي</h4>
        </div>
    """, unsafe_allow_html=True)

    # 🔺 الهيكل الهرمي المنظم للفريق 🔺

    # الصف الأول: رأس الهرم (قائد الفريق)
    _, leader_col, _ = st.columns([1, 1.8, 1])
    with leader_col:
        st.markdown("""
            <div class='team-card' style='border: 2px solid #2E7D32; background-color: #F9FBF7;'>
                <div style='font-size: 28px; margin-bottom: 5px;'>👑</div>
                <b style='font-size: 15px; color: #555555; display: block; margin-bottom: 4px;'>قائد الفريق</b>
                <span style='color: #1B5E20; font-size: 20px; font-weight: 700;'>محمد عبدالملك رجب</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # الصف الثاني: قاعدة الهرم (يمين شيماء، ويسار طيبة)
    cols = st.columns(2)

    with cols[1]:  # الجانب الأيمن (المصممة)
        st.markdown("""
            <div class='team-card'>
                <div style='font-size: 26px; margin-bottom: 5px;'>🎨</div>
                <b style='font-size: 14px; color: #777777; display: block; margin-bottom: 4px;'>المصممة</b>
                <span style='color: #2E7D32; font-size: 18px; font-weight: 700;'>شيماء مهيدي</span>
            </div>
        """, unsafe_allow_html=True)

    with cols[0]:  # الجانب الأيسر (المبرمجة)
        st.markdown("""
            <div class='team-card'>
                <div style='font-size: 26px; margin-bottom: 5px;'>💻</div>
                <b style='font-size: 14px; color: #777777; display: block; margin-bottom: 4px;'>المبرمجة</b>
                <span style='color: #2E7D32; font-size: 18px; font-weight: 700;'>طيبة خالد</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><hr style='border: 0; border-top: 1px solid #e0e0e0;'><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #333333; font-weight: 600;'>📞 قنوات التواصل الرسمية</h3><br>",
                unsafe_allow_html=True)

    # بطاقات الاتصال المعدلة بالتوجيه الأجنبي الموسط
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
            <div class='contact-card' style='background-color: #E8F5E9; border: 1px solid #C8E6C9;'>
                <h4 style='color: #2E7D32; margin-top: 0; font-weight: 600;'>📱 واتساب</h4>
                <p class='ltr-contact' style='font-size: 17px; color: #1B5E20;'>+964 773 904 3271</p>
                <a href="https://wa.me/9647739043271" target="_blank" style="text-decoration: none; background-color: #2E7D32; color: white; padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 5px; box-shadow: 0 2px 5px rgba(46,125,50,0.2);">تواصل معنا</a>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div class='contact-card' style='background-color: #E3F2FD; border: 1px solid #BBDEFB;'>
                <h4 style='color: #1565C0; margin-top: 0; font-weight: 600;'>✈️ تيليجرام</h4>
                <p class='ltr-contact' style='font-size: 17px; color: #0D47A1;'>@ictfmohamd</p>
                <a href="https://t.me/ictfmohamd" target="_blank" style="text-decoration: none; background-color: #1565C0; color: white; padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 5px; box-shadow: 0 2px 5px rgba(21,101,192,0.2);">راسلنا الحين</a>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
            <div class='contact-card' style='background-color: #FFF3E0; border: 1px solid #FFE0B2;'>
                <h4 style='color: #E65100; margin-top: 0; font-weight: 600;'>✉️ Email</h4>
                <p class='ltr-contact' style='font-size: 14px; color: #E65100; word-break: break-all;'>ictf.mohamd@gmail.com</p>
                <a href="mailto:ictf.mohamd@gmail.com" style="text-decoration: none; background-color: #E65100; color: white; padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; margin-top: 5px; box-shadow: 0 2px 5px rgba(230,81,0,0.2);">مراسلة بريدية</a>
            </div>
        """, unsafe_allow_html=True)