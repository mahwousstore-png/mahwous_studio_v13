"""
🎬 مهووس AI Studio v14.0 — التطبيق الرئيسي
Gemini 2.0 Flash + Imagen 4.0 + Fal.ai (Kling 2.1 / Hailuo / Flux) + Luma Ray-2 + RunwayML
"""

import streamlit as st

st.set_page_config(
    page_title="مهووس AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "مهووس AI Studio v14.0 — توليد الصور والفيديوهات بالذكاء الاصطناعي"}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
html,body,[class*="css"]{font-family:'Cairo','Segoe UI',sans-serif!important;direction:rtl}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0D0800 0%,#1A1000 50%,#0D0800 100%)!important;border-left:2px solid rgba(212,175,55,.30)!important}
[data-testid="stSidebar"] *{color:#D4B870!important}
.stApp{background:#0A0600!important}
.stButton>button{background:linear-gradient(135deg,#2A1A04,#3A2208)!important;border:1.5px solid rgba(212,175,55,.55)!important;color:#FFE060!important;border-radius:.6rem!important;font-weight:800!important;font-family:'Cairo',sans-serif!important;transition:all .2s!important}
.stButton>button:hover{background:linear-gradient(135deg,#3A2208,#4A3010)!important;border-color:#F0CC55!important;box-shadow:0 0 16px rgba(212,175,55,.25)!important;transform:translateY(-1px)!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#B8860B,#D4A017,#B8860B)!important;color:#0A0600!important;border-color:#FFD700!important}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,[data-baseweb="select"]>div{background:#1A1006!important;color:#F0D880!important;border:1.5px solid rgba(212,175,55,.35)!important;border-radius:.5rem!important}
.stTabs [data-baseweb="tab-list"]{background:#1A1006!important;border-bottom:2px solid rgba(212,175,55,.30)!important}
.stTabs [data-baseweb="tab"]{color:#906030!important;font-weight:700!important}
.stTabs [aria-selected="true"]{background:rgba(212,175,55,.15)!important;color:#FFE060!important;border-bottom:3px solid #F0CC55!important}
[data-testid="stMetric"]{background:#1A1006!important;border:1.5px solid rgba(212,175,55,.30)!important;border-radius:.6rem!important;padding:.8rem!important}
[data-testid="stMetricValue"]{color:#FFE060!important;font-weight:900!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#B8860B,#FFD700)!important}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:#0D0800}::-webkit-scrollbar-thumb{background:rgba(212,175,55,.40);border-radius:3px}
.stAlert{border-radius:.65rem!important;font-weight:700!important}
div[data-testid="stInfo"]{background:rgba(59,130,246,.12)!important;border-color:#3b82f6!important}
div[data-testid="stWarning"]{background:rgba(251,191,36,.12)!important;border-color:#fbbf24!important}
div[data-testid="stSuccess"]{background:rgba(52,211,153,.12)!important;border-color:#34d399!important}
div[data-testid="stError"]{background:rgba(239,68,68,.12)!important;border-color:#ef4444!important}
hr{border-color:rgba(212,175,55,.20)!important}
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem .5rem 1rem">
          <div style="font-size:2.8rem">🎬</div>
          <div style="color:#FFE060;font-size:1.3rem;font-weight:900;margin:.3rem 0">مهووس AI Studio</div>
          <div style="color:#906030;font-size:.72rem;font-weight:700">v14.0 · Kling 2.1 + Gemini + Fal.ai</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        nav_items = [
            ("🎬", "الاستديو الإبداعي", "studio"),
            ("⚙️", "إعدادات API",        "settings"),
            ("📊", "الإحصائيات",         "stats"),
            ("❓", "المساعدة",           "help"),
        ]
        if "current_page" not in st.session_state:
            st.session_state.current_page = "studio"

        for icon, label, page_key in nav_items:
            is_active = st.session_state.current_page == page_key
            if st.button(f"{icon}  {label}", use_container_width=True,
                         type="primary" if is_active else "secondary",
                         key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")
        from modules.ai_engine import _get_secrets, check_api_health
        secrets = _get_secrets()

        st.markdown("<div style='color:#906030;font-size:.85rem;font-weight:700;margin-bottom:.4rem'>📡 حالة النظام</div>",
                    unsafe_allow_html=True)
        if st.button("🔄 فحص الاتصال", key="check_health_btn", use_container_width=True):
            with st.spinner("جاري الفحص..."):
                st.session_state.api_health = check_api_health()

        health = st.session_state.get("api_health", {})
        def _status_row(label, key_name, icon):
            is_set = bool(secrets.get(key_name))
            if health and key_name in health:
                is_ok = health[key_name]["ok"]
                color = "#34d399" if is_ok else "#ef4444"
                status_icon = "🟢" if is_ok else "🔴"
            else:
                color = "#90D870" if is_set else "#707070"
                status_icon = "🟢" if is_set else "⚪"
            st.markdown(
                f"<div style='font-size:.75rem;margin-bottom:4px;display:flex;justify-content:space-between;"
                f"align-items:center;background:rgba(255,255,255,.03);padding:4px 8px;border-radius:4px'>"
                f"<span>{icon} {label}</span>"
                f"<span style='color:{color};font-weight:bold'>{status_icon}</span></div>",
                unsafe_allow_html=True)

        _status_row("Gemini AI",    "gemini",     "🧠")
        _status_row("Fal.ai",       "fal",        "⚡")
        _status_row("Luma Video",   "luma",       "🎬")
        _status_row("RunwayML",     "runway",     "🎥")
        _status_row("Claude 3.5",   "openrouter", "✍️")
        _status_row("ElevenLabs",   "elevenlabs", "🎙️")

        st.markdown("---")
        gen_count = st.session_state.get("gen_count", 0)
        st.markdown(f"""
        <div style='background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.20);
             border-radius:.6rem;padding:.7rem;text-align:center'>
          <div style='color:#FFE060;font-size:1.4rem;font-weight:900'>{gen_count}</div>
          <div style='color:#906030;font-size:.72rem;font-weight:700'>توليد في هذه الجلسة</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🗑️ مسح الجلسة", use_container_width=True, key="clear_session"):
            keys_keep = ["current_page","openrouter_key","gemini_key","luma_key","runway_key",
                         "webhook_url","fal_key","imgbb_key","elevenlabs_key","supabase_url","supabase_key"]
            for k in list(st.session_state.keys()):
                if k not in keys_keep:
                    del st.session_state[k]
            st.rerun()


def show_settings_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,.50);border-radius:1.2rem;
         padding:2rem;text-align:center;margin-bottom:2rem">
      <div style="font-size:2.5rem">⚙️</div>
      <div style="color:#FFE060;font-size:1.8rem;font-weight:900;margin:.5rem 0">إعدادات API</div>
      <div style="color:#906030;font-size:.9rem">أدخل مفاتيح API لتفعيل جميع ميزات التوليد</div>
    </div>""", unsafe_allow_html=True)

    # ── Gemini + Imagen ──────────────────────────────────────────────
    with st.expander("🧠 Google Gemini + Imagen 4.0 (تحليل + توليد الصور)", expanded=True):
        st.markdown("""<div style='background:rgba(66,133,244,.10);border:1.5px solid rgba(66,133,244,.40);
             border-radius:.6rem;padding:.8rem;margin-bottom:.8rem;color:#A0C0FF;font-size:.85rem'>
        🔑 <strong>للحصول على المفتاح:</strong>
        اذهب إلى <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#80AFFF">aistudio.google.com</a>
        ← انقر "Create API Key" — المفتاح يبدأ بـ <code>AIzaSy...</code>
        </div>""", unsafe_allow_html=True)
        gemini_key = st.text_input("GEMINI_API_KEY", value=st.session_state.get("gemini_key",""),
                                    type="password", placeholder="AIzaSy...", key="gemini_key_input")
        c1,c2 = st.columns(2)
        with c1:
            if st.button("💾 حفظ مفتاح Gemini", use_container_width=True, key="save_gemini"):
                st.session_state.gemini_key = gemini_key; st.success("✅ تم الحفظ!")
        with c2:
            if st.button("🧪 اختبار Gemini", use_container_width=True, key="test_gemini"):
                if not gemini_key: st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests as rq
                            r = rq.post(
                                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                                json={"contents":[{"parts":[{"text":"Say: OK"}]}]}, timeout=15)
                            if r.status_code == 200:
                                st.success("✅ Gemini يعمل!"); st.session_state.gemini_key = gemini_key
                            else: st.error(f"❌ خطأ {r.status_code}")
                        except Exception as e: st.error(f"❌ {e}")

    # ── Fal.ai ────────────────────────────────────────────────────────
    with st.expander("⚡ Fal.ai — Flux (صور) + Kling 2.1 + Hailuo (فيديو) ⭐ الأهم", expanded=True):
        st.markdown("""<div style='background:rgba(255,165,0,.10);border:1.5px solid rgba(255,165,0,.40);
             border-radius:.6rem;padding:.8rem;margin-bottom:.8rem;color:#FFD080;font-size:.85rem'>
        ⭐ <strong>الأولوية الأولى — يشمل الصور والفيديو بمفتاح واحد!</strong><br>
        🔑 اذهب إلى <a href="https://fal.ai/dashboard/keys" target="_blank" style="color:#FFB060">fal.ai/dashboard/keys</a>
        ← انقر "Create API Key"<br>
        💰 ابدأ بـ <strong>$20</strong> على <a href="https://fal.ai/dashboard/billing" target="_blank" style="color:#FFB060">fal.ai/dashboard/billing</a>
        </div>""", unsafe_allow_html=True)
        fal_key = st.text_input("FAL_API_KEY", value=st.session_state.get("fal_key",""),
                                 type="password", placeholder="YOUR_FAL_KEY", key="fal_key_input")
        if st.button("💾 حفظ مفتاح Fal.ai", use_container_width=True, key="save_fal"):
            st.session_state.fal_key = fal_key; st.success("✅ تم الحفظ!")

    # ── Luma ─────────────────────────────────────────────────────────
    with st.expander("🌙 Luma Dream Machine Ray-2 (فيديو سينمائي)"):
        st.markdown("""<div style='background:rgba(52,211,153,.10);border:1.5px solid rgba(52,211,153,.40);
             border-radius:.6rem;padding:.8rem;margin-bottom:.8rem;color:#A0FFD8;font-size:.85rem'>
        🔑 اذهب إلى <a href="https://lumalabs.ai/dream-machine/api" target="_blank" style="color:#80FFD0">lumalabs.ai</a>
        ← API ← Create API Key
        </div>""", unsafe_allow_html=True)
        luma_key = st.text_input("LUMA_API_KEY", value=st.session_state.get("luma_key",""),
                                  type="password", placeholder="luma-...", key="luma_key_input")
        c1,c2 = st.columns(2)
        with c1:
            if st.button("💾 حفظ مفتاح Luma", use_container_width=True, key="save_luma"):
                st.session_state.luma_key = luma_key; st.success("✅ تم الحفظ!")
        with c2:
            if st.button("🧪 اختبار Luma", use_container_width=True, key="test_luma"):
                if not luma_key: st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests as rq
                            r = rq.get("https://api.lumalabs.ai/dream-machine/v1/generations",
                                       headers={"Authorization": f"Bearer {luma_key}"}, timeout=15)
                            if r.status_code in [200,201]:
                                st.success("✅ Luma يعمل!"); st.session_state.luma_key = luma_key
                            elif r.status_code == 401: st.error("❌ مفتاح غير صحيح")
                            else: st.warning(f"⚠️ استجابة {r.status_code}"); st.session_state.luma_key = luma_key
                        except Exception as e: st.error(f"❌ {e}")

    # ── RunwayML ──────────────────────────────────────────────────────
    with st.expander("🎥 RunwayML Gen-4 Turbo (فيديو — بديل Luma)"):
        runway_key = st.text_input("RUNWAY_API_KEY", value=st.session_state.get("runway_key",""),
                                    type="password", placeholder="key_...", key="runway_key_input")
        if st.button("💾 حفظ مفتاح RunwayML", use_container_width=True, key="save_runway"):
            st.session_state.runway_key = runway_key; st.success("✅ تم الحفظ!")

    # ── OpenRouter ────────────────────────────────────────────────────
    with st.expander("✍️ OpenRouter / Claude 3.5 (توليد النصوص)"):
        openrouter_key = st.text_input("OPENROUTER_API_KEY", value=st.session_state.get("openrouter_key",""),
                                        type="password", placeholder="sk-or-v1-...", key="openrouter_key_input")
        if st.button("💾 حفظ مفتاح OpenRouter", use_container_width=True, key="save_openrouter"):
            st.session_state.openrouter_key = openrouter_key; st.success("✅ تم الحفظ!")

    # ── ElevenLabs ────────────────────────────────────────────────────
    with st.expander("🎙️ ElevenLabs (صوت عربي خليجي)"):
        st.markdown("""<div style='background:rgba(120,80,220,.10);border:1.5px solid rgba(120,80,220,.40);
             border-radius:.6rem;padding:.8rem;margin-bottom:.8rem;color:#C0A0FF;font-size:.85rem'>
        🔑 اذهب إلى <a href="https://elevenlabs.io/pricing" target="_blank" style="color:#B090FF">elevenlabs.io</a>
        ← Starter $5/شهر — يشمل الصوت العربي الخليجي واستنساخ الصوت
        </div>""", unsafe_allow_html=True)
        elevenlabs_key = st.text_input("ELEVENLABS_API_KEY", value=st.session_state.get("elevenlabs_key",""),
                                        type="password", placeholder="YOUR_KEY", key="elevenlabs_key_input")
        if st.button("💾 حفظ مفتاح ElevenLabs", use_container_width=True, key="save_elevenlabs"):
            st.session_state.elevenlabs_key = elevenlabs_key; st.success("✅ تم الحفظ!")

    # ── ImgBB ─────────────────────────────────────────────────────────
    with st.expander("🖼 ImgBB (رفع الصور للفيديو المرجعي)"):
        imgbb_key = st.text_input("IMGBB_API_KEY", value=st.session_state.get("imgbb_key",""),
                                   type="password", placeholder="YOUR_KEY", key="imgbb_key_input")
        if st.button("💾 حفظ مفتاح ImgBB", use_container_width=True, key="save_imgbb"):
            st.session_state.imgbb_key = imgbb_key; st.success("✅ تم الحفظ!")

    # ── Webhook ───────────────────────────────────────────────────────
    with st.expander("🔗 Make.com Webhook (نشر تلقائي — اختياري)"):
        webhook_url = st.text_input("WEBHOOK_URL", value=st.session_state.get("webhook_url",""),
                                     placeholder="https://hook.eu1.make.com/...", key="webhook_url_input")
        if st.button("💾 حفظ Webhook", use_container_width=True, key="save_webhook"):
            st.session_state.webhook_url = webhook_url; st.success("✅ تم الحفظ!")

    # ── Supabase ──────────────────────────────────────────────────────
    with st.expander("🗄️ Supabase (قاعدة بيانات — اختياري)"):
        su = st.text_input("SUPABASE_URL", value=st.session_state.get("supabase_url",""),
                            placeholder="https://your-project.supabase.co", key="supabase_url_input")
        sk = st.text_input("SUPABASE_KEY", value=st.session_state.get("supabase_key",""),
                            type="password", placeholder="YOUR_KEY", key="supabase_key_input")
        if st.button("💾 حفظ Supabase", use_container_width=True, key="save_supabase"):
            st.session_state.supabase_url = su; st.session_state.supabase_key = sk; st.success("✅ تم الحفظ!")

    st.markdown("---")
    if st.button("💾 حفظ جميع الإعدادات", type="primary", use_container_width=True, key="save_all"):
        for attr,key in [("gemini_key","gemini_key_input"),("openrouter_key","openrouter_key_input"),
                          ("luma_key","luma_key_input"),("runway_key","runway_key_input"),
                          ("fal_key","fal_key_input"),("imgbb_key","imgbb_key_input"),
                          ("elevenlabs_key","elevenlabs_key_input"),("webhook_url","webhook_url_input"),
                          ("supabase_url","supabase_url_input"),("supabase_key","supabase_key_input")]:
            val = st.session_state.get(key,"")
            if val: st.session_state[attr] = val
        st.success("✅ تم حفظ جميع الإعدادات!")
        st.balloons()

    st.markdown("""
    <div style='background:rgba(251,191,36,.10);border:1.5px solid rgba(251,191,36,.40);
         border-radius:.6rem;padding:.8rem;margin-top:1rem;color:#FFE880;font-size:.82rem'>
    🔒 <strong>الأمان:</strong> المفاتيح محفوظة في جلسة المتصفح فقط — لا تُشارك الكود وبه مفاتيح.<br>
    للحفظ الدائم أضفها في <code>.streamlit/secrets.toml</code>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 نموذج secrets.toml"):
        st.code("""# .streamlit/secrets.toml
GEMINI_API_KEY    = "AIzaSy..."
FAL_API_KEY       = "YOUR_FAL_KEY"
LUMA_API_KEY      = "luma-..."
RUNWAY_API_KEY    = "key_..."
OPENROUTER_API_KEY= "sk-or-v1-..."
ELEVENLABS_API_KEY= "YOUR_KEY"
IMGBB_API_KEY     = "YOUR_KEY"
MAKE_WEBHOOK_URL  = "https://hook..."
SUPABASE_URL      = "https://..."
SUPABASE_KEY      = "YOUR_KEY"
""", language="toml")


def show_stats_page():
    st.markdown("""<div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,.50);border-radius:1.2rem;
         padding:2rem;text-align:center;margin-bottom:2rem">
      <div style="font-size:2.5rem">📊</div>
      <div style="color:#FFE060;font-size:1.8rem;font-weight:900;margin:.5rem 0">إحصائيات الجلسة</div>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🎨 عمليات التوليد", st.session_state.get("gen_count",0))
    c2.metric("🖼️ الصور المولدة", len(st.session_state.get("generated_images",{})))
    c3.metric("✍️ التعليقات", "✅" if "captions_data" in st.session_state else "—")
    c4.metric("🎬 الفيديو", "✅" if st.session_state.get("video_url_ready") else "—")


def show_help_page():
    st.markdown("""<div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,.50);border-radius:1.2rem;
         padding:2rem;text-align:center;margin-bottom:2rem">
      <div style="font-size:2.5rem">❓</div>
      <div style="color:#FFE060;font-size:1.8rem;font-weight:900;margin:.5rem 0">دليل الاستخدام</div>
    </div>""", unsafe_allow_html=True)

    with st.expander("🚀 البدء السريع", expanded=True):
        st.markdown("""<div style='color:#D0B070;font-size:.9rem;line-height:2.2'>
        <strong style='color:#FFE060'>الخطوات:</strong><br>
        1️⃣ اذهب إلى <strong>إعدادات API</strong> وأدخل مفاتيحك (الأولوية: FAL_API_KEY + GEMINI_API_KEY)<br>
        2️⃣ ارجع إلى <strong>الاستديو الإبداعي</strong><br>
        3️⃣ ارفع صورة العطر أو أدخل البيانات يدوياً<br>
        4️⃣ اختر المنصات واضغط <strong>"توليد الصور الآن"</strong><br>
        5️⃣ لتوليد فيديو: انتقل إلى تبويب <strong>"توليد الفيديو"</strong><br>
        6️⃣ اختر المزود: Kling 2.1 (الأفضل) أو Luma أو RunwayML
        </div>""", unsafe_allow_html=True)

    with st.expander("🖼️ توليد الصور"):
        st.markdown("""<div style='color:#D0B070;font-size:.88rem;line-height:2'>
        • <strong>المزود الأول:</strong> Fal.ai Flux Dev (يتطلب FAL_API_KEY) — موثوق ومجرّب<br>
        • <strong>المزود الثاني:</strong> Imagen 4.0 (يتطلب GEMINI_API_KEY + تفعيل الفوترة في Google Cloud)<br>
        • <strong>Fallback تلقائي:</strong> إذا فشل مزود ينتقل للتالي تلقائياً<br>
        • 10 منصات: Instagram, TikTok, YouTube, Snapchat, Twitter, Facebook, LinkedIn, Pinterest
        </div>""", unsafe_allow_html=True)

    with st.expander("🎬 توليد الفيديو"):
        st.markdown("""<div style='color:#D0B070;font-size:.88rem;line-height:2'>
        • <strong>⭐ Kling 2.1</strong> — الأفضل للشخصيات 3D، 1080p، يتطلب FAL_API_KEY<br>
        • <strong>🎭 Hailuo</strong> — مشاهد درامية، يتطلب FAL_API_KEY<br>
        • <strong>🌱 Seedance</strong> — مشاهد متعددة، يتطلب FAL_API_KEY<br>
        • <strong>🌙 Luma Ray-2</strong> — يتطلب LUMA_API_KEY، 5s أو 9s فقط<br>
        • <strong>🎥 RunwayML Gen-4</strong> — يتطلب RUNWAY_API_KEY
        </div>""", unsafe_allow_html=True)

    with st.expander("💰 تقدير التكاليف"):
        st.markdown("""
        | الخدمة | التكلفة |
        |--------|---------|
        | Fal.ai Flux (صورة) | ~$0.003 |
        | Fal.ai Kling 2.1 (فيديو 5s) | ~$0.70 |
        | Fal.ai Hailuo (فيديو) | ~$0.10 |
        | Luma Ray-2 (فيديو 5s) | ~$0.50 |
        | Gemini (تحليل) | مجاني إلى حد كبير |
        | ElevenLabs Starter | $5/شهر |
        """)


def main():
    render_sidebar()
    page = st.session_state.get("current_page","studio")
    if page == "studio":
        from modules.studio import show_studio_page
        show_studio_page()
    elif page == "settings":
        show_settings_page()
    elif page == "stats":
        show_stats_page()
    elif page == "help":
        show_help_page()


if __name__ == "__main__":
    main()
