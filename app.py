"""
🎬 مهووس AI Studio — v14.0
التطبيق الرئيسي — هيكلة نظيفة وقابلة للتوسع
"""

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# إعداد الصفحة — يجب أن يكون أول شيء
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="مهووس AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://mahwousstore.com",
        "About": "مهووس AI Studio v14.0 — منصة توليد محتوى العطور الفاخرة"
    }
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS العام — الطراز الذهبي الفاخر
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

:root {
    --gold: #D4AF37;
    --gold-light: #FFE060;
    --gold-dim: rgba(212,175,55,0.35);
    --bg-main: #0A0600;
    --bg-card: #1A1006;
    --bg-card2: #130D04;
    --text-main: #F0D880;
    --text-dim: #906030;
    --text-bright: #FFE060;
    --border: rgba(212,175,55,0.30);
}

html, body, [class*="css"] {
    font-family: 'Cairo', 'Segoe UI', sans-serif !important;
    direction: rtl;
}

/* ─── Background ──── */
.stApp { background: var(--bg-main) !important; }

/* ─── Sidebar ──── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0800 0%, #1A1000 60%, #0D0800 100%) !important;
    border-left: 2px solid var(--gold-dim) !important;
}
[data-testid="stSidebar"] * { color: #D4B870 !important; }

/* ─── Buttons ──── */
.stButton > button {
    background: linear-gradient(135deg, #2A1A04, #3A2208) !important;
    border: 1.5px solid var(--gold-dim) !important;
    color: var(--gold-light) !important;
    border-radius: 0.6rem !important;
    font-weight: 800 !important;
    font-family: 'Cairo', sans-serif !important;
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
    color: #0A0600 !important;
    border-color: #FFD700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #D4A017, #FFD700, #D4A017) !important;
    box-shadow: 0 0 24px rgba(212,175,55,0.45) !important;
}

/* ─── Inputs ──── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1.5px solid var(--gold-dim) !important;
    border-radius: 0.5rem !important;
}

/* ─── Tabs ──── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-bottom: 2px solid var(--gold-dim) !important;
    gap: 0.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-dim) !important;
    font-weight: 700 !important;
    border-radius: 0.4rem 0.4rem 0 0 !important;
    padding: 0.5rem 1rem !important;
    font-family: 'Cairo', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(212,175,55,0.15) !important;
    color: var(--gold-light) !important;
    border-bottom: 3px solid #F0CC55 !important;
}

/* ─── Expander ──── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    color: #D4B870 !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 0.5rem !important;
    font-weight: 700 !important;
}

/* ─── Alerts ──── */
.stAlert { border-radius: 0.65rem !important; font-weight: 700 !important; }
div[data-testid="stInfo"]    { background: rgba(59,130,246,0.12)  !important; border-color: #3b82f6 !important; }
div[data-testid="stWarning"] { background: rgba(251,191,36,0.12)  !important; border-color: #fbbf24 !important; }
div[data-testid="stSuccess"] { background: rgba(52,211,153,0.12)  !important; border-color: #34d399 !important; }
div[data-testid="stError"]   { background: rgba(239,68,68,0.12)   !important; border-color: #ef4444 !important; }

/* ─── Metrics ──── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--gold-dim) !important;
    border-radius: 0.6rem !important;
    padding: 0.8rem !important;
}
[data-testid="stMetricValue"] { color: var(--gold-light) !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: var(--text-dim) !important; }

/* ─── Progress ──── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #B8860B, #FFD700) !important;
}

/* ─── File uploader ──── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--gold-dim) !important;
    border-radius: 0.8rem !important;
}

/* ─── Divider ──── */
hr { border-color: var(--gold-dim) !important; }

/* ─── Scrollbar ──── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D0800; }
::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.40); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(212,175,55,0.65); }

/* ─── Shared Components ──── */
.step-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(212,175,55,0.18); border: 2px solid var(--gold-dim);
    color: var(--gold-light); padding: 0.35rem 1rem; border-radius: 999px;
    font-size: 0.88rem; font-weight: 900; margin-bottom: 0.8rem;
}
.section-card {
    background: linear-gradient(135deg, #1A0E02, #2A1A06);
    border: 2px solid rgba(212,175,55,0.45); border-radius: 1.2rem;
    padding: 1.8rem; margin-bottom: 1.5rem;
}
.badge-ok  { background: rgba(52,211,153,0.15); border: 1px solid #34d399; color: #34d399; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; }
.badge-no  { background: rgba(239,68,68,0.15);  border: 1px solid #ef4444; color: #ef4444; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; }
.badge-warn{ background: rgba(251,191,36,0.15); border: 1px solid #fbbf24; color: #fbbf24; padding: 2px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# الشريط الجانبي — تنقل رئيسي
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:

        # ─── شعار الاستديو ───
        st.markdown("""
        <div style="text-align:center; padding:1.5rem 0.5rem 1rem;">
          <div style="font-size:3rem; line-height:1;">🎬</div>
          <div style="color:#FFE060; font-size:1.3rem; font-weight:900; margin:0.4rem 0;">مهووس AI Studio</div>
          <div style="color:#906030; font-size:0.72rem; font-weight:700; letter-spacing:0.05rem;">
            v14.0 · Gemini + Claude + Luma
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ─── التنقل ───
        pages = [
            ("studio",   "🎬", "الاستديو"),
            ("settings", "⚙️", "إعدادات API"),
            ("stats",    "📊", "الإحصائيات"),
            ("help",     "❓", "المساعدة"),
        ]
        if "page" not in st.session_state:
            st.session_state.page = "studio"

        for page_key, icon, label in pages:
            is_active = st.session_state.page == page_key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("---")

        # ─── حالة API ───
        _render_api_status()

        st.markdown("---")

        # ─── إحصائيات الجلسة ───
        gen_count = st.session_state.get("gen_count", 0)
        img_count = len(st.session_state.get("generated_images", {}))
        st.markdown(f"""
        <div style='background:rgba(212,175,55,0.08); border:1px solid rgba(212,175,55,0.20);
             border-radius:0.8rem; padding:0.8rem; text-align:center;'>
          <div style='display:flex; justify-content:space-around;'>
            <div>
              <div style='color:#FFE060; font-size:1.5rem; font-weight:900;'>{gen_count}</div>
              <div style='color:#906030; font-size:0.7rem;'>عملية توليد</div>
            </div>
            <div>
              <div style='color:#FFE060; font-size:1.5rem; font-weight:900;'>{img_count}</div>
              <div style='color:#906030; font-size:0.7rem;'>صورة</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        if st.button("🗑️ مسح الجلسة", use_container_width=True, key="clear_session"):
            _clear_session()
            st.rerun()


def _render_api_status():
    """عرض حالة مفاتيح API بشكل مضغوط"""
    try:
        from modules.ai_engine import _get_secrets
        secrets = _get_secrets()
    except Exception:
        secrets = {}

    st.markdown("<div style='color:#906030; font-size:0.82rem; font-weight:700; margin-bottom:6px;'>📡 حالة الاتصال</div>", unsafe_allow_html=True)

    apis = [
        ("gemini",      "🧠", "Gemini"),
        ("luma",        "🎬", "Luma"),
        ("fal",         "⚡", "Fal.ai"),
        ("openrouter",  "✍️", "Claude"),
        ("runway",      "🎥", "Runway"),
        ("elevenlabs",  "🎙️", "ElevenLabs"),
    ]
    rows_html = ""
    for key, icon, label in apis:
        is_ok   = bool(secrets.get(key))
        dot     = "🟢" if is_ok else "⚪"
        color   = "#90D870" if is_ok else "#505050"
        rows_html += (
            f"<div style='display:flex; justify-content:space-between; align-items:center;"
            f"background:rgba(255,255,255,0.03); padding:3px 8px; border-radius:4px; margin-bottom:2px;'>"
            f"<span style='font-size:0.75rem;'>{icon} {label}</span>"
            f"<span style='color:{color}; font-size:0.75rem; font-weight:bold;'>{dot}</span>"
            f"</div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)

    if st.button("🔄 فحص الاتصال", key="check_health", use_container_width=True):
        try:
            from modules.ai_engine import check_api_health
            with st.spinner("جاري الفحص..."):
                st.session_state.api_health = check_api_health()
            st.success("تم الفحص!")
        except Exception as e:
            st.warning(f"⚠️ {e}")


def _clear_session():
    """مسح بيانات الجلسة مع الحفاظ على الإعدادات"""
    keep = {k: v for k, v in st.session_state.items()
            if k.endswith("_key") or k in ("page", "api_health")}
    st.session_state.clear()
    st.session_state.update(keep)


# ══════════════════════════════════════════════════════════════════════════════
# صفحة الإعدادات
# ══════════════════════════════════════════════════════════════════════════════
def show_settings_page():
    st.markdown("""
    <div class="section-card" style="text-align:center;">
      <div style="font-size:2.5rem;">⚙️</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">إعدادات API</div>
      <div style="color:#906030; font-size:0.9rem;">أدخل مفاتيح API لتفعيل جميع ميزات التوليد</div>
    </div>
    """, unsafe_allow_html=True)

    # تعريف الخدمات
    services = [
        {
            "key":        "gemini_key",
            "label":      "🧠 Google Gemini + Imagen 3",
            "desc":       "توليد الصور + تحليل العطور",
            "color":      "rgba(66,133,244,0.15)",
            "border":     "rgba(66,133,244,0.40)",
            "text_color": "#A0C0FF",
            "link":       "https://aistudio.google.com/app/apikey",
            "link_label": "aistudio.google.com",
            "prefix":     "AIzaSy...",
            "test_url":   "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "secret_var": "GEMINI_API_KEY",
        },
        {
            "key":        "openrouter_key",
            "label":      "🤖 OpenRouter / Claude 3.5",
            "desc":       "توليد التعليقات والنصوص",
            "color":      "rgba(120,80,220,0.12)",
            "border":     "rgba(120,80,220,0.40)",
            "text_color": "#C0A0FF",
            "link":       "https://openrouter.ai/keys",
            "link_label": "openrouter.ai/keys",
            "prefix":     "sk-or-v1-...",
            "secret_var": "OPENROUTER_API_KEY",
        },
        {
            "key":        "luma_key",
            "label":      "🎬 Luma Dream Machine",
            "desc":       "توليد الفيديو — الأفضل",
            "color":      "rgba(52,211,153,0.10)",
            "border":     "rgba(52,211,153,0.40)",
            "text_color": "#A0FFD8",
            "link":       "https://lumalabs.ai/dream-machine/api",
            "link_label": "lumalabs.ai",
            "prefix":     "luma-...",
            "secret_var": "LUMA_API_KEY",
        },
        {
            "key":        "runway_key",
            "label":      "🎥 RunwayML Gen-3",
            "desc":       "توليد الفيديو — بديل",
            "color":      "rgba(239,68,68,0.10)",
            "border":     "rgba(239,68,68,0.40)",
            "text_color": "#FFB0B0",
            "link":       "https://app.runwayml.com/settings/api-keys",
            "link_label": "app.runwayml.com",
            "prefix":     "key_...",
            "secret_var": "RUNWAY_API_KEY",
        },
        {
            "key":        "fal_key",
            "label":      "⚡ Fal.ai — Flux + Kling",
            "desc":       "توليد الصور والفيديو السريع",
            "color":      "rgba(251,191,36,0.10)",
            "border":     "rgba(251,191,36,0.40)",
            "text_color": "#FFE880",
            "link":       "https://fal.ai/dashboard",
            "link_label": "fal.ai/dashboard",
            "prefix":     "xxxxxxxx-xxxx:xxxxxxxx",
            "secret_var": "FAL_API_KEY",
        },
        {
            "key":        "elevenlabs_key",
            "label":      "🎙️ ElevenLabs",
            "desc":       "تعليق صوتي للفيديوهات",
            "color":      "rgba(167,139,250,0.10)",
            "border":     "rgba(167,139,250,0.40)",
            "text_color": "#C4B5FD",
            "link":       "https://elevenlabs.io/app/settings/api-keys",
            "link_label": "elevenlabs.io",
            "prefix":     "sk_...",
            "secret_var": "ELEVENLABS_API_KEY",
        },
        {
            "key":        "imgbb_key",
            "label":      "🖼️ ImgBB",
            "desc":       "رفع الصور والحصول على روابط",
            "color":      "rgba(34,197,94,0.10)",
            "border":     "rgba(34,197,94,0.40)",
            "text_color": "#A7F3D0",
            "link":       "https://api.imgbb.com/",
            "link_label": "api.imgbb.com",
            "prefix":     "xxxxxxxxxxxxxxxx",
            "secret_var": "IMGBB_API_KEY",
        },
    ]

    # Webhook بشكل منفصل
    webhook_services = [
        {
            "key":        "webhook_url",
            "label":      "🔗 Make.com Webhook",
            "desc":       "نشر المحتوى التلقائي",
            "color":      "rgba(56,189,248,0.10)",
            "border":     "rgba(56,189,248,0.40)",
            "text_color": "#7DD3FC",
            "placeholder": "https://hook.eu2.make.com/...",
            "secret_var": "MAKE_WEBHOOK_URL",
            "is_url":     True,
        },
        {
            "key":        "supabase_url",
            "label":      "🗄️ Supabase URL",
            "desc":       "قاعدة بيانات العطور",
            "color":      "rgba(16,185,129,0.10)",
            "border":     "rgba(16,185,129,0.40)",
            "text_color": "#6EE7B7",
            "placeholder": "https://xxx.supabase.co",
            "secret_var": "SUPABASE_URL",
            "is_url":     True,
        },
    ]

    # ─── عرض خدمات API ───
    for svc in services:
        with st.expander(f"{svc['label']} — {svc['desc']}"):
            st.markdown(
                f"<div style='background:{svc['color']}; border:1.5px solid {svc['border']};"
                f"border-radius:0.6rem; padding:0.7rem; margin-bottom:0.8rem; color:{svc['text_color']}; font-size:0.85rem;'>"
                f"🔑 احصل على مفتاحك من: <a href='{svc.get('link','')}' target='_blank' style='color:{svc['text_color']};'>"
                f"{svc.get('link_label','')}</a></div>",
                unsafe_allow_html=True
            )
            val = st.text_input(
                svc["secret_var"],
                value=st.session_state.get(svc["key"], ""),
                type="password",
                placeholder=svc.get("prefix", ""),
                key=f"input_{svc['key']}"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"💾 حفظ", key=f"save_{svc['key']}", use_container_width=True):
                    st.session_state[svc["key"]] = val
                    st.success("✅ تم الحفظ!")
            with col2:
                if st.button(f"🧪 اختبار", key=f"test_{svc['key']}", use_container_width=True):
                    if not val:
                        st.error("❌ أدخل المفتاح أولاً")
                    else:
                        _test_api_key(svc["key"], val)

    # ─── Webhook و Supabase ───
    for svc in webhook_services:
        with st.expander(f"{svc['label']} — {svc['desc']}"):
            val = st.text_input(
                svc["secret_var"],
                value=st.session_state.get(svc["key"], ""),
                placeholder=svc.get("placeholder", ""),
                key=f"input_{svc['key']}"
            )
            if st.button(f"💾 حفظ {svc['label']}", key=f"save_{svc['key']}", use_container_width=True):
                st.session_state[svc["key"]] = val
                st.success("✅ تم الحفظ!")

    if "supabase_url" in [s["key"] for s in webhook_services]:
        with st.expander("🗄️ Supabase Key"):
            val = st.text_input("SUPABASE_KEY", value=st.session_state.get("supabase_key", ""), type="password", placeholder="eyJh...")
            if st.button("💾 حفظ Supabase Key", use_container_width=True):
                st.session_state["supabase_key"] = val
                st.success("✅ تم الحفظ!")

    # ─── حفظ الكل ───
    st.markdown("---")
    if st.button("💾 حفظ جميع الإعدادات", type="primary", use_container_width=True, key="save_all_btn"):
        for svc in services:
            val = st.session_state.get(f"input_{svc['key']}", "")
            if val:
                st.session_state[svc["key"]] = val
        st.success("✅ تم حفظ جميع الإعدادات!")
        st.balloons()

    # ─── ملاحظة الأمان ───
    st.markdown("""
    <div style='background:rgba(251,191,36,0.10); border:1.5px solid rgba(251,191,36,0.40);
         border-radius:0.6rem; padding:0.8rem; margin-top:1rem; color:#FFE880; font-size:0.82rem;'>
    🔒 <strong>ملاحظة الأمان:</strong> المفاتيح محفوظة في جلسة المتصفح فقط.<br>
    للحفظ الدائم: أضفها في ملف <code>.streamlit/secrets.toml</code>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 مثال على secrets.toml"):
        st.code("""# .streamlit/secrets.toml
GEMINI_API_KEY       = "AIzaSy..."
OPENROUTER_API_KEY   = "sk-or-v1-..."
LUMA_API_KEY         = "luma-..."
RUNWAY_API_KEY       = "key_..."
FAL_API_KEY          = "xxxx:xxxx"
IMGBB_API_KEY        = "xxxx"
ELEVENLABS_API_KEY   = "sk_..."
MAKE_WEBHOOK_URL     = "https://hook.eu2.make.com/..."
SUPABASE_URL         = "https://xxx.supabase.co"
SUPABASE_KEY         = "eyJh..."
""", language="toml")


def _test_api_key(service_key: str, key_val: str):
    """اختبار مفتاح API محدد"""
    import requests
    try:
        if service_key == "gemini_key":
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers={"Content-Type": "application/json", "x-goog-api-key": key_val},
                json={"contents": [{"parts": [{"text": "Say OK"}]}]},
                timeout=15
            )
            if r.status_code == 200:
                st.success("✅ Gemini يعمل!")
            else:
                st.error(f"❌ {r.status_code}: {r.json().get('error', {}).get('message', '')}")

        elif service_key == "openrouter_key":
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key_val}", "Content-Type": "application/json"},
                json={"model": "anthropic/claude-3.5-sonnet", "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5},
                timeout=20
            )
            st.success("✅ OpenRouter يعمل!") if r.status_code == 200 else st.error(f"❌ {r.status_code}: {r.text[:100]}")

        elif service_key == "luma_key":
            r = requests.get(
                "https://api.lumalabs.ai/dream-machine/v1/generations",
                headers={"Authorization": f"Bearer {key_val}"},
                timeout=15
            )
            if r.status_code in [200, 201]:
                st.success("✅ Luma يعمل!")
            elif r.status_code == 401:
                st.error("❌ مفتاح غير صحيح")
            else:
                st.warning(f"⚠️ استجابة {r.status_code} — قد يكون صحيحاً")

        elif service_key == "fal_key":
            st.info("ℹ️ مفتاح Fal.ai محفوظ — سيتم التحقق عند أول استخدام")

        elif service_key == "runway_key":
            r = requests.get(
                "https://api.dev.runwayml.com/v1/tasks",
                headers={"Authorization": f"Bearer {key_val}", "X-Runway-Version": "2024-11-06"},
                timeout=15
            )
            if r.status_code in [200, 201]:
                st.success("✅ RunwayML يعمل!")
            elif r.status_code == 401:
                st.error("❌ مفتاح غير صحيح")
            else:
                st.warning(f"⚠️ {r.status_code}")

        else:
            st.info("ℹ️ المفتاح محفوظ")

    except requests.exceptions.ConnectionError:
        st.error("❌ لا يوجد اتصال بالإنترنت")
    except requests.exceptions.Timeout:
        st.error("❌ انتهت مهلة الاتصال")
    except Exception as e:
        st.error(f"❌ خطأ: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# صفحة الإحصائيات
# ══════════════════════════════════════════════════════════════════════════════
def show_stats_page():
    st.markdown("""
    <div class="section-card" style="text-align:center;">
      <div style="font-size:2.5rem;">📊</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">إحصائيات الجلسة</div>
    </div>
    """, unsafe_allow_html=True)

    gen_count   = st.session_state.get("gen_count", 0)
    img_count   = len(st.session_state.get("generated_images", {}))
    has_video   = "video_url_ready" in st.session_state
    has_caps    = "captions_data" in st.session_state
    has_scene   = "scenario_data" in st.session_state

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⚡ عمليات التوليد", gen_count)
    c2.metric("🖼️ الصور", img_count)
    c3.metric("🎬 الفيديو", "✅" if has_video else "—")
    c4.metric("✍️ التعليقات", "✅" if has_caps else "—")
    c5.metric("🎭 السيناريو", "✅" if has_scene else "—")

    if st.session_state.get("generated_images"):
        st.markdown("---")
        st.markdown("### 🖼️ الصور المولدة")
        imgs = st.session_state.generated_images
        img_rows = [(k, d) for k, d in imgs.items() if d.get("bytes")]
        if img_rows:
            cols = st.columns(min(4, len(img_rows)))
            for i, (k, d) in enumerate(img_rows):
                with cols[i % 4]:
                    st.image(d["bytes"], caption=f"{d.get('label', k)}", use_container_width=True)

    if has_video:
        st.markdown("---")
        st.markdown("### 🎬 الفيديو")
        st.success(f"✅ رابط الفيديو: {st.session_state.get('video_url_ready')}")

    st.markdown("---")
    if st.button("🗑️ مسح جميع النتائج", use_container_width=True, type="secondary"):
        for k in ["generated_images", "video_url_ready", "captions_data",
                  "scenario_data", "hashtags_data", "descriptions_data", "gen_count"]:
            st.session_state.pop(k, None)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# صفحة المساعدة
# ══════════════════════════════════════════════════════════════════════════════
def show_help_page():
    st.markdown("""
    <div class="section-card" style="text-align:center;">
      <div style="font-size:2.5rem;">❓</div>
      <div style="color:#FFE060; font-size:1.8rem; font-weight:900; margin:0.5rem 0;">دليل الاستخدام</div>
      <div style="color:#906030; font-size:0.9rem;">كيفية استخدام مهووس AI Studio v14.0</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🚀 البدء السريع — 6 خطوات", expanded=True):
        st.markdown("""
        <div style='color:#D0B070; font-size:0.92rem; line-height:2.5;'>
        <strong style='color:#FFE060;'>① إعداد المفاتيح</strong> — اذهب إلى ⚙️ إعدادات API وأدخل مفاتيحك<br>
        <strong style='color:#FFE060;'>② اختر العطر</strong> — ارفع صورة العطر أو أدخل البيانات يدوياً<br>
        <strong style='color:#FFE060;'>③ حلل العطر</strong> — اضغط "تحليل" ليقرأ الذكاء الاصطناعي تفاصيل العطر<br>
        <strong style='color:#FFE060;'>④ اختر المنصات</strong> — حدد منصات نشر المحتوى المطلوبة<br>
        <strong style='color:#FFE060;'>⑤ ولّد المحتوى</strong> — صور، فيديو، تعليقات، سيناريوهات، هاشتاقات<br>
        <strong style='color:#FFE060;'>⑥ انشر أو حمّل</strong> — نشر تلقائي عبر Make.com أو تحميل ZIP
        </div>
        """, unsafe_allow_html=True)

    guides = [
        ("🖼️ توليد الصور", """
        • يتطلب GEMINI_API_KEY أو FAL_API_KEY<br>
        • يدعم جميع المنصات: Instagram، TikTok، YouTube، Twitter، وأكثر<br>
        • 5 أزياء لمهووس: البدلة · الهودي · الثوب · الكاجوال · غربي<br>
        • 7 مواقع: متجر · شاطئ · صحراء · استديو · حديقة · سطح · سيارة<br>
        • وضع رمضان الخاص<br>
        • رفع الدقة 4K عبر Fal.ai
        """),
        ("🎬 توليد الفيديو", """
        • Luma Dream Machine: الأفضل للجودة — يتطلب LUMA_API_KEY<br>
        • RunwayML Gen-3: بديل ممتاز — يتطلب RUNWAY_API_KEY<br>
        • Fal.ai (Kling/Veo/SVD): سريع — يتطلب FAL_API_KEY<br>
        • مدة: 5، 7، 10، 15 ثانية<br>
        • نسب: 9:16 (عمودي) · 16:9 (أفقي) · 1:1 (مربع)<br>
        • text-to-video و image-to-video
        """),
        ("✍️ توليد النصوص", """
        • يتطلب OPENROUTER_API_KEY (Claude 3.5 Sonnet)<br>
        • تعليقات لجميع المنصات باللغة العربية الخليجية<br>
        • أوصاف تسويقية: قصير · متوسط · طويل · إعلان<br>
        • هاشتاقات: عربية · إنجليزية · علامة · ترند<br>
        • سيناريوهات فيديو كاملة مع برومت Luma/Runway<br>
        • SEO متكامل + قصص عطور شعرية
        """),
        ("💰 تقدير التكاليف", """
        | الخدمة | التكلفة التقريبية |
        |--------|-------------------|
        | Gemini API | مجاني حتى حد معين |
        | Imagen 3 (صورة) | ~$0.03 |
        | Luma (فيديو 5s) | ~$0.10–0.30 |
        | RunwayML (فيديو 5s) | ~$0.25–0.50 |
        | Claude 3.5 | ~$0.003 / 1000 token |
        | Fal.ai | يعتمد على النموذج |
        """),
    ]

    for title, body in guides:
        with st.expander(title):
            st.markdown(f"<div style='color:#D0B070; font-size:0.88rem; line-height:2;'>{body}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# الموجّه الرئيسي
# ══════════════════════════════════════════════════════════════════════════════
def main():
    render_sidebar()

    page = st.session_state.get("page", "studio")

    if page == "studio":
        from modules.studio import show_studio_page
        show_studio_page()
    elif page == "settings":
        show_settings_page()
    elif page == "stats":
        show_stats_page()
    elif page == "help":
        show_help_page()
    else:
        st.error(f"صفحة غير معروفة: {page}")


if __name__ == "__main__":
    main()
