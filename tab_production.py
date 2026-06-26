import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from weather_service import get_weather_data
from calculator import calculate_production
from ai_engine import get_smart_alerts, get_personalized_advice
from utils import centered_button


def render_production_tab(DB_FILE):
    st.subheader("📥 مدخلات البيانات الشاملة والمتطورة للمزرعة")

    # تقسيم المدخلات على عمودين متناسقين لجمالية الواجهة
    col1, col2 = st.columns(2)

    with col1:
        city = st.selectbox("المحافظة",
                            ["بغداد", "الموصل", "البصرة", "بابل", "واسط", "النجف", "كربلاء", "ديالى", "الأنبار",
                             "ميسان"])
        crop = st.selectbox("نوع المحصول", ["حنطة", "شعير", "ذرة", "خضراوات", "فواكه", "تمور", "رز"])
        area = st.number_input("المساحة الإجمالية (بالدونم)", min_value=1.0, value=50.0)
        soil = st.selectbox("نوع تربة الحقل", ["طينية", "رملية", "مختلطة"])

    with col2:
        irrigation = st.selectbox("طريقة الري المستخدمة", ["سيحي/غمر", "رش محوري", "تنقيط"])
        seeds = st.selectbox("نوعية جودة البذور", ["محسنة", "عادية"])

        # --- تقسيم موضع السماد إلى نصفين للنوع والكمية ---
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fertilizer_type = st.selectbox("نوع السماد", ["يوريا (N)", "داب (DAP)", "مركب (NPK)", "عضوي"])
        with f_col2:
            fertilizer = st.number_input("الكمية (كغم/دونم)", min_value=0.0, value=50.0)

        # --- 🧠 الميزة الأولى: منطق الحسبة التلقائية المبدئية ---
        base_water_needs = {"رز": 35, "خضراوات": 20, "ذرة": 15, "فواكه": 15, "حنطة": 12, "شعير": 12, "تمور": 10}
        soil_factors = {"رملية": 1.2, "طينية": 0.85, "مختلطة": 1.0}

        crop_base = base_water_needs.get(crop, 15)
        soil_fact = soil_factors.get(soil, 1.0)
        # حسبة تقديرية حية بناءً على المدخلات الحالية
        approx_total_water = round(crop_base * soil_fact * area, 1)

        # عرض النص الإرشادي بمظهر مريح ومتناسق هندسياً في الواجهة
        st.markdown(f"""
            <div style='text-align: right; margin-top: 12px; padding-right: 5px;'>
                <span style='color: #1565C0; font-weight: bold;'>💧 الاحتياج المائي القياسي المقدر لأرضك:</span><br>
                <span style='color: #2E7D32; font-weight: bold; background-color: #E8F5E9; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-top: 5px;'>{approx_total_water} م³ يومياً</span>
            </div>
        """, unsafe_allow_html=True)

    if centered_button("تحليل وحساب الإنتاج بالذكاء الاصطناعي", key="btn_prod"):
        w_data = get_weather_data(city)
        if w_data["status"] == "success":
            # إرسال المعايير الـ 9 لدالة التنبؤ (تتضمن نوع السماد)
            res, current_acc = calculate_production(crop, area, soil, irrigation, fertilizer, fertilizer_type, seeds,
                                                    w_data)

            # 🛡️ نظام الحماية (Fail-Safe): فحص إذا كان النظام أرجع رسالة حظر لعدم توفر البيانات
            if res is None:
                st.error(current_acc)  # طباعة رسالة الحظر للمستخدم
                return  # إيقاف إكمال الكود لعدم حفظ السجل أو عرض نتائج عشوائية

            # --- 🌡️🌧️ منطق الحسبة المصححة والدقيقة لتقرير الإرواء بناءً على طقس العراق اللحظي ---
            current_temp = w_data.get('temp', 25)
            rain_amount = w_data.get("rain", 0.0)

            # عامل الحرارة: يزيد الاحتياج 4% لكل درجة فوق الـ 25 مئوية
            temp_factor = max(0.5, 1.0 + (current_temp - 25) * 0.04)
            # تحويل المطر من ملم إلى متر مكعب لكل دونم (1 ملم مطر = 2.5 متر مكعب للدونم العراقي)
            rain_m3_per_dunum = rain_amount * 2.5

            # المعادلة التفاعلية الذكية: (الاحتياج الأساسي × عامل التربة × عامل الحرارة) - كمية المطر الفعلي
            exact_per_dunum = max(0.0, (crop_base * soil_fact * temp_factor) - rain_m3_per_dunum)
            exact_total_water = round(exact_per_dunum * area, 1)

            # تخزين مؤقت لربط تبويب الجدوى الاقتصادية والمالية
            st.session_state.cached_production = {"area": area, "yield": res, "crop": crop, "city": city}

            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            # بناء السجل الشامل بالمسميات والمفاتيح المطلوبة
            new_record = {
                "تاريخ": current_timestamp,
                "محافظة": city,
                "محصول": crop,
                "مساحة (دونم)": area,
                "تربة": soil,
                "ري": irrigation,
                "نوع السماد": fertilizer_type,
                "السماد (كغم/دونم)": fertilizer,
                "مطر": f"{rain_amount} ملم",
                "حرارة": f"{w_data['temp']}°C",
                "رطوبة": f"{w_data['humidity']}%",
                "انتاج": f"{res} طن",
                "دقة": f"{current_acc}%"
            }

            # إدراج التقرير في بداية القائمة التاريخية ليعرض أولاً
            st.session_state.history_list.insert(0, new_record)

            # تحديث ملف السجل على الهارد ديسك تلقائياً وبأمان
            try:
                pd.DataFrame(st.session_state.history_list).to_csv(DB_FILE, index=False, encoding="utf-8-sig")
            except Exception as e:
                st.error(f"فشل في حفظ البيانات في ملف السجل التاريخي: {e}")

            # الاحتفاظ بالنتائج الفورية الحالية مع إضافة بيانات المياه
            st.session_state.latest_scan_results = {
                "city": city, "crop": crop, "res": res, "current_acc": current_acc, "w_data": w_data,
                "exact_water": exact_total_water, "irrigation_type": irrigation, "area": area
            }
            st.rerun()

    # عرض نتائج التحليل الزراعي والطقس اللحظية للمستخدم
    if 'latest_scan_results' in st.session_state and st.session_state.latest_scan_results:
        data = st.session_state.latest_scan_results
        w = data["w_data"]

        st.info(f"✨ حالة السماء الحالية في {data['city']}: {w['description']}")

        m1, m2, m3 = st.columns(3)
        m1.metric("🌡 الحرارة اللحظية", f"{w['temp']}°C")
        m2.metric("💧 الرطوبة الحالية", f"{w['humidity']}%")
        m3.metric("💨 سرعة الرياح", f"{w['wind_speed']} m/s")

        # --- 📑 الميزة الثانية: مربع كارت تقرير الإرواء الذكي وجدولة المياه لليوم ---
        rain_status = w.get('rain', 0.0)
        water_needed = data.get('exact_water', 0.0)
        irrigation_type = data.get('irrigation_type', 'المتبع')
        area_val = data.get('area', area)

        # صياغة نص الإرشاد الديناميكي بناءً على قراءات المطر الحقيقية
        if rain_status > 0.0 and water_needed == 0.0:
            irrigation_tip = "🌧️ **تنبيه الري التكميلي:** الأمطار الحالية كافية تماماً لإرواء المحصول، يرجى **إيقاف المضخات كلياً** لحماية الجذور من الاختناق والتغدق."
        elif rain_status > 0.0:
            irrigation_tip = f"🌤️ **تنبيه ري مختلط:** تم الاستفادة من الأمطار وتقليل الاعتماد على البئر؛ يرجى تشغيل ري ({irrigation_type}) لتغطية النقص البسيط المتبقي فقط."
        else:
            irrigation_tip = f"☀️ **توصية الأجواء الجافة والصيفية:** انعدام الأمطار والحرارة المرتفعة يتطلبان تشغيل نظام ري ({irrigation_type}) في الصباح الباكر أو بعد الغروب لتفادي هدر وتبخر المياه."

        st.markdown(f"""
        <div style='background-color: #E8F5E9; border-right: 5px solid #2E7D32; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 15px; text-align: right;'>
            <h4 style='color: #1B5E20; margin-top: 0; font-weight: bold;'>📑 تقرير الإرواء الذكي وجدولة المياه لليوم</h4>
            <p style='color: #2E7D32; margin-bottom: 6px; font-size: 15px;'>• طبقاً لطقس اليوم ومعدل المطر الحالي الحقيقي البالغ (<b>{rain_status} ملم</b>):</p>
            <p style='color: #2E7D32; margin-bottom: 10px; font-size: 15px;'>• يحتاج حقل محصول الـ(<b>{data['crop']}</b>) بمساحة <b>{area_val} دونم</b> كلياً إلى: <span style='font-size: 18px; font-weight: bold; color: #0D47A1; background-color: #E3F2FD; padding: 2px 6px; border-radius: 4px;'>{water_needed} متر مكعب</span> من مياه الري الفعالة.</p>
            <hr style='border: 0; border-top: 1px solid #C8E6C9; margin: 8px 0;'>
            <p style='color: #1B5E20; margin-bottom: 0; font-size: 14px; font-weight: 500;'>{irrigation_tip}</p>
        </div>
        """, unsafe_allow_html=True)

        for alert in get_smart_alerts(w['temp'], w['humidity']):
            st.warning(alert)

        st.success(f"🌾 تم التنبؤ بإنتاج إجمالي تقديري للمزرعة: {data['res']} طن")
        st.metric(label="🎯 نسبة موثوقية الثقة التنبؤية للدراسة الحالية", value=f"{data['current_acc']}%")

        with st.expander("💡 توصية زراعية مخصصة مدعومة بـ Gemini", expanded=True):
            with st.spinner("جاري صياغة التوصية..."):
                advice = get_personalized_advice(data['crop'], data['city'], w['description'], w['temp'])
                if advice.startswith("❌") or advice.startswith("⚠️"):
                    st.error(advice)
                else:
                    st.write(advice)
        st.markdown("<br>", unsafe_allow_html=True)

        # توليد رسم بياني تفاعلي تلقائي
        if st.session_state.history_list:
            fig = px.bar(
                pd.DataFrame(st.session_state.history_list),
                x="محصول",
                y="مساحة (دونم)",
                color="محافظة",
                labels={"مساحة (دونم)": "المساحة بالدونم"}
            )
            st.subheader("📊 تحليل مقارن للمساحات المزروعة في سجل عملياتك الموثق")
            st.plotly_chart(fig, use_container_width=True)