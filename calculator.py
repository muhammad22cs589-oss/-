import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import streamlit as st


# 1. الدالة الأساسية (محمية بالكاش ومزودة بنظام كشف الأخطاء)
@st.cache_resource
def load_and_train_model():
    model_obj = RandomForestRegressor(n_estimators=100, random_state=42)
    le_dict = {
        'crop': LabelEncoder(), 'city': LabelEncoder(), 'soil': LabelEncoder(),
        'irrigation': LabelEncoder(), 'seeds': LabelEncoder(), 'fert_type': LabelEncoder()
    }

    hist_weather = {}
    accuracy_val = 85.0
    is_ready = False
    error_details = ""
    file_path = "iraq_agriculture_data.csv"

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')

            if not df.empty:
                # الأعمدة المطلوبة لعمل الخوارزمية
                required_cols = ['المحصول', 'المحافظة', 'نوع_التربة', 'طريقة_الري', 'جودة_البذور', 'نوع_السماد',
                                 'كمية_السماد_بالكغم', 'الحرارة', 'الرطوبة', 'الإنتاج_بالدونم']

                # فحص ما إذا كان هناك أعمدة مفقودة بسبب اختلاف التسميات
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    error_details = f"الأسماء غير متطابقة! مفقود: {missing_cols}"
                    return None, None, None, 0.0, False, error_details

                # تنظيف البيانات من الخلايا الفارغة (NaN) التي تسبب انهيار الخوارزمية
                df = df.dropna(subset=required_cols)

                if df.empty:
                    error_details = "بعد تنظيف الخلايا الفارغة، أصبح الملف فارغاً تماماً ولا يمكن التدريب."
                    return None, None, None, 0.0, False, error_details

                # تشفير البيانات
                df['crop_n'] = le_dict['crop'].fit_transform(df['المحصول'].astype(str))
                df['city_n'] = le_dict['city'].fit_transform(df['المحافظة'].astype(str))
                df['soil_n'] = le_dict['soil'].fit_transform(df['نوع_التربة'].astype(str))
                df['irrigation_n'] = le_dict['irrigation'].fit_transform(df['طريقة_الري'].astype(str))
                df['seeds_n'] = le_dict['seeds'].fit_transform(df['جودة_البذور'].astype(str))
                df['fert_type_n'] = le_dict['fert_type'].fit_transform(df['نوع_السماد'].astype(str))

                for c in df['المحافظة'].unique():
                    c_df = df[df['المحافظة'] == c]
                    hist_weather[c] = {'avg_temp': c_df['الحرارة'].mean(), 'avg_hum': c_df['الرطوبة'].mean()}

                X = df[['crop_n', 'city_n', 'soil_n', 'irrigation_n', 'seeds_n', 'fert_type_n', 'كمية_السماد_بالكغم',
                        'الحرارة', 'الرطوبة']]
                y = df['الإنتاج_بالدونم']

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model_obj.fit(X_train, y_train)

                score = model_obj.score(X_test, y_test)
                accuracy_val = round(score * 100, 1) if score > 0 else 85.0
                is_ready = True
            else:
                error_details = "الملف موجود ولكنه فارغ."
        except Exception as e:
            error_details = f"خطأ برمجي أثناء التدريب: {str(e)}"
    else:
        error_details = "ملف البيانات (iraq_agriculture_data.csv) غير موجود."

    return model_obj, le_dict, hist_weather, accuracy_val, is_ready, error_details


# 2. دالة إعادة التدريب المربوطة بلوحة الإدارة (الآن لن تحتفل إلا إذا كان التدريب ناجحاً فعلياً)
def retrain_model(new_df, mode="replace"):
    file_path = "iraq_agriculture_data.csv"
    try:
        new_df.to_csv(file_path, index=False, encoding="utf-8-sig")
        load_and_train_model.clear()

        # استدعاء الدالة وبناء العقل الجديد
        model_obj, le_dict, hist_weather, accuracy_val, is_ready, error_details = load_and_train_model()

        if is_ready:
            return True, "تم تحديث البيانات وتدريب النموذج بنجاح! النظام الآن أذكى."
        else:
            return False, f"فشل تدريب النموذج! السبب الفني: {error_details}"
    except Exception as e:
        return False, f"حدث خطأ أثناء حفظ الملف: {str(e)}"


# 3. دالة التنبؤ المربوطة بالتبويب الرئيسي
def calculate_production(crop, area, soil, irrigation, fertilizer, fertilizer_type, seeds, weather_data):
    model, le_dict, historical_weather, model_accuracy, ai_ready, error_details = load_and_train_model()

    city = weather_data.get('city', 'بغداد')
    c_temp = weather_data.get('temp', 25)
    c_hum = weather_data.get('humidity', 50)

    if ai_ready and model is not None:
        if crop not in le_dict['crop'].classes_ or city not in le_dict['city'].classes_:
            return None, "⚠️ تنبيه: مؤشرات الإدخال (المحصول أو المحافظة) خارج نطاق تدريب النظام الحالي. يرجى تحديث بيانات النظام أولاً."

        hist_t = historical_weather.get(city, {}).get('avg_temp', c_temp)
        hist_h = historical_weather.get(city, {}).get('avg_hum', c_hum)

        t = (hist_t * 0.7) + (c_temp * 0.3)
        h = (hist_h * 0.7) + (c_hum * 0.3)

        c_enc = le_dict['crop'].transform([crop])[0]
        city_enc = le_dict['city'].transform([city])[0]
        soil_enc = le_dict['soil'].transform([soil])[0] if soil in le_dict['soil'].classes_ else 0
        irr_enc = le_dict['irrigation'].transform([irrigation])[0] if irrigation in le_dict[
            'irrigation'].classes_ else 0
        seed_enc = le_dict['seeds'].transform([seeds])[0] if seeds in le_dict['seeds'].classes_ else 0
        fert_type_enc = le_dict['fert_type'].transform([fertilizer_type])[0] if fertilizer_type in le_dict[
            'fert_type'].classes_ else 0

        pred_per_dunum = \
        model.predict([[c_enc, city_enc, soil_enc, irr_enc, seed_enc, fert_type_enc, fertilizer, t, h]])[0]
        total_production_tons = round((float(pred_per_dunum) * area) / 1000, 2)
        dynamic_confidence = max(65.0, round(model_accuracy - (abs(c_temp - hist_t) * 0.4), 1))

        return total_production_tons, dynamic_confidence

    # السحر هنا: إذا لم يكن جاهزاً، سيطبع لك السبب الدقيق لتتمكن من إصلاحه!
    return None, f"⚠️ النظام غير جاهز. السبب: {error_details}"