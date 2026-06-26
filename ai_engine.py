import google.generativeai as genai
import streamlit as st


def get_all_api_keys():
    """جلب كافة المفاتيح المتاحة ديناميكياً من ملف الأسرار"""
    keys = []

    # حلقة تكرارية تفحص الأرقام من 1 إلى 4 وتجلب المفاتيح المتوفرة
    for i in range(1, 5):
        key_name = f"GEMINI_API_KEY_{i}"
        if key_name in st.secrets:
            keys.append(st.secrets[key_name])

    # دعم التسمية القديمة المفردة كخيار احتياطي أخير
    if not keys and "GEMINI_API_KEY" in st.secrets:
        keys.append(st.secrets["GEMINI_API_KEY"])

    return keys


def fetch_gemini_text(prompt, image=None):
    """دالة مركزية تدعم التدوير التلقائي لـ 4 مفاتيح عند استهلاك الحصة (Quota Exceeded)"""
    api_keys = get_all_api_keys()

    if not api_keys:
        return "⚠️ خطأ: لم يتم العثور على أي مفاتيح API في ملف الأسرار."

    last_error = ""

    # محاولة تشغيل البرومبت على كل مفتاح متاح بالتوالي
    for i, key in enumerate(api_keys):
        try:
            # تهيئة الجيمني بالمفتاح الحالي في اللفة
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            # محاولة توليد المحتوى
            response = model.generate_content([prompt, image] if image else prompt)
            return response.text

        except Exception as e:
            # تخزين نص الخطأ الحالي للرجوع إليه إذا فشلت جميع المفاتيح
            last_error = str(e)
            # في حال حدوث خطأ 429 (انتهاء الحصة)، سينتقل الكود تلقائياً للمفتاح التالي في اللفة القادمة
            continue

            # إذا مر الكود على كل المفاتيح الـ 4 وفشلت كلها:
    return f"⚠️ عذراً، جميع المفاتيح الـ 4 المتاحة استهلكت حصتها اليومية المجانية. تفاصيل آخر خطأ: {last_error}"


def agri_chat(q):
    return fetch_gemini_text(f"أنت مستشار زراعي عراقي خبير. أجب باختصار مفيد وبدقة علمية عالية: {q}")


def diagnose_plant_disease(img):
    return fetch_gemini_text(
        "أنت بروفيسور تشخيص أمراض نباتات زراعية. ما هو المرض الظاهر في الصورة وما علاجه باختصار شديد؟", img)


def get_smart_alerts(t, h):
    alerts = []
    if t > 38: alerts.append("🌡 تحذير موجة حر: خطر الإجهاد الحراري، يُفضل الري في الساعات المتأخرة أو الصباح الباكر.")
    if h > 80 and 20 < t < 30: alerts.append("🦠 بيئة خصبة للأمراض: انتشار الفطريات.")
    if t < 7: alerts.append("❄️ تحذير صقيع محتمل: قم بتغطية الشتلات الحساسة.")
    return alerts


def get_personalized_advice(crop, city, weather_desc, temp):
    prompt = f"المزارع في {city} يزرع {crop} والطقس الحالي {weather_desc} والحرارة {temp}. أعطه نصيحة زراعية ذكية ومختصرة جداً تناسب هذه الظروف."
    return fetch_gemini_text(prompt)


def calculate_economics(area, expected_yield, cost_per_dunum, price_per_ton):
    """دالة حساب الجدوى الاقتصادية المبسطة للمزارع"""
    try:
        total_cost = area * cost_per_dunum
        total_income = expected_yield * price_per_ton
        net_profit = total_income - total_cost

        if net_profit > 0:
            status = "📈 ربح متوقع جيد جداً"
        elif net_profit < 0:
            status = "📉 خسارة تقديرية، يرجى مراجعة المصاريف"
        else:
            status = "⚖️ نقطة التعادل (لا ربح ولا خسارة)"

        return net_profit, status
    except Exception as e:
        return 0, f"⚠️ خطأ في الحساب المالي: {str(e)}"