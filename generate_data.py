import pandas as pd
import numpy as np


def generate_agricultural_data(num_records=1500, use_seed=True):
    """
    دالة ذكية لتوليد بيانات زراعية محاكية للواقع العراقي.
    إذا كان use_seed=True: يتم توليد نفس الـ 1500 سجل دائماً (لضبط المصنع).
    إذا كان use_seed=False: يتم توليد أرقام وسيناريوهات جديدة تماماً في كل مرة.
    """
    if use_seed:
        np.random.seed(42)  # تثبيت العشوائية
    else:
        np.random.seed(None)  # تحرير العشوائية لتوليد بيانات جديدة للذكاء الاصطناعي

    # المعطيات الأساسية للبيئة الزراعية العراقية
    cities = ["بغداد", "الموصل", "البصرة", "بابل", "واسط", "النجف", "كربلاء", "الأنبار", "ديالى", "ميسان"]
    crops = ["حنطة", "شعير", "ذرة", "خضراوات", "فواكه", "تمور", "رز"]
    soils = ["طينية", "رملية", "مختلطة"]
    irrigations = ["سيحي/غمر", "رش محوري", "تنقيط"]
    seeds = ["محسنة", "عادية"]
    fertilizer_types = ["يوريا (N)", "داب (DAP)", "مركب (NPK)", "عضوي"]

    data = []

    for _ in range(num_records):
        city = np.random.choice(cities)
        crop = np.random.choice(crops)
        soil = np.random.choice(soils)
        irrigation = np.random.choice(irrigations)
        seed = np.random.choice(seeds)
        fertilizer_type = np.random.choice(fertilizer_types)
        fertilizer = np.random.randint(20, 120)

        temp = round(np.random.uniform(15.0, 45.0), 1)
        humidity = round(np.random.uniform(20.0, 80.0), 1)

        base_yield = 1000.0
        if crop in ["حنطة", "شعير", "ذرة"]:
            base_yield = np.random.uniform(800.0, 1500.0)
        elif crop in ["خضراوات", "فواكه"]:
            base_yield = np.random.uniform(1500.0, 3500.0)
        elif crop == "تمور":
            base_yield = np.random.uniform(1200.0, 2500.0)
        elif crop == "رز":
            base_yield = np.random.uniform(900.0, 1800.0)

        factor = 1.0

        if temp > 38.0 or temp < 18.0: factor -= 0.20
        if humidity > 60.0 or humidity < 30.0: factor -= 0.10

        if fertilizer >= 80:
            factor += 0.15
        elif fertilizer < 40:
            factor -= 0.15

        if soil == "طينية" and crop in ["حنطة", "رز"]: factor += 0.10
        if soil == "رملية" and crop in ["خضراوات", "فواكه"] and irrigation == "تنقيط": factor += 0.10
        if soil == "رملية" and irrigation == "سيحي/غمر": factor -= 0.25

        if fertilizer_type == "يوريا (N)" and crop in ["خضراوات", "ذرة"]: factor += 0.15
        if fertilizer_type == "داب (DAP)" and crop in ["حنطة", "شعير"]: factor += 0.15
        if fertilizer_type == "عضوي" and soil == "رملية": factor += 0.10

        final_yield = int(base_yield * factor * np.random.uniform(0.9, 1.1))

        data.append([city, crop, temp, humidity, soil, irrigation, fertilizer_type, fertilizer, seed, final_yield])

    # تحويل البيانات إلى إطار بيانات بأسماء أعمدة مطابقة للموديل
    df = pd.DataFrame(data, columns=[
        'المحافظة', 'المحصول', 'الحرارة', 'الرطوبة', 'نوع_التربة',
        'طريقة_الري', 'نوع_السماد', 'كمية_السماد_بالكغم', 'جودة_البذور', 'الإنتاج_بالدونم'
    ])

    return df


# الكود القديم الذي يعمل إذا تم تشغيل الملف بشكل منفصل من التيرمنال
if __name__ == "__main__":
    df = generate_agricultural_data(1500, use_seed=True)
    df.to_csv("iraq_agriculture_data.csv", index=False, encoding='utf-8-sig')
    print("تم توليد البيانات الافتراضية بنجاح!")