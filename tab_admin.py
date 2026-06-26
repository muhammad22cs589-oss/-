import streamlit as st
import pandas as pd
import os
import time
from calculator import retrain_model, load_and_train_model
from utils import centered_button
from generate_data import generate_agricultural_data  # استدعاء دالة التوليد الذكية
from ai_engine import fetch_gemini_text

def render_admin_tab():
    st.subheader("⚙️ لوحة إدارة النظام والتدريب المستمر (MLOps)")
    st.write("يرجى اختيار مسار تحديث النظام من التبويبات أدناه:")

    # إضافة تبويب ثالث للخيارات الذكية الجديدة
    task_tabs = st.tabs([
        "🔄 التحديث من سجل النظام",
        "📥 إرفاق ملف خارجي",
        "🧠 التوليد الذكي وإعادة الضبط"
    ])

    BASE_FILE = "iraq_agriculture_data.csv"
    SESSION_FILE = "session_data.csv"
    required_cols = ['المحصول', 'المحافظة', 'نوع_التربة', 'طريقة_الري', 'جودة_البذور', 'نوع_السماد',
                     'كمية_السماد_بالكغم', 'الحرارة', 'الرطوبة', 'الإنتاج_بالدونم']

    # ==========================================
    # التبويب الأول: التحديث من سجل النظام الحالي
    # ==========================================
    with task_tabs[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            orig_count = len(pd.read_csv(BASE_FILE, encoding='utf-8-sig')) if os.path.exists(BASE_FILE) else 0
            session_count = len(pd.read_csv(SESSION_FILE, encoding='utf-8-sig')) if os.path.exists(SESSION_FILE) else 0

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("سجلات القاعدة الأساسية", f"{orig_count} سجل")
            with col_m2:
                st.metric("سجلات الجلسة المنتظرة", f"{session_count} سجل")

            st.markdown("<br>", unsafe_allow_html=True)

            if centered_button("🔄 دمج السجلات وتحديث الموديل", key="btn_merge_sync"):
                if session_count == 0:
                    st.warning("⚠️ لا توجد سجلات جديدة لدمجها حالياً.")
                else:
                    with st.spinner("جاري التنظيف وإعادة التدريب..."):
                        df_session = pd.read_csv(SESSION_FILE, encoding='utf-8-sig')

                        # التخلص من السجلات الفارغة تماماً قبل أي عملية
                        df_session.dropna(how='all', inplace=True)

                        df_mapped = pd.DataFrame()
                        df_mapped['المحافظة'] = df_session['محافظة']
                        df_mapped['المحصول'] = df_session['محصول']
                        df_mapped['الحرارة'] = df_session['حرارة'].astype(str).str.replace('°C', '',
                                                                                           regex=False).astype(float)
                        df_mapped['الرطوبة'] = df_session['رطوبة'].astype(str).str.replace('%', '', regex=False).astype(
                            float)
                        df_mapped['نوع_التربة'] = df_session['تربة']
                        df_mapped['طريقة_الري'] = df_session['ري']
                        df_mapped['نوع_السماد'] = df_session['نوع السماد'].fillna(
                            'مركب (NPK)') if 'نوع السماد' in df_session.columns else 'مركب (NPK)'
                        df_mapped['كمية_السماد_بالكغم'] = df_session['السماد (كغم/دونم)'].astype(float)
                        df_mapped['جودة_البذور'] = 'محسنة'

                        prod_ton = df_session['انتاج'].astype(str).str.replace(' طن', '', regex=False).astype(float)
                        area_dunum = df_session['مساحة (دونم)'].astype(float)
                        df_mapped['الإنتاج_بالدونم'] = (prod_ton * 1000) / area_dunum
                        df_mapped = df_mapped[required_cols]

                        # تنظيف إضافي لضمان عدم وجود سجلات فارغة بعد التعيين
                        df_mapped.dropna(how='all', inplace=True)

                        if os.path.exists(BASE_FILE):
                            df_orig = pd.read_csv(BASE_FILE, encoding='utf-8-sig')
                            df_orig = df_orig[required_cols] if all(
                                c in df_orig.columns for c in required_cols) else pd.DataFrame(columns=required_cols)
                        else:
                            df_orig = pd.DataFrame(columns=required_cols)

                        # دمج وحذف المكرر والتأكد من حذف الفارغ
                        df_final = pd.concat([df_orig, df_mapped], axis=0, ignore_index=True).dropna(
                            how='all').drop_duplicates()

                        added_records = len(df_final) - len(df_orig)

                        df_final.to_csv(BASE_FILE, index=False, encoding='utf-8-sig')

                        status, msg = retrain_model(df_final, "replace")
                        if status:
                            # تم إزالة أوامر مسح ملف الجلسة بناءً على طلبك
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            load_and_train_model()

                            st.success("🎉 تم دمج السجلات وتحديث الموديل بنجاح!")

                            # ملخص العملية للمستخدم
                            summary_msg = f"""
                            📝 **ملخص ما تم عمله:**
                            * تم تنظيف البيانات وتجاهل أي سجل فارغ أو مكرر.
                            * تم إضافة `{added_records}` سجل فريد جديد إلى قاعدة البيانات.
                            * لم يتم مسح سجلاتك السابقة من الجلسة (بناءً على إعداداتك).
                            * إجمالي السجلات في الموديل الآن: `{len(df_final)}` سجل.
                            """
                            st.info(summary_msg)

                            time.sleep(5)
                            st.rerun()
                        else:
                            st.error(f"❌ خطأ: {msg}")
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")

    # ==========================================
    # التبويب الثاني: إرفاق ملف خارجي
    # ==========================================
        # ==========================================
        # التبويب الثاني: إرفاق ملف خارجي (مع فحص حاسم للهيكلية ومنع الأعمدة الزائدة)
        # ==========================================
        with task_tabs[1]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "📋 **توجيه إداري:** يرجى رفع ملف Excel أو CSV يحتوي على البيانات المحدثة. سيقوم النظام بفحص الأعمدة للتأكد من مطابقتها تماماً لهيكلية البرنامج المنشودة.")

            uploaded_file = st.file_uploader("📥 رفع ملف البيانات الجديد (CSV أو XLSX)", type=['csv', 'xlsx'])

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        new_df = pd.read_csv(uploaded_file)
                    else:
                        new_df = pd.read_excel(uploaded_file)

                    # 1. تنظيف أولي: حذف أي سطر فارغ تماماً في الملف المرفوع
                    new_df.dropna(how='all', inplace=True)

                    st.success("✅ تم رفع الملف بنجاح! جاري فحص الهيكلية...")
                    st.write("🔍 **معاينة لأول 5 أسطر من الملف المرفوع:**")
                    st.dataframe(new_df.head())

                    # كشف الأعمدة الزائدة والغريبة التي ليست من ضمن الهيكلية المطلوبة
                    extra_cols = [col for col in new_df.columns if col not in required_cols]
                    missing_cols = [col for col in required_cols if col not in new_df.columns]

                    # 2. عرض رسالة التحذير الصارمة إذا وُجدت أعمدة غريبة
                    if extra_cols:
                        st.error(
                            f"⚠️ تنبيه: الملف يحتوي على أعمدة زائدة: {extra_cols}. هذه الأعمدة لا يمكنني إضافتها لأنها ليست من هيكلية البرنامج.")

                    if missing_cols:
                        st.warning(f"⚠️ تنبيه: الملف يفتقد إلى بعض الأعمدة الأساسية المطلوبة: {missing_cols}")

                    if centered_button("🤖 تحليل ومطابقة البيانات (بواسطة Gemini)", key="btn_gemini_analyze"):
                        with st.spinner("جاري فحص جودة البيانات وهيكليتها..."):
                            columns_str = ", ".join(new_df.columns)
                            prompt = f"""
                            أنت مهندس بيانات. تم رفع ملف زراعي يحتوي على الأعمدة التالية: {columns_str}.
                            الأعمدة المطلوبة في النظام هي: {required_cols}.
                            هل الأعمدة المرفوعة قريبة أو تتطابق مع المطلوبة؟ أعطني تقريراً قصيراً جداً (3 أسطر) وهل تنصح باعتماد الملف؟
                            """
                            ai_report = fetch_gemini_text(prompt)
                            st.markdown(f"**📊 تقرير الذكاء الاصطناعي:**\n{ai_report}")

                    st.markdown("---")
                    st.subheader("🎛️ استراتيجية دمج وتدريب البيانات")
                    strategy_tab2 = st.radio(
                        "اختر طريقة التعامل مع البيانات الجديدة:",
                        ["➕ دمج وتوسيع السجلات (إضافة كـ أسطر جديدة مع البيانات القديمة بدون تكرار وبنفس الأعمدة)",
                         "🔄 مسح شامل واستبدال (تصفير النظام والاعتماد على الملف الجديد فقط)"],
                        key="strategy_tab2"
                    )

                    if centered_button("🚀 بدء تدريب الخوارزمية وتحديث النظام", key="btn_train_model"):
                        # إيقاف المعالجة فوراً وحظر التدريب إذا كانت هناك أعمدة غريبة أو مفقودة في حالة الدمج
                        if extra_cols:
                            st.error(
                                f"❌ تم إلغاء العملية! يرجى إزالة الأعمدة التالية أولاً وإعادة رفع الملف: {extra_cols}. (لا يمكنني إضافتها لأنها ليست من هيكلية البرنامج).")
                        elif missing_cols:
                            st.error(
                                f"❌ تم إلغاء العملية! الملف يفتقر إلى الأعمدة المطلوبة للنظام: {missing_cols}. يرجى تهيئة الملف بشكل صحيح.")
                        else:
                            with st.spinner("جاري معالجة الملف وتطهيره من التكرار وتدريب النموذج..."):

                                # فلترة وضمان أخذ الأعمدة المطلوبة فقط وبالترتيب الصحيح وحذف الفارغ كلياً
                                df_cleaned_new = new_df[required_cols].dropna(how='all')
                                summary_msg_tab2 = ""

                                # ------------------------------------
                                # الاختيار الأول: دمج عمودي آمن (أسطر وسجلات فقط)
                                # ------------------------------------
                                if "دمج" in strategy_tab2:
                                    if os.path.exists(BASE_FILE):
                                        try:
                                            df_old_tab2 = pd.read_csv(BASE_FILE, encoding='utf-8-sig')
                                            df_old_tab2 = df_old_tab2[required_cols] if all(
                                                c in df_old_tab2.columns for c in required_cols) else pd.DataFrame(
                                                columns=required_cols)
                                        except:
                                            df_old_tab2 = pd.DataFrame(columns=required_cols)
                                    else:
                                        df_old_tab2 = pd.DataFrame(columns=required_cols)

                                    initial_rows = len(df_old_tab2)

                                    # دمج السجلات عمودياً وحذف القيم الفارغة والمكررة بالكامل
                                    df_final = pd.concat([df_old_tab2, df_cleaned_new], ignore_index=True).dropna(
                                        how='all').drop_duplicates()
                                    final_rows = len(df_final)
                                    added_rows = final_rows - initial_rows

                                    df_final.to_csv(BASE_FILE, index=False, encoding='utf-8-sig')
                                    status, msg = retrain_model(df_final, "replace")

                                    summary_msg_tab2 = f"""
                                    📝 **ملخص ما تم عمله (دمج السجلات بنجاح):**
                                    * تم الحفاظ على هيكلية الأعمدة الأساسية الـ {len(required_cols)} بدقة ومنع أي عمود غريب.
                                    * تم تجاهل وتنظيف أي سجلات فارغة أو مكررة تماماً.
                                    * عدد السجلات الأصلية السابقة: `{initial_rows}` سجل.
                                    * عدد السجلات الفريدة المضافة من الملف الجديد المرفوع: `{added_rows}` سجل جديد.
                                    * إجمالي قاعدة البيانات الحالي بعد الدمج السليم: `{final_rows}` سجل.
                                    """

                                # ------------------------------------
                                # الاختيار الثاني: استبدال كلي نظيف
                                # ------------------------------------
                                else:
                                    if os.path.exists(BASE_FILE):
                                        try:
                                            os.remove(BASE_FILE)
                                        except:
                                            pass

                                    df_final = df_cleaned_new.drop_duplicates()
                                    df_final.to_csv(BASE_FILE, index=False, encoding='utf-8-sig')
                                    status, msg = retrain_model(df_final, "replace")
                                    final_rows = len(df_final)

                                    summary_msg_tab2 = f"""
                                    📝 **ملخص ما تم عمله (استبدال كامل):**
                                    * تم حذف ملف البيانات القديم تماماً من النظام.
                                    * تم تخزين واعتماد سجلات الملف الجديد كقاعدة بيانات حصرية وحيدة ومطابقة للهيكلية.
                                    * إجمالي السجلات الفريدة المخزنة حالياً: `{final_rows}` سجل.
                                    """

                                if status:
                                    try:
                                        st.cache_data.clear()
                                        st.cache_resource.clear()
                                        load_and_train_model()
                                    except:
                                        pass

                                    st.success(f"🎉 {msg}")
                                    st.info(summary_msg_tab2)
                                    st.balloons()
                                    time.sleep(5)
                                    st.rerun()
                                else:
                                    st.error(f"❌ خطأ أثناء التدريب: {msg}")

                except Exception as e:
                    st.error(f"❌ حدث خطأ في معالجة أو قراءة الملف: {e}")

    # ==========================================
    # التبويب الثالث: التوليد الذكي وإعادة الضبط
    # ==========================================
        # ==========================================
        # التبويب الثالث: التوليد الذكي وإعادة الضبط
        # ==========================================
        with task_tabs[2]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "💡 **إدارة متقدمة:** يمكنك إعادة النظام لنقطة الصفر، أو توسيع قاعدة البيانات ببيانات اصطناعية ذكية لمنع التكرار وحذف الحقول الفارغة.")

            c1, c2 = st.columns(2)

            # 🟢 الزر الأول: التوسيع الذكي (بدون Seed مع منع التكرار وتطهير الفارغ)
            with c1:
                st.markdown("<h4 style='color:#2E7D32;'>🚀 التوسيع الذكي (Smart Append)</h4>", unsafe_allow_html=True)
                st.write(
                    "يقوم بتوليد سيناريوهات وظروف طقس جديدة ويضيف السجلات غير المكررة فقط لتوسيع إدراك الذكاء الاصطناعي.")

                if centered_button("توليد ودمج السجلات الذكية", key="btn_smart_gen"):
                    with st.spinner("جاري التوليد العشوائي والمقارنة لمنع التكرار..."):
                        # 1. توليد بيانات جديدة بعشوائية مطلقة (use_seed=False)
                        df_new = generate_agricultural_data(num_records=1500, use_seed=False)

                        # تنظيف أولي للبيانات المولدة من أي قيم فارغة إن وجدت
                        df_new.dropna(how='all', inplace=True)

                        # 2. قراءة الملف الأصلي
                        if os.path.exists(BASE_FILE):
                            df_orig = pd.read_csv(BASE_FILE, encoding='utf-8-sig')
                            valid_cols = [c for c in required_cols if c in df_orig.columns]
                            if len(valid_cols) == len(required_cols):
                                df_orig = df_orig[required_cols]
                            else:
                                df_orig = pd.DataFrame(columns=required_cols)
                        else:
                            df_orig = pd.DataFrame(columns=required_cols)

                        # 3. الدمج العمودي وحذف السجلات المتطابقة كلياً وتنظيف السطور الفارغة تماماً
                        df_final = pd.concat([df_orig, df_new], ignore_index=True).dropna(how='all').drop_duplicates()

                        # حساب عدد السجلات الجديدة الفعلية التي أضيفت بعد الفلترة
                        added_records = len(df_final) - len(df_orig)

                        if added_records > 0:
                            df_final.to_csv(BASE_FILE, index=False, encoding='utf-8-sig')
                            status, msg = retrain_model(df_final, "replace")

                            summary_msg_tab3_1 = f"""
                            📝 **ملخص ما تم عمله (توسيع ذكي):**
                            * تم تشغيل نظام توليد البيانات الاصطناعية الذكي.
                            * تمت مقارنة وتصفية البيانات لمنع التكرار وحذف أي أسطر فارغة.
                            * تم إضافة `{added_records}` سجل فريد جديد يعزز من كفاءة واكتشاف الموديل.
                            * إجمالي السجلات الحالي في النظام: `{len(df_final)}` سجل.
                            """

                            if status:
                                try:
                                    st.cache_data.clear()
                                    st.cache_resource.clear()
                                    load_and_train_model()
                                except:
                                    pass
                                st.success(f"📈 تم إضافة {added_records} سجل فريد جديد بنجاح!")
                                st.info(summary_msg_tab3_1)
                                st.balloons()
                                time.sleep(5)
                                st.rerun()
                            else:
                                st.error(f"❌ خطأ أثناء التدريب: {msg}")
                        else:
                            st.warning(
                                "⚠️ جميع البيانات التي تم توليدها متطابقة ومكررة مع سجلاتك الحالية، لذا لم يتم إضافة أي جديد لحماية النموذج.")

            # 🔴 الزر الثاني: إعادة ضبط المصنع (مع Seed ثابت وتنظيف شامل)
            with c2:
                st.markdown("<h4 style='color:#C62828;'>🗑️ ضبط المصنع (Factory Reset)</h4>", unsafe_allow_html=True)
                st.write(
                    "يقوم بمسح كامل قاعدة البيانات الحالية والسجلات المؤقتة، ويعيد توليد الـ 1500 سجل الأصلي الثابت فقط.")

                if centered_button("إعادة ضبط النظام نهائياً", key="btn_factory_reset"):
                    with st.spinner("جاري محو البيانات وإعادة التوليد الأصلي القياسي..."):
                        # 1. توليد بيانات ثابتة (use_seed=True) وتطهيرها فوراً
                        df_factory = generate_agricultural_data(num_records=1500, use_seed=True)
                        df_factory.dropna(how='all', inplace=True)

                        df_factory.to_csv(BASE_FILE, index=False, encoding='utf-8-sig')

                        # 2. مسح ملف السجل والجلسة المؤقتة وتصفير عدادات الحالة لقاعدة البيانات
                        if os.path.exists(SESSION_FILE):
                            try:
                                os.remove(SESSION_FILE)
                            except:
                                pass

                        st.session_state.history_list = []
                        st.session_state.latest_scan_results = None

                        # 3. إعادة تدريب النموذج على النسخة النظيفة الافتراضية
                        status, msg = retrain_model(df_factory, "replace")

                        summary_msg_tab3_2 = f"""
                        📝 **ملخص ما تم عمله (إعادة ضبط المصنع):**
                        * تم تصفير ومسح جميع البيانات المدخلة وسجلات الجلسة المؤقتة كلياً.
                        * تم استرجاع واعادة بناء النسخة الأساسية النظيفة (1500 سجل ثابت).
                        * عاد النظام لهيكليته وحالته الافتراضية الأولى والآمنة تماماً.
                        """

                        if status:
                            try:
                                st.cache_data.clear()
                                st.cache_resource.clear()
                                load_and_train_model()
                            except:
                                pass
                            st.success("♻️ تمت عملية إعادة ضبط المصنع الافتراضية بنجاح!")
                            st.info(summary_msg_tab3_2)
                            time.sleep(5)
                            st.rerun()
                        else:
                            st.error(f"❌ خطأ أثناء إعادة البناء: {msg}")