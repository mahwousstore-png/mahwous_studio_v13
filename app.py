"""
🎬 مهووس AI Studio v13.0 — التطبيق الرئيسي
توليد الصور والفيديوهات مباشرة من التطبيق
Gemini 2.0 Flash + Imagen 3 + Claude 3.5 + Luma Dream Machine + RunwayML Gen-3
"""

import streamlit as st

st.set_page_config(
    page_title="مهووس AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://mahwousstore.com",
        "About": "مهووس AI Studio v13.0 — توليد الصور والفيديوهات بالذكاء الاصطناعي"
    }
)

# ─── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', 'Segoe UI', sans-serif !important;
    direction: rtl;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0800 0%, #1A1000 50%, #0D0800 100%) !important;
    border-left: 2px solid rgba(212,175,55,0.30) !important;
}
[data-testid="stSidebar"] * { color: #D4B870 !important; }

/* Main background */
.stApp { background: #0A0600 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2A1A04, #3A2208) !important;
    border: 1.5px solid rgba(212,175,55,0.55) !important;
    color: #FFE060 !important; border-radius: 0.6rem !important;
    font-weight: 800 !important; font-family: 'Cairo', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3A2208, #4A3010) !important;
    border-color: #F0CC55 !important;
    box-shadow: 0 0 16px rgba(212,175,55,0.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #B8860B, #D4A017, #B8860B) !important;
    color: #0A0600 !important; border-color: #FFD700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #D4A017, #FFD700, #D4A017) !important;
    box-shadow: 0 0 24px rgba(212,175,55,0.45) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #1A1006 !important; color: #F0D880 !important;
    border: 1.5px solid rgba(212,175,55,0.35) !important;
    border-radius: 0.5rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1A1006 !important;
    border-bottom: 2px solid rgba(212,175,55,0.30) !important;
    gap: 0.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    color: #906030 !important; font-weight: 700 !important;
    border-radius: 0.4rem 0.4rem 0 0 !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(212,175,55,0.15) !important;
    color: #FFE060 !important;
    border-bottom: 3px solid #F0CC55 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1A1006 !important; color: #D4B870 !important;
    border: 1px solid rgba(212,175,55,0.25) !important;
    border-radius: 0.5rem !important; font-weight: 700 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #1A1006 !important; border: 1.5px solid rgba(212,175,55,0.30) !important;
    border-radius: 0.6rem !important; padding: 0.8rem !important;
}
[data-testid="stMetricValue"] { color: #FFE060 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #906030 !important; }

/* Progress */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #B8860B, #FFD700) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D0800; }
::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.40); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(212,175,55,0.65); }

/* Info/Warning/Error */
.stAlert { border-radius: 0.65rem !important; font-weight: 700 !important; }
div[data-testid="stInfo"] { background: rgba(59,130,246,0.12) !important; border-color: #3b82f6 !important; }
div[data-testid="stWarning"] { background: rgba(251,191,36,0.12) !important; border-color: #fbbf24 !important; }
div[data-testid="stSuccess"] { background: rgba(52,211,153,0.12) !important; border-color: #34d399 !important; }
div[data-testid="stError"] { background: rgba(239,68,68,0.12) !important; border-color: #ef4444 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1A1006 !important; border: 2px dashed rgba(212,175,55,0.40) !important;
    border-radius: 0.8rem !important;
}

/* Divider */
hr { border-color: rgba(212,175,55,0.20) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="text-align:center; padding:1.5rem 0.5rem 1rem;">
          <div style="font-size:2.8rem;">🎬</div>
          <div style="color:#FFE060; font-size:1.3rem; font-weight:900; margin:0.3rem 0;">مهووس AI Studio</div>
          <div style="color:#906030; font-size:0.72rem; font-weight:700;">v13.0 · Powered by Gemini + Claude</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        nav_items = [
            ("🎬", "الاستديو الإبداعي", "studio"),
            ("⚙️", "إعدادات API", "settings"),
            ("📊", "الإحصائيات", "stats"),
            ("❓", "المساعدة", "help"),
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "studio"

        for icon, label, page_key in nav_items:
            is_active = st.session_state.current_page == page_key
            if st.button(
                f"{icon}  {label}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"nav_{page_key}"
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # API Status Quick View
        from modules.ai_engine import _get_secrets
        secrets = _get_secrets()

        st.markdown("<div style='color:#906030; font-size:0.75rem; font-weight:700; margin-bottom:0.4rem;'>حالة الاتصال</div>", unsafe_allow_html=True)

        api_list = [
            ("Gemini + Imagen 3", secrets["gemini"], "🖼️"),
            ("OpenRouter / Claude", secrets["openrouter"], "🤖"),
            ("Luma Dream Machine", secrets["luma"], "🎬"),
            ("RunwayML Gen-3", secrets["runway"], "🎥"),
        ]

        for name, key, icon in api_list:
            status = "🟢" if key else "🔴"
            st.markdown(
                f"<div style='font-size:0.78rem; padding:0.2rem 0; color:{'#90D870' if key else '#F06060'};'>"
                f"{status} {icon} {name}</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Stats
        gen_count = st.session_state.get("gen_count", 0)
        st.markdown(f"""
        <div style='background:rgba(212,175,55,0.08); border:1px solid rgba(212,175,55,0.20);
             border-radius:0.6rem; padding:0.7rem; text-align:center;'>
          <div style='color:#FFE060; font-size:1.4rem; font-weight:900;'>{gen_count}</div>
          <div style='color:#906030; font-size:0.72rem; font-weight:700;'>توليد في هذه الجلسة</div>
        </div>
        """, unsafe_allow_html=True)

        # Clear session
        if st.button("🗑️ مسح الجلسة", use_container_width=True, key="clear_session"):
            keys_to_keep = ["current_page", "openrouter_key", "gemini_key", "luma_key", "runway_key", "webhook_url"]
            for k in list(st.session_state.keys()):
                if k not in keys_to_keep:
                    del st.session_state[k]
            st.rerun()


# ─── Settings Page ────────────────────────────────────────────────────────────
def show_settings_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,0.50); border-radius:1.2rem;
         padding:2rem; text-align:center; margin-bottom:2rem;">
      <div style="font-size:2.5rem;">⚙️</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">إعدادات API</div>
      <div style="color:#906030; font-size:0.9rem;">أدخل مفاتيح API لتفعيل جميع ميزات التوليد</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Gemini ──────────────────────────────────────────────────────────────
    with st.expander("🖼️ Google Gemini + Imagen 3 (توليد الصور + تحليل العطور)", expanded=True):
        st.markdown("""
        <div style='background:rgba(66,133,244,0.10); border:1.5px solid rgba(66,133,244,0.40);
             border-radius:0.6rem; padding:0.8rem; margin-bottom:0.8rem; color:#A0C0FF; font-size:0.85rem;'>
        <strong>🔑 كيف تحصل على المفتاح:</strong><br>
        1. افتح <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#80AFFF;">aistudio.google.com</a><br>
        2. انقر "Create API Key" → انسخ المفتاح<br>
        3. المفتاح يبدأ بـ <code>AIzaSy...</code>
        </div>
        """, unsafe_allow_html=True)

        gemini_key = st.text_input(
            "GEMINI_API_KEY",
            value=st.session_state.get("gemini_key", ""),
            type="password",
            placeholder="AIzaSy...",
            key="gemini_key_input",
            help="يُستخدم لتحليل صور العطور وتوليد الصور بـ Imagen 3"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ مفتاح Gemini", use_container_width=True, key="save_gemini"):
                st.session_state.gemini_key = gemini_key
                st.success("✅ تم حفظ مفتاح Gemini!")
        with col2:
            if st.button("🧪 اختبار مفتاح Gemini", use_container_width=True, key="test_gemini"):
                if not gemini_key:
                    st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests
                            r = requests.post(
                                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                                headers={"Content-Type": "application/json", "x-goog-api-key": gemini_key},
                                json={"contents": [{"parts": [{"text": "Say: OK"}]}]},
                                timeout=15
                            )
                            if r.status_code == 200:
                                st.success("✅ Gemini API يعمل بشكل صحيح!")
                                st.session_state.gemini_key = gemini_key
                            else:
                                st.error(f"❌ خطأ {r.status_code}: {r.json().get('error', {}).get('message', '')}")
                        except Exception as e:
                            st.error(f"❌ فشل الاتصال: {e}")

    # ── OpenRouter ──────────────────────────────────────────────────────────
    with st.expander("🤖 OpenRouter / Claude 3.5 (توليد النصوص والتعليقات)"):
        st.markdown("""
        <div style='background:rgba(120,80,220,0.10); border:1.5px solid rgba(120,80,220,0.40);
             border-radius:0.6rem; padding:0.8rem; margin-bottom:0.8rem; color:#C0A0FF; font-size:0.85rem;'>
        <strong>🔑 كيف تحصل على المفتاح:</strong><br>
        1. افتح <a href="https://openrouter.ai/keys" target="_blank" style="color:#B090FF;">openrouter.ai/keys</a><br>
        2. انقر "Create Key" → انسخ المفتاح<br>
        3. المفتاح يبدأ بـ <code>sk-or-v1-...</code>
        </div>
        """, unsafe_allow_html=True)

        openrouter_key = st.text_input(
            "OPENROUTER_API_KEY",
            value=st.session_state.get("openrouter_key", ""),
            type="password",
            placeholder="sk-or-v1-...",
            key="openrouter_key_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ مفتاح OpenRouter", use_container_width=True, key="save_openrouter"):
                st.session_state.openrouter_key = openrouter_key
                st.success("✅ تم حفظ مفتاح OpenRouter!")
        with col2:
            if st.button("🧪 اختبار OpenRouter", use_container_width=True, key="test_openrouter"):
                if not openrouter_key:
                    st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests
                            r = requests.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {openrouter_key}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": "anthropic/claude-3.5-sonnet",
                                    "messages": [{"role": "user", "content": "Say: OK"}],
                                    "max_tokens": 10
                                },
                                timeout=20
                            )
                            if r.status_code == 200:
                                st.success("✅ OpenRouter يعمل بشكل صحيح!")
                                st.session_state.openrouter_key = openrouter_key
                            else:
                                st.error(f"❌ خطأ {r.status_code}: {r.text[:200]}")
                        except Exception as e:
                            st.error(f"❌ فشل الاتصال: {e}")

    # ── Luma Dream Machine ──────────────────────────────────────────────────
    with st.expander("🎬 Luma Dream Machine (توليد الفيديو — الأفضل)"):
        st.markdown("""
        <div style='background:rgba(52,211,153,0.10); border:1.5px solid rgba(52,211,153,0.40);
             border-radius:0.6rem; padding:0.8rem; margin-bottom:0.8rem; color:#A0FFD8; font-size:0.85rem;'>
        <strong>🔑 كيف تحصل على المفتاح:</strong><br>
        1. افتح <a href="https://lumalabs.ai/dream-machine/api" target="_blank" style="color:#80FFD0;">lumalabs.ai</a><br>
        2. سجّل حساباً → API → Create API Key<br>
        3. المفتاح يبدأ بـ <code>luma-...</code> أو UUID
        </div>
        """, unsafe_allow_html=True)

        luma_key = st.text_input(
            "LUMA_API_KEY",
            value=st.session_state.get("luma_key", ""),
            type="password",
            placeholder="luma-... أو UUID",
            key="luma_key_input",
            help="يُستخدم لتوليد الفيديو بـ Luma Dream Machine"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ مفتاح Luma", use_container_width=True, key="save_luma"):
                st.session_state.luma_key = luma_key
                st.success("✅ تم حفظ مفتاح Luma!")
        with col2:
            if st.button("🧪 اختبار Luma", use_container_width=True, key="test_luma"):
                if not luma_key:
                    st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests
                            r = requests.get(
                                "https://api.lumalabs.ai/dream-machine/v1/generations",
                                headers={"Authorization": f"Bearer {luma_key}", "Accept": "application/json"},
                                timeout=15
                            )
                            if r.status_code in [200, 201]:
                                st.success("✅ Luma API يعمل بشكل صحيح!")
                                st.session_state.luma_key = luma_key
                            elif r.status_code == 401:
                                st.error("❌ مفتاح غير صحيح")
                            else:
                                st.warning(f"⚠️ استجابة غير متوقعة {r.status_code} — قد يكون المفتاح صحيحاً")
                                st.session_state.luma_key = luma_key
                        except Exception as e:
                            st.error(f"❌ فشل الاتصال: {e}")

    # ── RunwayML ────────────────────────────────────────────────────────────
    with st.expander("🎥 RunwayML Gen-3 Alpha Turbo (توليد الفيديو — بديل)"):
        st.markdown("""
        <div style='background:rgba(239,68,68,0.10); border:1.5px solid rgba(239,68,68,0.40);
             border-radius:0.6rem; padding:0.8rem; margin-bottom:0.8rem; color:#FFB0B0; font-size:0.85rem;'>
        <strong>🔑 كيف تحصل على المفتاح:</strong><br>
        1. افتح <a href="https://app.runwayml.com/settings/api-keys" target="_blank" style="color:#FF9090;">app.runwayml.com</a><br>
        2. انقر "Generate Token" → انسخ المفتاح<br>
        3. المفتاح يبدأ بـ <code>key_...</code>
        </div>
        """, unsafe_allow_html=True)

        runway_key = st.text_input(
            "RUNWAY_API_KEY",
            value=st.session_state.get("runway_key", ""),
            type="password",
            placeholder="key_...",
            key="runway_key_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ مفتاح RunwayML", use_container_width=True, key="save_runway"):
                st.session_state.runway_key = runway_key
                st.success("✅ تم حفظ مفتاح RunwayML!")
        with col2:
            if st.button("🧪 اختبار RunwayML", use_container_width=True, key="test_runway"):
                if not runway_key:
                    st.error("❌ أدخل المفتاح أولاً")
                else:
                    with st.spinner("جاري الاختبار..."):
                        try:
                            import requests
                            r = requests.get(
                                "https://api.dev.runwayml.com/v1/tasks",
                                headers={
                                    "Authorization": f"Bearer {runway_key}",
                                    "X-Runway-Version": "2024-11-06"
                                },
                                timeout=15
                            )
                            if r.status_code in [200, 201]:
                                st.success("✅ RunwayML API يعمل بشكل صحيح!")
                                st.session_state.runway_key = runway_key
                            elif r.status_code == 401:
                                st.error("❌ مفتاح غير صحيح")
                            else:
                                st.warning(f"⚠️ استجابة {r.status_code}")
                                st.session_state.runway_key = runway_key
                        except Exception as e:
                            st.error(f"❌ فشل الاتصال: {e}")

    # ── Webhook ──────────────────────────────────────────────────────────────
    with st.expander("🔗 Make.com Webhook (نشر المحتوى التلقائي — اختياري)"):
        webhook_url = st.text_input(
            "WEBHOOK_PUBLISH_CONTENT",
            value=st.session_state.get("webhook_url", ""),
            placeholder="https://hook.eu1.make.com/...",
            key="webhook_url_input"
        )
        if st.button("💾 حفظ Webhook", use_container_width=True, key="save_webhook"):
            st.session_state.webhook_url = webhook_url
            st.success("✅ تم حفظ Webhook!")

    # ── Supabase ────────────────────────────────────────────────────────────
    with st.expander("🗄️ Supabase Database (تخزين بيانات العطور — اختياري)"):
        supabase_url = st.text_input(
            "SUPABASE_URL",
            value=st.session_state.get("supabase_url", ""),
            placeholder="https://xyz.supabase.co",
            key="supabase_url_input"
        )
        supabase_key = st.text_input(
            "SUPABASE_KEY (Anon/Service Role)",
            value=st.session_state.get("supabase_key", ""),
            type="password",
            placeholder="eyJhbGciOiJIUzI1NiI...",
            key="supabase_key_input"
        )
        if st.button("💾 حفظ إعدادات Supabase", use_container_width=True, key="save_supabase"):
            st.session_state.supabase_url = supabase_url
            st.session_state.supabase_key = supabase_key
            st.success("✅ تم حفظ إعدادات Supabase!")

    # ── حفظ الكل ────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("💾 حفظ جميع الإعدادات", type="primary", use_container_width=True, key="save_all"):
        st.session_state.gemini_key     = st.session_state.get("gemini_key_input", "")
        st.session_state.openrouter_key = st.session_state.get("openrouter_key_input", "")
        st.session_state.luma_key       = st.session_state.get("luma_key_input", "")
        st.session_state.runway_key     = st.session_state.get("runway_key_input", "")
        st.session_state.webhook_url    = st.session_state.get("webhook_url_input", "")
        st.session_state.supabase_url   = st.session_state.get("supabase_url_input", "")
        st.session_state.supabase_key   = st.session_state.get("supabase_key_input", "")
        st.success("✅ تم حفظ جميع الإعدادات بنجاح!")
        st.balloons()

    # ── ملاحظة الأمان ───────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:rgba(251,191,36,0.10); border:1.5px solid rgba(251,191,36,0.40);
         border-radius:0.6rem; padding:0.8rem; margin-top:1rem; color:#FFE880; font-size:0.82rem;'>
    🔒 <strong>ملاحظة الأمان:</strong> المفاتيح محفوظة في جلسة المتصفح فقط ولا تُرسل لأي خادم خارجي.
    لحفظها بشكل دائم، أضفها في ملف <code>secrets.toml</code> أو متغيرات البيئة.
    </div>
    """, unsafe_allow_html=True)

    # ── كيفية الحفظ الدائم ──────────────────────────────────────────────────
    with st.expander("📋 كيفية الحفظ الدائم (secrets.toml)"):
        st.code("""# .streamlit/secrets.toml
GEMINI_API_KEY = "AIzaSy..."
OPENROUTER_API_KEY = "sk-or-v1-..."
LUMA_API_KEY = "luma-..."
RUNWAY_API_KEY = "key_..."
WEBHOOK_PUBLISH_CONTENT = "https://hook.eu1.make.com/..."
""", language="toml")
        st.markdown("""
        <div style='color:#D0B070; font-size:0.82rem;'>
        ضع الملف في مجلد <code>.streamlit/</code> في مجلد المشروع.<br>
        على Streamlit Cloud: اذهب إلى Settings → Secrets وأضف المفاتيح هناك.
        </div>
        """, unsafe_allow_html=True)


# ─── Stats Page ───────────────────────────────────────────────────────────────
def show_stats_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,0.50); border-radius:1.2rem;
         padding:2rem; text-align:center; margin-bottom:2rem;">
      <div style="font-size:2.5rem;">📊</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">إحصائيات الجلسة</div>
    </div>
    """, unsafe_allow_html=True)

    gen_count = st.session_state.get("gen_count", 0)
    has_images = "generated_images" in st.session_state
    has_captions = "captions_data" in st.session_state
    has_scenario = "scenario_data" in st.session_state
    has_video = "video_gen_id" in st.session_state

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎨 عمليات التوليد", gen_count)
    c2.metric("🖼️ الصور المولدة", len(st.session_state.get("generated_images", {})))
    c3.metric("✍️ التعليقات", "✅" if has_captions else "—")
    c4.metric("🎬 الفيديو", "✅" if has_video else "—")

    if has_images:
        st.markdown("### 🖼️ الصور المولدة في هذه الجلسة")
        imgs = st.session_state.generated_images
        for key, data in imgs.items():
            if data.get("bytes"):
                st.markdown(f"- {data['label']} ({data['w']}×{data['h']})")

    if has_video:
        st.markdown("### 🎬 الفيديو المطلوب")
        st.info(f"معرّف التوليد: {st.session_state.get('video_gen_id', '—')}")
        if "video_url_ready" in st.session_state:
            st.success(f"✅ الفيديو جاهز: {st.session_state['video_url_ready']}")


# ─── Help Page ────────────────────────────────────────────────────────────────
def show_help_page():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A0E02,#2A1A06);
         border:2px solid rgba(212,175,55,0.50); border-radius:1.2rem;
         padding:2rem; text-align:center; margin-bottom:2rem;">
      <div style="font-size:2.5rem;">❓</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">دليل الاستخدام</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🚀 البدء السريع", expanded=True):
        st.markdown("""
        <div style='color:#D0B070; font-size:0.9rem; line-height:2.2;'>
        <strong style='color:#FFE060;'>الخطوات الأساسية:</strong><br>
        1️⃣ اذهب إلى <strong>إعدادات API</strong> وأدخل مفاتيحك<br>
        2️⃣ ارجع إلى <strong>الاستديو الإبداعي</strong><br>
        3️⃣ ارفع صورة العطر أو أدخل البيانات يدوياً<br>
        4️⃣ اختر المنصات المطلوبة<br>
        5️⃣ انقر <strong>"توليد الصور الآن"</strong><br>
        6️⃣ لتوليد فيديو: انتقل إلى تبويب <strong>"توليد الفيديو"</strong>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🖼️ توليد الصور — Imagen 3"):
        st.markdown("""
        <div style='color:#D0B070; font-size:0.88rem; line-height:2;'>
        • يتطلب <strong>GEMINI_API_KEY</strong><br>
        • يدعم جميع المنصات: Instagram، TikTok، YouTube، Twitter، Facebook، وأكثر<br>
        • خيارات: مهووس مع العطر، العطر وحده، وضع رمضان<br>
        • 4 أزياء مختلفة: البدلة، الهودي، الثوب، الكاجوال<br>
        • 7 مواقع: متجر، شاطئ، صحراء، استديو، حديقة، سطح، سيارة
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🎬 توليد الفيديو — Luma + RunwayML"):
        st.markdown("""
        <div style='color:#D0B070; font-size:0.88rem; line-height:2;'>
        • <strong>Luma Dream Machine:</strong> يتطلب LUMA_API_KEY — الأفضل للجودة<br>
        • <strong>RunwayML Gen-3:</strong> يتطلب RUNWAY_API_KEY — بديل ممتاز<br>
        • يدعم: text-to-video و image-to-video<br>
        • مدة الفيديو: 5، 7، 10، 15 ثانية<br>
        • نسب العرض: 9:16 (عمودي)، 16:9 (أفقي)، 1:1 (مربع)<br>
        • الفيديو يُعالج في السحابة — عادةً 2-5 دقائق
        </div>
        """, unsafe_allow_html=True)

    with st.expander("✍️ توليد النصوص — Claude 3.5"):
        st.markdown("""
        <div style='color:#D0B070; font-size:0.88rem; line-height:2;'>
        • يتطلب <strong>OPENROUTER_API_KEY</strong><br>
        • يولّد: تعليقات لجميع المنصات، أوصاف تسويقية، هاشتاقات، سيناريوهات، قصص<br>
        • اللغة: عربية خليجية راقية مخصصة لكل منصة
        </div>
        """, unsafe_allow_html=True)

    with st.expander("💰 تقدير التكاليف"):
        st.markdown("""
        | الخدمة | التكلفة التقريبية |
        |--------|-------------------|
        | Gemini API (تحليل + نص) | مجاني حتى حد معين |
        | Imagen 3 (صورة واحدة) | ~$0.03 |
        | Luma Dream Machine (فيديو 5s) | ~$0.10-0.30 |
        | RunwayML Gen-3 (فيديو 5s) | ~$0.25-0.50 |
        | OpenRouter / Claude 3.5 | ~$0.003 لكل 1000 token |
        """, unsafe_allow_html=True)


# ─── Main Router ──────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    page = st.session_state.get("current_page", "studio")

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
