import requests
import streamlit as st


@st.cache_data(ttl=1800)  # كاش لمدة 30 دقيقة لتوفير استهلاك الـ API وتسريع الاستجابة
def get_weather_data(city_name):
    """جلب بيانات الطقس الحقيقية بآلية برمجية مختصرة ومحمية بالكاش والأسرار"""

    # 🔒 استدعاء المفتاح بأمان
    try:
        WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
    except KeyError:
        return {"status": "error", "message": "مفتاح الطقس مفقود من ملف الأسرار"}

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=ar"

    try:
        res = requests.get(url, timeout=5).json()
        if res.get("cod") == 200:
            return {
                "city": city_name, "temp": res["main"]["temp"], "humidity": res["main"]["humidity"],
                "pressure": res["main"]["pressure"], "wind_speed": res["wind"]["speed"],
                "description": res["weather"][0]["description"], "rain": res.get("rain", {}).get("1h", 0.0),
                "status": "success"
            }
    except:
        pass
    return {"status": "error", "message": "خطأ في الاتصال أو اسم المدينة غير دقيق"}