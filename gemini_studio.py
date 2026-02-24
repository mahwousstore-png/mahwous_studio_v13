"""
🌟 مهووس Gemini Studio — كل شيء من مفتاح واحد
نصوص + صور + فيديو + صوت  ←→  GEMINI_API_KEY فقط
"""

import streamlit as st
import base64
import io
import time
from datetime import datetime

st.set_page_config(
    page_title="🌟 Gemini All-In-One Studio",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
html,body,[class*="css"]{font-family:'Cairo',sans-serif!important;direction:rtl}
.stApp{background:#050A1A!important}
[data-testid="stSidebar"]{background:#080D18!important;border-left:2px solid rgba(100,160,255,.20)!important}
h1,h2,h3{color:#6EB4FF!important}
.stButton>button{background:linear-gradient(135deg,#0A3A8A,#1A6FFF)!important;color:#fff!important;
  font-weight:800!important;border:none!important;border-radius:.7rem!important;
  font-family:'Cairo',sans-serif!important;transition:all .2s!important}
.stButton>button:hover{box-shadow:0 0 20px rgba(42,127,255,.4)!important;transform:translateY(-1px)!important}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  background:#0D1525!important;color:#C8D8F0!important;
  border:1.5px solid rgba(100,160,255,.30)!important;border-radius:.6rem!important}
.stTabs [data-baseweb="tab-list"]{background:#0A1020!important;border-radius:.8rem;padding:4px;gap:4px}
.stTabs [data-baseweb="tab"]{color:rgba(150,180,255,.5)!important;font-weight:700!important;border-radius:.5rem!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1A5FBF,#2A8FFF)!important;color:#fff!important}
.card{background:#0D1525;border:1.5px solid rgba(100,160,255,.18);border-radius:1rem;padding:1.2rem;margin-bottom:1rem}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:.7rem;font-weight:800;
  letter-spacing:.1em;margin-bottom:.5rem}
.badge-free{background:rgba(52,211,153,.15);color:#34d399;border:1px solid rgba(52,211,153,.3)}
.badge-paid{background:rgba(251,191,36,.10);color:#fbbf24;border:1px solid rgba(251,191,36,.25)}
.tag{font-size:.62rem;font-weight:700;background:rgba(100,160,255,.12);
  color:#6EB4FF;border-radius:4px;padding:2px 7px;margin:1px}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in {
    "gemini_key": "", "gen_count": 0,
    "last_text": "", "last_images": {}, "last_audio": None,
    "veo_operation": None, "veo_state": "idle", "veo_url": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.5rem 0'>
      <div style='font-size:2.5rem'>🌟</div>
      <div style='color:#6EB4FF;font-size:1.1rem;font-weight:900'>Gemini All-In-One</div>
      <div style='color:rgba(100,160,255,.5);font-size:.65rem;margin-top:4px'>
        نص · صور · فيديو · صوت — مفتاح واحد
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🔑 مفتاح Google Gemini")
    api_key = st.text_input(
        "GEMINI_API_KEY", type="password",
        value=st.session_state.gemini_key,
        placeholder="AIzaSy...",
        label_visibility="collapsed"
    )
    if api_key:
        st.session_state.gemini_key = api_key

    # Test key button
    if st.button("🧪 اختبار المفتاح", use_container_width=True):
        if not api_key:
            st.warning("أدخل المفتاح أولاً")
        else:
            with st.spinner("جاري الفحص..."):
                try:
                    import requests as _rq
                    r = _rq.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                        timeout=10
                    )
                    if r.status_code == 200:
                        models = r.json().get("models", [])
                        model_names = [m["name"].replace("models/","") for m in models]
                        has_tts = any("tts" in m for m in model_names)
                        has_veo = any("veo" in m for m in model_names)
                        has_img = any("imagen" in m for m in model_names)
                        st.success("✅ المفتاح يعمل!")
                        st.markdown(f"""
                        <div class='card' style='padding:.8rem'>
                        🧠 النصوص: ✅ مفعّل<br>
                        🖼️ الصور (Imagen): {"✅" if has_img else "⚠️ يحتاج فوترة"}<br>
                        🎬 الفيديو (Veo): {"✅" if has_veo else "⚠️ يحتاج فوترة"}<br>
                        🎙️ الصوت (TTS): {"✅" if has_tts else "✅ متاح (preview)"}
                        </div>""", unsafe_allow_html=True)
                    elif r.status_code == 400:
                        st.error("❌ مفتاح غير صالح")
                    else:
                        st.error(f"❌ خطأ {r.status_code}")
                except Exception as e:
                    st.error(f"❌ {e}")

    st.markdown("---")

    # خريطة التكاليف
    st.markdown("### 💰 تكاليف Google API")
    st.markdown("""
    <div class='card' style='padding:.8rem;font-size:.8rem'>
    <span class='badge badge-free'>مجاني</span><br>
    🧠 Gemini 2.5 Flash النصوص<br>
    🖼️ Gemini Flash image gen<br>
    🎙️ TTS (حدود يومية)<br><br>
    <span class='badge badge-paid'>مدفوع (فوترة مطلوبة)</span><br>
    🖼️ Imagen 4.0 الصور (~$0.04/صورة)<br>
    🎬 Veo 3.1 الفيديو (~$0.15/ثانية)
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div class='card' style='text-align:center;padding:.8rem'>
    <div style='color:#6EB4FF;font-size:1.6rem;font-weight:900'>{st.session_state.gen_count}</div>
    <div style='color:rgba(150,180,255,.5);font-size:.7rem'>عمليات توليد</div>
    </div>""", unsafe_allow_html=True)

    if st.button("🗑️ مسح الجلسة", use_container_width=True):
        for k in ["last_text","last_images","last_audio","veo_operation","veo_state","veo_url","gen_count"]:
            st.session_state[k] = {} if k == "last_images" else (0 if k == "gen_count" else None if "veo" not in k or k=="veo_state" else "idle")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style='padding:1rem 0 1.5rem;border-bottom:1px solid rgba(100,160,255,.12);margin-bottom:1.5rem'>
  <h1 style='margin:0;font-size:1.6rem'>🌟 Gemini All-In-One Studio</h1>
  <p style='color:rgba(150,180,255,.45);font-size:.72rem;margin:4px 0 0;letter-spacing:.2em'>
    GEMINI 2.5 FLASH · IMAGEN 4.0 · VEO 3.1 · TTS — مفتاح Google واحد
  </p>
</div>""", unsafe_allow_html=True)

if not st.session_state.gemini_key:
    st.warning("⚠️ أدخل GEMINI_API_KEY في الشريط الجانبي لبدء الاستخدام")
    st.markdown("""
    <div class='card'>
    <strong>🔑 للحصول على مفتاحك المجاني:</strong><br><br>
    1️⃣ اذهب إلى <a href='https://aistudio.google.com/app/apikey' target='_blank'
       style='color:#6EB4FF'>aistudio.google.com/app/apikey</a><br>
    2️⃣ انقر "Create API Key"<br>
    3️⃣ الصق المفتاح في الحقل الجانبي<br><br>
    ✅ المفتاح يكفي للنصوص والصوت مجاناً<br>
    💳 للصور العالية الجودة والفيديو: فعّل الفوترة على 
    <a href='https://console.cloud.google.com/billing' target='_blank' style='color:#6EB4FF'>
    console.cloud.google.com/billing</a>
    </div>""", unsafe_allow_html=True)

# ── التبويبات ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 النصوص",
    "🖼️ الصور",
    "🎬 الفيديو",
    "🎙️ الصوت"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: النصوص
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🧠 توليد النصوص — Gemini 2.5 Flash")
    st.markdown('<span class="badge badge-free">مجاني تماماً</span>', unsafe_allow_html=True)

    L, R = st.columns([1, 1.2], gap="large")
    with L:
        txt_mode = st.selectbox("نوع المحتوى", [
            "✍️ نص حر",
            "📣 تعليق إعلاني لمنتج عطر",
            "📱 كابشن لإنستغرام",
            "🎬 سيناريو فيديو إعلاني",
            "📧 رسالة تسويقية",
            "🏷️ أفكار لأسماء عطور"
        ])
        user_prompt = st.text_area("فكرتك أو طلبك", height=100,
            placeholder="مثال: عطر عود ملكي للرجال، رائحة شرقية فاخرة...")
        temperature = st.slider("إبداعية الإجابة", 0.0, 1.0, 0.85, 0.05)

        # ربط نوع المحتوى بسيستم بروبت
        systems = {
            "✍️ نص حر": "أنت كاتب إبداعي محترف. أجب بالعربية.",
            "📣 تعليق إعلاني لمنتج عطر": "أنت خبير تسويق عطور فاخرة. اكتب تعليقاً إعلانياً جذاباً وشاعرياً بالعربية لا يتجاوز 100 كلمة. اجعله عاطفياً ومؤثراً.",
            "📱 كابشن لإنستغرام": "أنت متخصص في التسويق الرقمي. اكتب كابشن إنستغرام بالعربية مع إيموجي مناسبة وهاشتاقات. اجعله جذاباً ومؤثراً.",
            "🎬 سيناريو فيديو إعلاني": "أنت مخرج إعلانات فاخرة. اكتب سيناريو فيديو إعلاني لعطر بالعربية، يتضمن: المشهد، الحوار، حركة الكاميرا، المشاعر. 30-60 ثانية.",
            "📧 رسالة تسويقية": "أنت خبير تسويق. اكتب رسالة تسويقية احترافية بالعربية تقنع العميل بشراء العطر.",
            "🏷️ أفكار لأسماء عطور": "أنت مبدع في تسمية العطور. اقترح 10 أسماء فاخرة وجذابة مع معناها. الأسماء تكون بالعربية أو اللغات الشرقية.",
        }
        system_prompt = systems.get(txt_mode, "أنت مساعد إبداعي.")

        if st.button("✨ توليد النص", type="primary", use_container_width=True):
            if not user_prompt.strip():
                st.warning("أدخل فكرتك أولاً")
            elif not st.session_state.gemini_key:
                st.error("❌ أدخل مفتاح Gemini في الشريط الجانبي")
            else:
                with st.spinner("🧠 Gemini يكتب..."):
                    try:
                        from modules.gemini_engine import gemini_text
                        result = gemini_text(user_prompt, system_prompt)
                        st.session_state.last_text = result
                        st.session_state.gen_count += 1
                    except Exception as e:
                        st.error(f"❌ {e}")

    with R:
        st.markdown("**النتيجة:**")
        if st.session_state.last_text:
            st.markdown(f"""
            <div class='card' style='min-height:180px;line-height:1.9;font-size:.9rem;color:#C8D8F0'>
            {st.session_state.last_text.replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ حفظ النص",
                data=st.session_state.last_text,
                file_name=f"mahwous_text_{datetime.now().strftime('%H%M')}.txt",
                mime="text/plain")
        else:
            st.markdown("""
            <div style='border:2px dashed rgba(100,160,255,.12);border-radius:1rem;
            padding:60px;text-align:center;opacity:.3'>
            <div style='font-size:3rem'>🧠</div>
            <div style='margin-top:8px'>النص يظهر هنا</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: الصور
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🖼️ توليد الصور — Imagen 4.0")
    st.markdown("""
    <span class="badge badge-paid">Imagen 4.0 — يتطلب فوترة</span>
    <span class="badge badge-free">Gemini 2.0 Flash — مجاني (fallback)</span>
    """, unsafe_allow_html=True)

    L, R = st.columns([1, 1.4], gap="large")
    with L:
        MAHWOUS_DNA = (
            "Photorealistic 3D animated character Mahwous, Gulf Arab perfume expert, "
            "neatly styled dark hair, groomed beard, warm brown eyes, "
            "luxury black suit with gold tie, cinematic lighting, Pixar Disney 3D style, "
            "ultra HD 4K"
        )
        img_prompt = st.text_area("بروبت الصورة (إنجليزي أفضل)", height=90,
            value=f"{MAHWOUS_DNA}. Holding luxury oud perfume bottle, golden smoke.",
            placeholder="Describe the image in English for best results...")
        img_aspect = st.selectbox("النسبة", ["1:1", "9:16", "16:9"], index=0,
            format_func=lambda x: {
                "1:1": "1:1 مربع (إنستغرام)",
                "9:16": "9:16 عمودي (ستوري/تيك توك)",
                "16:9": "16:9 أفقي (يوتيوب)"
            }[x])
        platforms = st.multiselect(
            "توليد لمنصات متعددة",
            ["Instagram Post (1:1)", "Story/TikTok (9:16)", "YouTube (16:9)", "Twitter (16:9)"],
            default=["Instagram Post (1:1)"]
        )

        if st.button("🎨 توليد الصورة", type="primary", use_container_width=True):
            if not img_prompt.strip():
                st.warning("أدخل البروبت أولاً")
            elif not st.session_state.gemini_key:
                st.error("❌ أدخل مفتاح Gemini")
            else:
                aspect_map = {
                    "Instagram Post (1:1)": "1:1",
                    "Story/TikTok (9:16)":  "9:16",
                    "YouTube (16:9)":        "16:9",
                    "Twitter (16:9)":        "16:9",
                }
                imgs = {}
                bar = st.progress(0, text="⏳ جاري التوليد...")
                for i, plat in enumerate(platforms or ["Instagram Post (1:1)"]):
                    bar.progress(int((i + 0.5) / max(len(platforms or [1]), 1) * 100),
                                 text=f"⏳ {plat}...")
                    try:
                        from modules.gemini_engine import gemini_image
                        asp = aspect_map.get(plat, "1:1")
                        img_bytes = gemini_image(img_prompt, asp)
                        imgs[plat] = img_bytes
                    except Exception as e:
                        st.error(f"❌ {plat}: {e}")
                bar.progress(100, text="✅ تم!")
                if imgs:
                    st.session_state.last_images = imgs
                    st.session_state.gen_count += len(imgs)
                    st.rerun()

    with R:
        st.markdown("**الصور المُولَّدة:**")
        imgs = st.session_state.last_images
        if not imgs:
            st.markdown("""
            <div style='border:2px dashed rgba(100,160,255,.10);border-radius:1rem;
            padding:60px;text-align:center;opacity:.3'>
            <div style='font-size:3rem'>🖼️</div>
            <div style='margin-top:8px'>الصور تظهر هنا</div>
            </div>""", unsafe_allow_html=True)
        else:
            for plat, img_bytes in imgs.items():
                st.markdown(f"**{plat}**")
                st.image(img_bytes, use_container_width=True)
                st.download_button(
                    f"⬇️ تحميل {plat}",
                    data=img_bytes,
                    file_name=f"mahwous_{plat.split('(')[0].strip().lower().replace(' ','_')}.png",
                    mime="image/png",
                    key=f"dl_img_{plat}"
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: الفيديو
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🎬 توليد الفيديو — Veo 3.1")
    st.markdown('<span class="badge badge-paid">يتطلب تفعيل الفوترة · ~$0.15/ثانية</span>', unsafe_allow_html=True)

    # تفعيل الفوترة reminder
    with st.expander("💡 كيف أُفعّل الفوترة لـ Veo 3.1؟"):
        st.markdown("""
        1. اذهب إلى [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
        2. أنشئ حساب فوترة جديد أو اربط حساباً موجوداً
        3. اذهب إلى [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
        4. ابحث عن **"Generative Language API"** وفعّله
        5. **8 ثواني فيديو = ~$1.20** — تكلفة منخفضة مقارنة بـ Luma وRunway
        """)

    L, R = st.columns([1, 1.4], gap="large")
    with L:
        vid_prompt = st.text_area("بروبت الفيديو (إنجليزي أفضل)", height=120,
            placeholder="Mahwous character walks through a luxury perfume boutique in Dubai, golden lighting, cinematic 4K, slow motion...")
        vid_aspect = st.selectbox("النسبة", ["9:16", "16:9"],
            format_func=lambda x: "9:16 عمودي (تيك توك/ريلز)" if x == "9:16" else "16:9 أفقي (يوتيوب)")
        vid_duration = st.select_slider("المدة (ثواني)", options=[5, 8], value=8)
        vid_audio = st.checkbox("✅ توليد صوت تلقائي مع الفيديو", value=True)

        ref_img = st.file_uploader("📤 صورة مرجعية (اختياري)", type=["jpg","jpeg","png"])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎥 إنشاء الفيديو", type="primary", use_container_width=True,
                         disabled=(st.session_state.veo_state == "processing")):
                if not vid_prompt.strip():
                    st.warning("أدخل البروبت أولاً")
                elif not st.session_state.gemini_key:
                    st.error("❌ أدخل مفتاح Gemini")
                else:
                    with st.spinner("🚀 إرسال طلب Veo 3.1..."):
                        try:
                            from modules.gemini_engine import gemini_video_start
                            ref_bytes = ref_img.getvalue() if ref_img else None
                            result = gemini_video_start(
                                vid_prompt, vid_aspect, vid_duration, ref_bytes
                            )
                            st.session_state.veo_operation = result["operation"]
                            st.session_state.veo_state = "processing"
                            st.session_state.veo_url = None
                            st.session_state.gen_count += 1
                            st.success("✅ تم الإرسال! اضغط 'تحديث الحالة' خلال 3-5 دقائق")
                        except Exception as e:
                            st.error(f"❌ {e}")

        with c2:
            if st.button("🔄 تحديث الحالة", use_container_width=True,
                         disabled=(not st.session_state.veo_operation)):
                with st.spinner("فحص..."):
                    try:
                        from modules.gemini_engine import gemini_video_status, gemini_video_download
                        status = gemini_video_status(st.session_state.veo_operation)
                        if status["state"] == "completed":
                            st.session_state.veo_state = "completed"
                            st.session_state.veo_url = status.get("video_uri", "")
                            st.rerun()
                        elif status["state"] == "failed":
                            st.session_state.veo_state = "failed"
                            st.error(f"❌ فشل التوليد: {status.get('error','')}")
                        else:
                            prog = status.get("progress", 0)
                            st.info(f"⏳ جاري المعالجة... {prog}% — حاول مجدداً خلال دقيقة")
                    except Exception as e:
                        st.error(f"❌ {e}")

    with R:
        # حالة Veo
        state_map = {
            "idle":       ("⬜", "#606070", "انتظار طلب"),
            "processing": ("🌀", "#C87AFF", "جاري التوليد..."),
            "completed":  ("✅", "#50C878", "مكتمل!"),
            "failed":     ("❌", "#FF7070", "فشل"),
        }
        icon, color, label = state_map.get(st.session_state.veo_state, ("❓", "#888", "—"))
        st.markdown(f"""
        <div class='card' style='text-align:center;padding:1.2rem'>
          <div style='font-size:2.5rem'>{icon}</div>
          <div style='font-weight:900;color:{color};margin:.5rem 0'>{label}</div>
          <div style='font-size:.7rem;color:rgba(150,180,255,.4)'>
          {("معرف: " + st.session_state.veo_operation[:40] + "...") if st.session_state.veo_operation else "لا يوجد طلب نشط"}
          </div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.veo_state == "processing":
            st.info("⏳ Veo 3.1 يحتاج 3-5 دقائق — اضغط 'تحديث الحالة' كل دقيقة")

        if st.session_state.veo_url:
            st.video(st.session_state.veo_url)
            st.markdown(f"""
            <div style='text-align:center;margin-top:10px'>
            <a href='{st.session_state.veo_url}' target='_blank'
               style='background:#1A6FFF;color:#fff;padding:10px 24px;
               border-radius:.6rem;font-weight:800;text-decoration:none'>
               ⬇️ تحميل الفيديو
            </a></div>""", unsafe_allow_html=True)
        elif st.session_state.veo_state == "idle":
            st.markdown("""
            <div style='border:2px dashed rgba(100,160,255,.10);border-radius:1rem;
            padding:80px;text-align:center;opacity:.3'>
            <div style='font-size:3.5rem'>🎬</div>
            <div style='margin-top:8px'>الفيديو يظهر هنا</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: الصوت
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🎙️ توليد الصوت — Gemini 2.5 Flash TTS")
    st.markdown('<span class="badge badge-free">مجاني (حدود يومية تسمح بالاستخدام العادي)</span>', unsafe_allow_html=True)

    L, R = st.columns([1, 1], gap="large")
    with L:
        tts_text = st.text_area("النص المراد قراءته (عربي أو إنجليزي)", height=120,
            placeholder="مثال: مرحباً بكم في عالم مهووس للعطور الفاخرة. عطر اليوم يحمل أسرار المشرق...")

        from modules.gemini_engine import TTS_VOICES
        voice_choice = st.selectbox(
            "الصوت",
            list(TTS_VOICES.keys()),
            format_func=lambda v: TTS_VOICES[v],
            index=1  # Charon default
        )

        # أمثلة جاهزة
        st.markdown("**أمثلة جاهزة:**")
        examples = [
            ("إعلان عطر", "مرحباً بكم في عالم مهووس للعطور الفاخرة. عطرنا الجديد يجمع بين عبق العود الأصيل ونضارة زهور الربيع. لأنك تستحق الأفضل دائماً."),
            ("تعليق مهووس", "أنا مهووس! هذا العطر يأخذك في رحلة إلى أعماق الصحراء العربية. قوي، فاخر، لا يُنسى."),
            ("مقدمة قناة", "أهلاً وسهلاً بكم في قناة مهووس — وجهتك الأولى لعالم العطور الفاخرة والتجارب الحسية الاستثنائية."),
        ]
        for label, text in examples:
            if st.button(f"📝 {label}", key=f"ex_{label}"):
                st.session_state["_tts_text"] = text
                st.rerun()
        if "_tts_text" in st.session_state:
            tts_text = st.session_state.pop("_tts_text")

        if st.button("🎙️ توليد الصوت", type="primary", use_container_width=True):
            if not tts_text.strip():
                st.warning("أدخل النص أولاً")
            elif not st.session_state.gemini_key:
                st.error("❌ أدخل مفتاح Gemini")
            else:
                with st.spinner("🎙️ Gemini يولّد الصوت..."):
                    try:
                        from modules.gemini_engine import gemini_tts, pcm_to_wav
                        pcm_bytes = gemini_tts(tts_text, voice_choice)
                        wav_bytes  = pcm_to_wav(pcm_bytes)
                        st.session_state.last_audio = wav_bytes
                        st.session_state.gen_count += 1
                        st.success("✅ تم! استمع إلى الصوت")
                    except Exception as e:
                        st.error(f"❌ {e}")

    with R:
        st.markdown("**الصوت المُولَّد:**")
        if st.session_state.last_audio:
            st.audio(st.session_state.last_audio, format="audio/wav")
            st.download_button(
                "⬇️ تحميل (WAV)",
                data=st.session_state.last_audio,
                file_name=f"mahwous_tts_{datetime.now().strftime('%H%M')}.wav",
                mime="audio/wav"
            )
            st.markdown("""
            <div class='card' style='font-size:.82rem;color:rgba(150,180,255,.6)'>
            💡 لتحويل WAV إلى MP3 استخدم أي موقع مجاني مثل:<br>
            <a href='https://cloudconvert.com/wav-to-mp3' target='_blank' style='color:#6EB4FF'>
            cloudconvert.com/wav-to-mp3
            </a>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='border:2px dashed rgba(100,160,255,.10);border-radius:1rem;
            padding:60px;text-align:center;opacity:.3'>
            <div style='font-size:3rem'>🎙️</div>
            <div style='margin-top:8px'>الصوت يظهر هنا</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='card' style='margin-top:1rem'>
          <strong style='color:#6EB4FF'>🎙️ الأصوات المتاحة:</strong><br><br>
          <span class='tag'>Kore — هادئ واحترافي</span>
          <span class='tag'>Charon — عميق وقوي</span>
          <span class='tag'>Puck — خفيف وودود</span><br>
          <span class='tag'>Fenrir — جريء</span>
          <span class='tag'>Aoede — ناعم</span>
          <span class='tag'>Leda — أنثوي</span>
          <span class='tag'>Orus — ذكوري رسمي</span><br><br>
          <span style='font-size:.75rem;color:rgba(150,180,255,.5)'>
          ✅ جميع الأصوات تدعم العربية والإنجليزية
          </span>
        </div>""", unsafe_allow_html=True)


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 .5rem;opacity:.2;font-size:.6rem;letter-spacing:.3em'>
MAHWOUS GEMINI ALL-IN-ONE STUDIO · 2026 · ONE KEY TO RULE THEM ALL
</div>""", unsafe_allow_html=True)
