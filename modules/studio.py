"""
🎬 استديو مهووس الذكي v13.0
واجهة رئيسية محسّنة — توليد الصور والفيديوهات مباشرة من التطبيق
"""

import streamlit as st
import base64
import json
import io
import zipfile
from datetime import datetime
from PIL import Image

from modules.ai_engine import (
    analyze_perfume_image, generate_platform_images,
    generate_all_captions, generate_descriptions,
    generate_hashtags, generate_scenario,
    generate_video_luma, check_luma_status, poll_luma_video,
    generate_video_runway, check_runway_status,
    generate_video_fal, check_fal_video_status,
    generate_image_gemini, smart_generate_image, generate_perfume_story,
    build_manual_info, build_video_prompt,
    send_to_make, build_make_payload,
    analyze_competitor, generate_image_remix_fal,
    load_asset_bytes,
    generate_concurrent_images, generate_voiceover_elevenlabs,
    PLATFORMS, MAHWOUS_OUTFITS, FAL_VIDEO_MODELS, _get_secrets
)

# ─── Helper functions for prompt building ─────────────────────────────────────
def build_mahwous_product_prompt(info: dict, outfit: str, scene: str, aspect: str) -> str:
    brand = info.get("brand", "luxury perfume brand")
    product = info.get("product_name", "luxury fragrance")
    mood = info.get("mood", "luxurious and elegant")
    outfit_desc = {
        "suit": "elegant black suit with golden embroidery and golden tie",
        "hoodie": "signature golden hoodie with brand logo",
        "thobe": "royal white thobe with golden trim",
        "casual": "smart casual outfit with golden accents",
        "western": "stylish western leather jacket"
    }.get(outfit, "elegant outfit")
    scene_desc = {
        "store": "luxury perfume boutique with golden shelves",
        "beach": "golden sunset beach with soft waves",
        "desert": "golden sand dunes at sunset",
        "studio": "professional luxury studio with dramatic lighting",
        "garden": "royal garden with roses and fountains",
        "rooftop": "rooftop of a luxury skyscraper at night",
        "car": "interior of a luxury sports car"
    }.get(scene, "luxury setting")
    return (
        f"Ultra-realistic professional photo of Mahwous, a charismatic Arab male brand ambassador "
        f"with black hair, short brown beard, and warm brown eyes, wearing {outfit_desc}, "
        f"holding {brand} {product} perfume bottle elegantly in {scene_desc}. "
        f"Mood: {mood}. Photorealistic, cinematic lighting, luxury commercial photography. "
        f"Aspect ratio {aspect}. High quality 4K."
    )

def build_product_only_prompt(info: dict, aspect: str) -> str:
    brand = info.get("brand", "luxury perfume brand")
    product = info.get("product_name", "luxury fragrance")
    colors = info.get("colors", ["gold", "black"])
    colors_str = ", ".join(colors[:3]) if colors else "gold and black"
    return (
        f"Ultra-realistic luxury product photography of {brand} {product} perfume bottle, "
        f"elegant flacon with {colors_str} color scheme, placed on a reflective marble surface "
        f"with dramatic studio lighting, golden bokeh background, luxury brand advertisement style. "
        f"Aspect ratio {aspect}. High quality 4K commercial photo."
    )

def build_ramadan_product_prompt(info: dict, aspect: str) -> str:
    brand = info.get("brand", "luxury perfume brand")
    product = info.get("product_name", "luxury fragrance")
    return (
        f"Ultra-realistic Ramadan themed luxury product photo of {brand} {product} perfume, "
        f"surrounded by golden crescent moon, traditional lanterns, golden star decorations, "
        f"soft warm glowing lights, dates and Arabic calligraphy elements, "
        f"elegant Ramadan Kareem atmosphere. Aspect ratio {aspect}. High quality 4K."
    )

def generate_trend_insights(info: dict) -> dict:
    """توليد تحليل ترندات للمنتج — يستخدم Claude أو Gemini تلقائياً"""
    import json
    from modules.ai_engine import _call_claude, _parse_json_response
    brand = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    mood = info.get("mood", "luxury")
    prompt = f"""أنت خبير تسويق رقمي متخصص في العطور الفاخرة.
حلّل هذا المنتج واقترح ترندات محتوى:
العطر: {brand} - {product}
المزاج: {mood}

أعطني JSON فقط بهذا الشكل بدون أي نص إضافي:
{{
  "product_summary": "ملخص هوية العطر في جملتين",
  "target_audience": "وصف الجمهور المستهدف",
  "trending_topics": [
    {{"platform": "TikTok", "topic": "موضوع رائج", "hook": "هوك جذاب", "relevance": "سبب الارتباط"}},
    {{"platform": "Instagram", "topic": "موضوع رائج", "hook": "هوك جذاب", "relevance": "سبب الارتباط"}},
    {{"platform": "Twitter", "topic": "موضوع رائج", "hook": "هوك جذاب", "relevance": "سبب الارتباط"}}
  ],
  "viral_hooks": ["هوك 1", "هوك 2", "هوك 3"],
  "content_angles": [
    {{"angle": "زاوية 1", "description": "وصف الزاوية", "format": "ريلز"}},
    {{"angle": "زاوية 2", "description": "وصف الزاوية", "format": "بوست"}}
  ],
  "trending_hashtags": {{
    "viral": ["#هاشتاق1", "#هاشتاق2"],
    "niche": ["#هاشتاق3", "#هاشتاق4"],
    "buying": ["#شراء_عطور_فاخرة", "#عطور_أصلية"]
  }},
  "best_post_times": {{"TikTok": "8-10 مساءً", "Instagram": "12-2 ظهراً"}},
  "competitor_gap": "فرصة غير مستغلة في السوق",
  "seasonal_angle": "زاوية موسمية مناسبة"
}}"""
    try:
        # _call_claude يتضمن fallback تلقائي إلى Gemini عند نقص رصيد OpenRouter
        text = _call_claude(prompt, max_tokens=1500)
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e)}

def analyze_perfume_url(url: str) -> dict:
    """استخراج معلومات العطر من رابط المنتج — يستخدم Claude أو Gemini تلقائياً"""
    import requests, json
    from bs4 import BeautifulSoup
    from modules.ai_engine import _call_claude
    if not url or not url.startswith("http"):
        return {"success": False, "error": "رابط غير صالح"}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        title_text = title.get_text()[:200] if title else ""
        meta_desc = soup.find("meta", {"name": "description"})
        desc_text = meta_desc.get("content", "")[:300] if meta_desc else ""
        page_text = soup.get_text()[:1000]

        prompt = f"""من هذه الصفحة استخرج معلومات العطر بـ JSON:
العنوان: {title_text}
الوصف: {desc_text}
النص: {page_text[:500]}

أعطني JSON فقط بهذا الشكل بدون أي نص إضافي:
{{"brand": "العلامة التجارية", "product_name": "اسم العطر", "type": "EDP/EDT", "gender": "masculine/feminine/unisex", "style": "luxury", "mood": "المزاج", "notes_guess": "ملاحظات العطر", "bottle_shape": "شكل الزجاجة", "colors": ["gold"]}}"""

        # _call_claude يتضمن fallback تلقائي إلى Gemini عند نقص رصيد OpenRouter
        text = _call_claude(prompt, max_tokens=500)
        if "```" in text:
            text = text.split("```")[1].lstrip("json").strip()
        result = json.loads(text.strip())
        result["success"] = True
        return result
    except Exception as e:
        # فشل AI — إرجاع بيانات أساسية من عنوان الصفحة
        try:
            import requests as _r
            from bs4 import BeautifulSoup as _BS
            _resp = _r.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            _soup = _BS(_resp.text, "html.parser")
            _title = _soup.find("title")
            _title_text = _title.get_text()[:200] if _title else url
            return {
                "success": True,
                "brand": _title_text.split("-")[0].strip() if "-" in _title_text else _title_text[:30],
                "product_name": _title_text, "type": "EDP", "gender": "unisex",
                "style": "luxury", "mood": "فاخر", "notes_guess": "", "bottle_shape": "", "colors": ["gold"]
            }
        except Exception:
            return {"success": False, "error": str(e)}

def upscale_image_fal(image_bytes: bytes) -> dict:
    """رفع دقة الصورة باستخدام Fal.ai"""
    try:
        import fal_client, base64
        secrets = _get_secrets()
        if not secrets.get("fal"):
            return {"success": False, "error": "FAL_API_KEY مفقود"}
        import os
        os.environ["FAL_KEY"] = secrets["fal"]
        b64 = base64.b64encode(image_bytes).decode()
        data_uri = f"data:image/jpeg;base64,{b64}"
        result = fal_client.run(
            "fal-ai/ccsr",
            arguments={"image_url": data_uri, "scale": 2}
        )
        img_url = result.get("image", {}).get("url") or result.get("url", "")
        if img_url:
            import requests
            img_resp = requests.get(img_url, timeout=30)
            return {"success": True, "bytes": img_resp.content, "url": img_url}
        return {"success": False, "error": "لم يتم إرجاع صورة"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Studio CSS ────────────────────────────────────────────────────────────────
STUDIO_CSS = """
<style>
.studio-hero {
    background: linear-gradient(135deg, #1A0E02 0%, #2A1A06 50%, #1A0E02 100%);
    border: 2px solid rgba(212,175,55,0.60);
    border-radius: 1.3rem; padding: 2.8rem 2rem; text-align: center;
    margin-bottom: 2rem; position: relative; overflow: hidden;
}
.studio-hero::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 55% at 50% 40%, rgba(212,175,55,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.studio-hero h1 { color: #FFE060; font-size: 2.4rem; margin: 0; position: relative; font-weight: 900; }
.studio-hero .sub { color: #F0C870; margin: 0.5rem 0 0; font-size: 0.95rem; position: relative; font-weight: 700; }
.studio-hero .version-badge {
    display: inline-block; background: rgba(212,175,55,0.20); border: 1.5px solid rgba(212,175,55,0.55);
    color: #FFE060; padding: 0.25rem 1rem; border-radius: 999px; font-size: 0.75rem; font-weight: 900;
    letter-spacing: 0.08rem; margin-top: 0.8rem; position: relative;
}
.mode-card {
    background: #130D04; border: 2px solid rgba(212,175,55,0.25);
    border-radius: 1rem; padding: 1.6rem; text-align: center; cursor: pointer;
    transition: all 0.25s; position: relative; overflow: hidden;
}
.mode-card:hover, .mode-card.active {
    border-color: #F0CC55; background: rgba(212,175,55,0.08);
    box-shadow: 0 0 24px rgba(212,175,55,0.15);
}
.analysis-card {
    background: linear-gradient(135deg, #1E1006, #281808);
    border: 2px solid rgba(212,175,55,0.50); border-radius: 1rem; padding: 1.4rem;
}
.analysis-card .brand { color: #FFE060; font-size: 1.5rem; font-weight: 900; }
.analysis-card .name { color: #FFF0D8; font-size: 1.05rem; font-weight: 800; }
.analysis-card .tag {
    display: inline-block; background: rgba(212,175,55,0.18);
    border: 1.5px solid rgba(212,175,55,0.50); color: #FFD840;
    padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.78rem; margin: 0.15rem;
    font-weight: 800;
}
.result-section {
    background: #1E1408; border: 1.5px solid rgba(212,175,55,0.35);
    border-radius: 1rem; padding: 1.6rem; margin-bottom: 1rem;
}
.result-section h3 { color: #FFE060; font-size: 1.1rem; margin: 0 0 1rem; font-weight: 900; }
.caption-block {
    background: #1A1006; border: 1.5px solid rgba(212,175,55,0.30);
    border-radius: 0.8rem; padding: 1rem; margin-bottom: 0.65rem;
}
.hashtag-pill {
    display: inline-block; background: rgba(212,175,55,0.18);
    border: 1.5px solid rgba(212,175,55,0.45); color: #FFD040;
    padding: 0.25rem 0.7rem; border-radius: 999px; font-size: 0.78rem; margin: 0.18rem;
    font-weight: 800;
}
.scene-card {
    background: #1A1206; border-right: 4px solid #FFD840;
    border-radius: 0.6rem; padding: 1rem; margin-bottom: 0.7rem;
}
.step-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(212,175,55,0.20); border: 2px solid rgba(212,175,55,0.60);
    color: #FFE060; padding: 0.4rem 1.1rem; border-radius: 999px;
    font-size: 0.9rem; font-weight: 900; margin-bottom: 0.8rem;
    letter-spacing: 0.02rem;
}
.video-card {
    background: linear-gradient(135deg, #0D0A1A, #1A1030);
    border: 2px solid rgba(120,80,220,0.50); border-radius: 1rem;
    padding: 1.4rem; margin-bottom: 1rem;
}
.video-card h3 { color: #C0A0FF; font-size: 1.1rem; margin: 0 0 0.8rem; font-weight: 900; }
.video-status-pending {
    background: rgba(251,191,36,0.15); border: 1.5px solid #fbbf24;
    border-radius: 0.65rem; padding: 0.8rem 1rem; color: #FFE070;
    font-size: 0.9rem; font-weight: 800; text-align: center;
}
.video-status-done {
    background: rgba(52,211,153,0.15); border: 1.5px solid #34d399;
    border-radius: 0.65rem; padding: 0.8rem 1rem; color: #A0FFD8;
    font-size: 0.9rem; font-weight: 800; text-align: center;
}
.video-status-error {
    background: rgba(239,68,68,0.15); border: 1.5px solid #ef4444;
    border-radius: 0.65rem; padding: 0.8rem 1rem; color: #FFB0B0;
    font-size: 0.9rem; font-weight: 800; text-align: center;
}
.flow-prompt {
    background: #030200; border: 1px solid rgba(100,200,80,0.30);
    border-radius: 0.55rem; padding: 0.8rem; margin-top: 0.5rem;
    font-family: 'Courier New', monospace; font-size: 0.74rem;
    color: #90D860; line-height: 1.7; direction: ltr; text-align: left;
    white-space: pre-wrap; max-height: 200px; overflow-y: auto;
}
.warning-box {
    background: rgba(251,191,36,0.15); border: 2px solid rgba(251,191,36,0.65);
    border-radius: 0.7rem; padding: 0.9rem; margin-bottom: 0.6rem;
    color: #FFE880; font-size: 0.9rem; font-weight: 800;
}
.api-badge-ok {
    display: inline-block; background: rgba(52,211,153,0.15);
    border: 1.5px solid #34d399; color: #A0FFD8;
    padding: 0.2rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 800;
}
.api-badge-no {
    display: inline-block; background: rgba(239,68,68,0.15);
    border: 1.5px solid #ef4444; color: #FFB0B0;
    padding: 0.2rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 800;
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.loading-bar {
    background: linear-gradient(90deg, #1E1004 25%, #4A2800 50%, #1E1004 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 0.3rem; height: 4px; margin: 0.5rem 0;
}
</style>
<script>
function copyText(id) {
    var el = document.getElementById(id);
    if (el) { navigator.clipboard.writeText(el.innerText || el.value); }
}
</script>
"""


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _pil_resize(img_bytes: bytes, target_w: int, target_h: int) -> bytes:
    try:
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert("RGB")
        img = img.resize((target_w, target_h), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95, optimize=True)
        return buf.getvalue()
    except:
        return img_bytes


def _create_zip(images: dict, info: dict) -> bytes:
    buf = io.BytesIO()
    brand = info.get("brand", "mahwous").replace(" ", "_").lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for key, data in images.items():
            if data.get("bytes"):
                resized = _pil_resize(data["bytes"], data["w"], data["h"])
                fname = f"{key}_{data['w']}x{data['h']}.jpg"
                zf.writestr(fname, resized)
        meta = {
            "brand": info.get("brand"),
            "product_name": info.get("product_name"),
            "generated_at": datetime.now().isoformat(),
            "platforms": list(images.keys()),
            "source": "Mahwous AI Studio v13.0"
        }
        zf.writestr("info.json", json.dumps(meta, ensure_ascii=False, indent=2))
    buf.seek(0)
    return buf.read()


def _info_card(info: dict):
    colors = info.get("colors", [])
    color_dots = "".join([
        f"<span style='display:inline-block;width:16px;height:16px;border-radius:50%;background:{c};border:1.5px solid rgba(255,255,255,0.25);margin:0 0.2rem;vertical-align:middle;' title='{c}'></span>"
        for c in colors[:4]
    ])
    tags_html = ""
    for tag in [info.get("type"), info.get("size"), info.get("gender"), info.get("style")]:
        if tag:
            tags_html += f"<span class='tag'>{tag}</span>"
    conf = info.get("confidence", 0)
    conf_str = f"🎯 دقة التحليل: {int(conf*100)}%" if conf else ""
    st.markdown(f"""
    <div class="analysis-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="brand">{info.get('brand', '—')}</div>
                <div class="name">{info.get('product_name', '—')}</div>
                <div style="margin-top:0.5rem;">{tags_html}</div>
            </div>
            <div style="text-align:left; min-width:120px;">
                <div>{color_dots}</div>
                <div style="color:#706040; font-size:0.72rem; margin-top:0.4rem;">{conf_str}</div>
            </div>
        </div>
        <div style="margin-top:0.75rem; color:#A09070; font-size:0.8rem; line-height:1.5;">
            <strong style="color:#906030;">الزجاجة:</strong> {info.get('bottle_shape', '—')}<br>
            <strong style="color:#906030;">المزاج:</strong> {info.get('mood', '—')} · 
            <strong style="color:#906030;">الملاحظات:</strong> {info.get('notes_guess', '—')}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Platform Selector ────────────────────────────────────────────────────────
def platform_selector() -> list:
    if "selected_platforms" not in st.session_state:
        st.session_state.selected_platforms = ["instagram_post"]

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<div style='color:#D4AF37; font-weight:700; font-size:0.9rem;'>🎯 اختر المنصات</div>", unsafe_allow_html=True)
    if c2.button("🗑️ مسح الكل", use_container_width=True, key="clear_platforms"):
        st.session_state.selected_platforms = []
        st.rerun()

    cols = st.columns(len(PLATFORMS))
    for col, key in zip(cols, PLATFORMS.keys()):
        plat = PLATFORMS[key]
        is_sel = key in st.session_state.selected_platforms
        if col.button(
            f"{plat['emoji']} {'✓' if is_sel else '○'}",
            key=f"plat_{key}",
            help=plat["label"],
            use_container_width=True,
            type="primary" if is_sel else "secondary"
        ):
            if is_sel:
                st.session_state.selected_platforms.remove(key)
            else:
                st.session_state.selected_platforms.append(key)
            st.rerun()

    return st.session_state.selected_platforms


def _show_how_it_works():
    st.markdown("""
    <div style='background:rgba(212,175,55,0.06); border:1px solid rgba(212,175,55,0.20);
         border-radius:0.75rem; padding:1.2rem; margin-top:1rem;'>
      <div style='color:#F5D060; font-size:0.95rem; font-weight:900; margin-bottom:0.8rem;'>🚀 كيف يعمل الاستديو؟</div>
      <div style='color:#D0B070; font-size:0.85rem; line-height:2;'>
        1️⃣ ارفع صورة العطر أو أدخل البيانات يدوياً<br>
        2️⃣ اختر المنصات المطلوبة<br>
        3️⃣ انقر "توليد الصور" لإنشاء محتوى جاهز لكل منصة<br>
        4️⃣ استخدم تبويب الفيديو لتوليد فيديو سينمائي مباشرة<br>
        5️⃣ حمّل الصور والفيديوهات بصيغة ZIP
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── ✅ تبويب توليد الفيديو المباشر ──────────────────────────────────────────
def _show_video_generation_tab(perfume_info: dict):
    """تبويب توليد الفيديو المباشر — Luma + RunwayML + Fal.ai"""
    st.markdown("""
    <div class="video-card">
      <h3>🎬 توليد فيديو سينمائي مباشرة</h3>
      <div style='color:#A090D0; font-size:0.85rem;'>
        Luma Dream Machine · RunwayML Gen-3 · Fal.ai (Kling/Veo/SVD) — فيديو احترافي في دقائق
      </div>
    </div>
    """, unsafe_allow_html=True)

    secrets = _get_secrets()
    has_luma   = bool(secrets["luma"])
    has_runway = bool(secrets["runway"])
    has_fal    = bool(secrets["fal"])

    # حالة المفاتيح
    col_l, col_r, col_f = st.columns(3)
    with col_l:
        if has_luma:
            st.markdown("<span class='api-badge-ok'>🟢 Luma Dream Machine متصل</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='api-badge-no'>🔴 Luma — أضف LUMA_API_KEY في الإعدادات</span>", unsafe_allow_html=True)
    with col_r:
        if has_runway:
            st.markdown("<span class='api-badge-ok'>🟢 RunwayML Gen-3 متصل</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='api-badge-no'>🔴 RunwayML — أضف RUNWAY_API_KEY في الإعدادات</span>", unsafe_allow_html=True)
    with col_f:
        if has_fal:
            st.markdown("<span class='api-badge-ok'>🟢 Fal.ai متصل</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='api-badge-no'>🔴 Fal.ai — أضف FAL_API_KEY في الإعدادات</span>", unsafe_allow_html=True)

    if not has_luma and not has_runway and not has_fal:
        st.warning("⚠️ أضف مفتاح Luma أو RunwayML أو FAL في الإعدادات لتفعيل توليد الفيديو")
        with st.expander("📋 كيف أحصل على مفاتيح API الفيديو؟"):
            st.markdown("""
            <div style='color:#D0B070; font-size:0.88rem; line-height:2;'>
            <strong style='color:#F5D060;'>Luma Dream Machine:</strong><br>
            1. افتح <a href="https://lumalabs.ai" target="_blank" style="color:#C0A0FF;">lumalabs.ai</a><br>
            2. سجّل حساباً → API → Create Key<br>
            3. أضف المفتاح في الإعدادات كـ LUMA_API_KEY<br><br>
            <strong style='color:#F5D060;'>RunwayML Gen-3:</strong><br>
            1. افتح <a href="https://runwayml.com" target="_blank" style="color:#C0A0FF;">runwayml.com</a><br>
            2. سجّل حساباً → API → Generate Token<br>
            3. أضف المفتاح في الإعدادات كـ RUNWAY_API_KEY<br><br>
            <strong style='color:#F5D060;'>Fal.ai (Kling/Veo/SVD):</strong><br>
            1. افتح <a href="https://fal.ai" target="_blank" style="color:#C0A0FF;">fal.ai</a><br>
            2. سجّل حساباً → API Keys → Create<br>
            3. أضف المفتاح في الإعدادات كـ FAL_API_KEY
            </div>
            """, unsafe_allow_html=True)
        return

    st.markdown("---")

    # بناء قائمة مزودي الفيديو المتاحين
    provider_options = []
    if has_luma:
        provider_options.append("luma")
    if has_runway:
        provider_options.append("runway")
    if has_fal:
        provider_options.append("fal")
    if not provider_options:
        provider_options = ["luma"]

    # إعدادات الفيديو
    vc1, vc2 = st.columns(2)
    with vc1:
        video_provider = st.selectbox(
            "🎬 منصة التوليد",
            options=provider_options,
            format_func=lambda x: {"luma": "Luma Dream Machine", "runway": "RunwayML Gen-3", "fal": "Fal.ai (Kling/Veo/SVD)"}.get(x, x),
            key="video_provider"
        )
    with vc2:
        video_duration = st.select_slider(
            "⏱️ مدة الفيديو",
            options=[5, 7, 10, 15],
            value=7,
            key="video_duration"
        )

    # نموذج Fal.ai (يظهر فقط عند اختيار Fal)
    fal_video_model = "kling"  # قيمة افتراضية
    if video_provider == "fal":
        fal_video_model = st.selectbox(
            "🤖 نموذج Fal.ai للفيديو",
            options=["kling", "veo", "svd"],
            format_func=lambda x: {"kling": "Kling v1.6", "veo": "Veo 2", "svd": "Stable Video (SVD)"}.get(x, x),
            key="fal_video_model",
            help="Kling: أفضل للفيديو الاحترافي · Veo: جودة عالية · SVD: سريع وخفيف"
        )

    vr1, vr2 = st.columns(2)
    with vr1:
        video_scene = st.selectbox(
            "🎬 الموقع",
            options=["store", "beach", "desert", "studio", "garden", "rooftop", "car"],
            format_func=lambda x: {
                "store": "🏪 متجر العطور", "beach": "🌅 شاطئ الغروب",
                "desert": "🏜️ صحراء ذهبية", "studio": "🎬 استديو فاخر",
                "garden": "🌹 حديقة ملكية", "rooftop": "🌆 سطح ناطحة سحاب",
                "car": "🚗 سيارة فارهة"
            }.get(x, x),
            key="video_scene"
        )
    with vr2:
        video_outfit = st.selectbox(
            "👔 الزي",
            options=list(MAHWOUS_OUTFITS.keys()),
            format_func=lambda x: {
                "suit": "🤵 البدلة الفاخرة", "hoodie": "🏆 الهودي الأيقوني",
                "thobe": "👘 الثوب الملكي", "casual": "👕 الكاجوال الأنيق",
                "western": "🤠 غربي (Leather) 🆕"
            }.get(x, x),
            key="video_outfit"
        )

    video_scene_type = st.radio(
        "نوع المشهد",
        ["مهووس مع العطر", "العطر يتكلم وحده", "مهووس بدون عطر"],
        horizontal=True,
        key="video_scene_type"
    )

    # إعدادات متقدمة (مخفية لتسهيل التجربة)
    with st.expander("⚙️ إعدادات متقدمة (الكاميرا، الأبعاد، الإضافات)"):
        ac1, ac2 = st.columns(2)
        with ac1:
            video_aspect = st.selectbox("📐 نسبة العرض", ["9:16", "16:9", "1:1"], index=0, key="video_aspect")
        with ac2:
            video_camera = st.selectbox(
                "📷 حركة الكاميرا",
                options=["push_in", "zoom", "orbit", "static", "low_rise", "dolly", "crane"],
                format_func=lambda x: {
                    "push_in": "Push In — اقتراب", "zoom": "Zoom — تكبير",
                    "orbit": "Orbit — دوران", "static": "Static — ثابت",
                    "low_rise": "Low Rise — من الأسفل", "dolly": "Dolly — تتبع",
                    "crane": "Crane — من الأعلى"
                }.get(x, x),
                key="video_camera"
            )
        video_extra = st.text_input("✨ إضافات خاصة", placeholder="مثال: مطر ذهبي، بتلات ورد...", key="video_extra")

    has_char_ref = "char_ref_bytes" in st.session_state
    video_ref_source = st.radio(
        "🖼️ مصدر الصورة المرجعية",
        options=["none", "video_upload"] + (["char_ref"] if has_char_ref else []),
        format_func=lambda x: {"none": "بدون مرجع", "video_upload": "ارفع صورة", "char_ref": "استخدم مرجع الشخصية"}.get(x, x),
        key="video_ref_source",
        help="استخدم مرجع الشخصية المُختار أو ارفع صورة خاصة بالفيديو"
    )

    video_ref_img = None
    if video_ref_source == "video_upload":
        video_ref_img = st.file_uploader(
            "📤 ارفع صورة مرجعية للفيديو",
            type=["jpg", "jpeg", "png"],
            key="video_ref_upload",
            help="ارفع صورة لتحويلها إلى فيديو متحرك"
        )

    # بناء البرومت
    video_prompt = build_video_prompt(
        perfume_info,
        scene=video_scene,
        outfit=video_outfit,
        camera=st.session_state.get("video_camera", "orbit"),
        duration=st.session_state.get("video_duration", 7),
        aspect=st.session_state.get("video_aspect", "9:16"),
        extra=st.session_state.get("video_extra", ""),
    )
    with st.expander("👁️ معاينة برومت الفيديو"):
        st.markdown(f'<div class="flow-prompt">{video_prompt}</div>', unsafe_allow_html=True)
        if st.button("📋 نسخ البرومت", key="copy_vid_prompt"):
            st.code(video_prompt, language="text")

    st.markdown("---")

    # ── زر التوليد ──
    provider_label = {"luma": "Luma Dream Machine", "runway": "RunwayML Gen-3", "fal": "Fal.ai"}.get(video_provider, video_provider)
    gen_col1, gen_col2 = st.columns([2, 1])
    with gen_col1:
        generate_video_btn = st.button(
            f"🎬 توليد الفيديو الآن — {provider_label}",
            type="primary",
            use_container_width=True,
            key="generate_video_btn"
        )
    with gen_col2:
        loop_video = st.checkbox("🔄 فيديو حلقي (Loop)", value=False, key="loop_video")

    if generate_video_btn:
        # تحديد بايتات الصورة المرجعية
        if video_ref_source == "char_ref":
            ref_bytes = st.session_state.get("char_reference_bytes")
        elif video_ref_source == "video_upload":
            ref_bytes = video_ref_img.getvalue() if video_ref_img else None
        else:
            ref_bytes = None

        with st.spinner(f"⚡ جاري إرسال طلب التوليد إلى {provider_label}..."):
            if video_provider == "luma":
                result = generate_video_luma(
                    prompt=video_prompt,
                    image_bytes=ref_bytes,
                    duration=video_duration,
                    aspect_ratio=video_aspect,
                    loop=loop_video
                )
            elif video_provider == "runway":
                result = generate_video_runway(
                    prompt=video_prompt,
                    image_bytes=ref_bytes,
                    aspect_ratio=video_aspect,
                    duration=video_duration,
                )
            else:  # fal
                result = generate_video_fal(
                    prompt=video_prompt,
                    model=fal_video_model,
                    aspect_ratio=video_aspect,
                    image_bytes=ref_bytes,
                )

        if result.get("error"):
            st.markdown(f"<div class='video-status-error'>❌ {result['error']}</div>", unsafe_allow_html=True)
        elif result.get("state") == "completed" and result.get("video_url"):
            # Fal.ai أو أي مزود أعاد الفيديو فوراً
            video_url = result["video_url"]
            st.markdown(f"""
            <div class='video-status-done'>
              ✅ الفيديو جاهز!
              <a href="{video_url}" target="_blank" style="color:#A0FFD8; font-weight:900;">
                ← تحميل الفيديو
              </a>
            </div>
            """, unsafe_allow_html=True)
            st.video(video_url)
            st.session_state["video_url_ready"] = video_url
            st.session_state.gen_count = st.session_state.get("gen_count", 0) + 1
        else:
            gen_id = result.get("id", "")
            st.session_state["video_gen_id"] = gen_id
            st.session_state["video_gen_provider"] = video_provider
            st.markdown(f"""
            <div class='video-status-pending'>
              ⏳ تم إرسال الطلب بنجاح! معرّف التوليد: <code>{gen_id}</code><br>
              الفيديو قيد المعالجة — عادةً يستغرق 2-5 دقائق
            </div>
            """, unsafe_allow_html=True)
            st.session_state.gen_count = st.session_state.get("gen_count", 0) + 1

    # ── فحص حالة الفيديو ──
    if "video_gen_id" in st.session_state and st.session_state["video_gen_id"]:
        st.markdown("---")
        st.markdown("### 📊 حالة الفيديو")
        gen_id = st.session_state["video_gen_id"]
        provider = st.session_state.get("video_gen_provider", "luma")

        check_col1, check_col2 = st.columns(2)
        with check_col1:
            if st.button("🔄 فحص الحالة الآن", use_container_width=True, key="check_video_status"):
                with st.spinner("جاري الفحص..."):
                    if provider == "luma":
                        status = check_luma_status(gen_id)
                    elif provider == "fal":
                        status = check_fal_video_status(gen_id)
                    else:
                        status = check_runway_status(gen_id)

                state = status.get("state", "")
                video_url = status.get("video_url", "")

                if state == "completed" and video_url:
                    st.markdown(f"""
                    <div class='video-status-done'>
                      ✅ الفيديو جاهز! 
                      <a href="{video_url}" target="_blank" style="color:#A0FFD8; font-weight:900;">
                        ← تحميل الفيديو
                      </a>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video(video_url)
                    st.session_state["video_url_ready"] = video_url
                elif state in ["failed", "error"]:
                    err = status.get("error", "خطأ غير معروف")
                    st.markdown(f"<div class='video-status-error'>❌ فشل التوليد: {err}</div>", unsafe_allow_html=True)
                else:
                    progress = status.get("progress", 0)
                    st.markdown(f"""
                    <div class='video-status-pending'>
                      ⏳ الحالة: {state} — التقدم: {int(progress*100) if progress else '?'}%<br>
                      انتظر قليلاً ثم انقر "فحص الحالة" مجدداً
                    </div>
                    """, unsafe_allow_html=True)

        with check_col2:
            if st.button("⏳ انتظار تلقائي (5 دقائق)", use_container_width=True, key="wait_video"):
                progress_bar = st.progress(0, text="⏳ في انتظار اكتمال الفيديو...")
                for i in range(30):
                    time_wait = i / 30
                    progress_bar.progress(time_wait, text=f"⏳ انتظار... {i*10} ثانية")
                    if provider == "luma":
                        status = check_luma_status(gen_id)
                    elif provider == "fal":
                        status = check_fal_video_status(gen_id)
                    else:
                        status = check_runway_status(gen_id)
                    if status.get("state") == "completed":
                        video_url = status.get("video_url", "")
                        progress_bar.progress(1.0, text="✅ الفيديو جاهز!")
                        st.markdown(f"""
                        <div class='video-status-done'>
                          ✅ الفيديو جاهز! 
                          <a href="{video_url}" target="_blank" style="color:#A0FFD8; font-weight:900;">
                            ← تحميل الفيديو
                          </a>
                        </div>
                        """, unsafe_allow_html=True)
                        st.video(video_url)
                        st.session_state["video_url_ready"] = video_url
                        break
                    elif status.get("state") in ["failed", "error"]:
                        progress_bar.progress(1.0, text="❌ فشل التوليد")
                        st.error(f"فشل: {status.get('error', '')}")
                        break
                    import time as time_module
                    time_module.sleep(10)

        # عرض الفيديو إذا كان جاهزاً
        if "video_url_ready" in st.session_state:
            st.markdown(f"""
            <div style='background:rgba(52,211,153,0.10); border:1.5px solid #34d399;
                 border-radius:0.65rem; padding:0.8rem; margin-top:0.5rem; text-align:center;'>
              <a href="{st.session_state['video_url_ready']}" target="_blank"
                 style='color:#A0FFD8; font-weight:900; font-size:1rem;'>
                ⬇️ تحميل الفيديو المكتمل ←
              </a>
            </div>
            """, unsafe_allow_html=True)

        # مسح الجلسة
        if st.button("🗑️ مسح وبدء فيديو جديد", key="clear_video_session"):
            for k in ["video_gen_id", "video_gen_provider", "video_url_ready"]:
                st.session_state.pop(k, None)
            st.rerun()


# ─── ✅ تبويب توليد الصورة المفردة ───────────────────────────────────────────
def _show_single_image_tab(perfume_info: dict):
    """توليد صورة مفردة مخصصة"""
    st.markdown("### 🖼️ توليد صورة مخصصة")

    si1, si2 = st.columns(2)
    with si1:
        img_type = st.selectbox(
            "نوع التوليد",
            ["مهووس مع العطر", "العطر وحده", "رمضاني", "✨ ريمكس (تغيير الخلفية)"],
            key="single_img_type"
        )
    with si2:
        img_outfit = st.selectbox(
            "الزي",
            list(MAHWOUS_OUTFITS.keys()),
            format_func=lambda x: {
                "suit": "🤵 البدلة", "hoodie": "🏆 الهودي",
                "thobe": "👘 الثوب", "casual": "👕 الكاجوال",
                "western": "🤠 غربي 🆕"
            }.get(x, x),
            key="single_img_outfit"
        )
        img_scene = st.selectbox(
            "المكان",
            ["store", "beach", "desert", "studio", "garden", "rooftop", "car"],
            format_func=lambda x: {
                "store": "🏪 متجر", "beach": "🌅 شاطئ",
                "desert": "🏜️ صحراء", "studio": "🎬 استديو",
                "garden": "🌹 حديقة", "rooftop": "🌆 سطح", "car": "🚗 سيارة"
            }.get(x, x),
            key="single_img_scene"
        )

    with st.expander("⚙️ إعدادات إضافية"):
        img_aspect = st.selectbox(
            "نسبة العرض",
            ["1:1", "9:16", "16:9", "2:3"],
            key="single_img_aspect"
        )
        img_extra = st.text_input("✨ إضافات خاصة", placeholder="مثال: golden rain, rose petals", key="single_img_extra")

    remix_bytes = None
    if img_type == "✨ ريمكس (تغيير الخلفية)":
        st.info("ℹ️ ارفع صورة العطر الأصلية وسيتم تغيير الخلفية مع الحفاظ على شكل العطر")
        remix_file = st.file_uploader("📤 صورة العطر الأصلية", type=["jpg","jpeg","png"], key="remix_upload")
        if remix_file:
            remix_bytes = remix_file.getvalue()
            st.image(remix_bytes, width=200, caption="الأصلية")
        remix_strength = st.slider("قوة التعديل", 0.3, 0.9, 0.6, 0.05, key="remix_strength")

    if st.button("🎨 توليد الصورة الآن", type="primary", use_container_width=True, key="gen_single_img"):
        prompt = ""
        if img_type == "مهووس مع العطر":
            prompt = build_mahwous_product_prompt(perfume_info, img_outfit, img_scene, img_aspect)
        elif img_type == "العطر وحده":
            prompt = build_product_only_prompt(perfume_info, img_aspect)
        elif img_type == "✨ ريمكس (تغيير الخلفية)":
            prompt = f"High quality photo of perfume bottle with new artistic background, same product"
        elif img_type == "🌙 وضع رمضان":
            prompt = build_ramadan_product_prompt(perfume_info, img_aspect)

        if img_extra:
            prompt += f"\nAdditional: {img_extra}"

        with st.spinner("🎨 جاري توليد الصورة..."):
            img_bytes = None
            try:
                if img_type == "✨ ريمكس (تغيير الخلفية)" and remix_bytes:
                    img_bytes = generate_image_remix_fal(prompt, remix_bytes, remix_strength)
                else:
                    img_bytes = smart_generate_image(prompt, img_aspect)
            except Exception as e:
                st.error(f"❌ فشل توليد الصورة: {e}")

            if img_bytes:
                st.image(img_bytes, caption=f"✅ {img_type}", use_container_width=True)
                st.download_button(
                    "⬇️ تحميل الصورة",
                    img_bytes,
                    f"mahwous_{img_type}_{img_aspect.replace(':','x')}.jpg",
                    "image/jpeg",
                    use_container_width=True
                )


# ─── Smart Trends Panel ───────────────────────────────────────────────────────
def _show_smart_trends_panel(perfume_info: dict):
    """لوحة ترندات ذكية مدمجة — تظهر تلقائياً بعد تحديد المنتج"""
    product_key = f"trends_{perfume_info.get('product_name','')}"

    # تحقق هل يوجد ترند محفوظ لهذا المنتج
    cached = st.session_state.get(product_key)

    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.markdown("""
        <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:0.4rem;'>
          <span style='font-size:1.4rem;'>🔥</span>
          <span style='color:#FFE060; font-size:1rem; font-weight:900;'>ترندات ذكية مقترحة</span>
          <span style='color:#906030; font-size:0.8rem;'> — بناءً على هذا المنتج</span>
        </div>
        """, unsafe_allow_html=True)
    with btn_col:
        refresh = st.button(
            "⚡ تحليل" if not cached else "🔄 تحديث",
            key=f"refresh_trends_{product_key}",
            use_container_width=True,
            help="تحليل ترندات المنتج بالذكاء الاصطناعي"
        )

    if refresh or not cached:
        with st.spinner("🔄 جاري تحليل الترندات..."):
            try:
                data = generate_trend_insights(perfume_info)
                st.session_state[product_key] = data
                cached = data
            except Exception as e:
                st.warning(f"⚠️ تعذّر تحليل الترندات: {e}")
                return

    if not cached or "error" in cached:
        if cached and "error" in cached:
            st.caption(f"⚠️ {cached['error']}")
        return

    # ── عرض مضغوط ──
    if cached.get("product_summary"):
        st.markdown(
            f"<div style='background:rgba(212,175,55,0.08); border-right:3px solid #F0CC55; "
            f"padding:0.5rem 0.8rem; border-radius:0 0.4rem 0.4rem 0; color:#FFE8A0; "
            f"font-size:0.88rem; margin-bottom:0.6rem;'>💡 {cached['product_summary']}</div>",
            unsafe_allow_html=True
        )

    # أبرز 3 ترندات
    topics = cached.get("trending_topics", [])[:3]
    if topics:
        cols = st.columns(len(topics))
        platform_colors = {"TikTok": "#FF2D55", "Instagram": "#C13584", "Twitter": "#1DA1F2"}
        for col, t in zip(cols, topics):
            with col:
                plat = t.get("platform", "")
                color = platform_colors.get(plat, "#A090D0")
                st.markdown(f"""
                <div style='background:#1A1206; border:1.5px solid rgba(212,175,55,0.25);
                     border-radius:0.6rem; padding:0.7rem; height:100%;'>
                  <div style='color:{color}; font-size:0.72rem; font-weight:900; margin-bottom:0.3rem;'>
                    {plat}
                  </div>
                  <div style='color:#FFE060; font-size:0.85rem; font-weight:800;'>{t.get('topic','')}</div>
                  <div style='color:#A09070; font-size:0.75rem; margin-top:0.3rem; line-height:1.4;'>
                    {t.get('hook','')[:80]}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # أبرز هوكين
    hooks = cached.get("viral_hooks", [])[:2]
    if hooks:
        st.markdown("<div style='margin-top:0.5rem;'>", unsafe_allow_html=True)
        for h in hooks:
            st.markdown(
                f"<div style='background:rgba(255,60,60,0.08); border:1px solid rgba(255,60,60,0.30); "
                f"border-radius:0.5rem; padding:0.4rem 0.8rem; color:#FFB8B8; font-size:0.82rem; "
                f"margin-bottom:0.3rem;'>🎯 {h}</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("💡 انتقل إلى تبويب 🔥 ترند ذكي للتفاصيل الكاملة")


def _show_trends_tab(perfume_info: dict):
    """تبويب الترندات الذكية الكامل"""
    st.markdown("""
    <div class="video-card">
      <h3>🔥 ترند ذكي</h3>
      <div style='color:#A090D0; font-size:0.85rem;'>
        تحليل المنتج واقتراح مواضيع ترند فيروسية · هوكات صادمة · زوايا محتوى جديدة
      </div>
    </div>
    """, unsafe_allow_html=True)

    product_key = f"trends_{perfume_info.get('product_name','')}"
    cached = st.session_state.get(product_key)

    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        if st.button("🔥 تحليل الترندات الآن", type="primary", use_container_width=True, key="trends_full_btn"):
            with st.spinner("🔍 يحلل الذكاء الاصطناعي المنتج ويبحث عن الترندات..."):
                try:
                    data = generate_trend_insights(perfume_info)
                    st.session_state[product_key] = data
                    cached = data
                    st.session_state.gen_count = st.session_state.get("gen_count", 0) + 1
                except Exception as e:
                    st.error(f"❌ خطأ في التحليل: {e}")
    with btn_col2:
        if cached and st.button("🗑️ مسح", use_container_width=True, key="trends_clear_btn"):
            st.session_state.pop(product_key, None)
            st.rerun()

    if not cached:
        st.info("💡 انقر 'تحليل الترندات الآن' لتحليل المنتج وإيجاد أفضل المواضيع الرائجة")
        return

    if "error" in cached:
        st.error(cached["error"])
        return

    # ── ملخص المنتج والجمهور ───────────────────────────────────────
    if cached.get("product_summary") or cached.get("target_audience"):
        st.markdown("#### 🎯 تشخيص المنتج")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style='background:rgba(212,175,55,0.08); border:1.5px solid rgba(212,175,55,0.35);
                 border-radius:0.7rem; padding:1rem;'>
              <div style='color:#F5D060; font-weight:900; font-size:0.85rem; margin-bottom:0.4rem;'>
                💡 هوية العطر
              </div>
              <div style='color:#E8D5A0; font-size:0.9rem; line-height:1.6;'>
                {cached.get('product_summary','—')}
              </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style='background:rgba(60,120,255,0.08); border:1.5px solid rgba(60,120,255,0.30);
                 border-radius:0.7rem; padding:1rem;'>
              <div style='color:#A0C0FF; font-weight:900; font-size:0.85rem; margin-bottom:0.4rem;'>
                👥 الجمهور المستهدف
              </div>
              <div style='color:#C0D8FF; font-size:0.9rem; line-height:1.6;'>
                {cached.get('target_audience','—')}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── المواضيع الترند ───────────────────────────────────────────
    topics = cached.get("trending_topics", [])
    if topics:
        st.markdown("#### 🔥 المواضيع الرائجة المقترحة")
        platform_colors = {"TikTok": "#FF2D55", "Instagram": "#C13584", "Twitter": "#1DA1F2"}
        for t in topics:
            plat = t.get("platform", "")
            color = platform_colors.get(plat, "#A090D0")
            st.markdown(f"""
            <div style='background:#1A1206; border:1.5px solid rgba(212,175,55,0.25);
                 border-left:4px solid {color}; border-radius:0 0.6rem 0.6rem 0;
                 padding:0.9rem 1rem; margin-bottom:0.7rem;'>
              <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                  <span style='color:{color}; font-size:0.75rem; font-weight:900;'>{plat}</span>
                  <span style='color:#FFE060; font-size:1rem; font-weight:900; margin-right:0.5rem;'>
                    {t.get('topic','')}
                  </span>
                </div>
              </div>
              <div style='color:#A09070; font-size:0.82rem; margin-top:0.4rem;'>
                🔗 {t.get('relevance','')}
              </div>
              <div style='background:rgba(255,60,60,0.10); border:1px solid rgba(255,60,60,0.25);
                   border-radius:0.4rem; padding:0.4rem 0.7rem; margin-top:0.5rem;
                   color:#FFB8B8; font-size:0.85rem;'>
                🎯 الهوك: {t.get('hook','')}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── هوكات فيروسية ─────────────────────────────────────────────
    hooks = cached.get("viral_hooks", [])
    if hooks:
        st.markdown("#### 💥 هوكات فيروسية جاهزة")
        for i, h in enumerate(hooks, 1):
            st.markdown(f"""
            <div style='background:rgba(255,60,60,0.08); border:1.5px solid rgba(255,60,60,0.35);
                 border-radius:0.6rem; padding:0.7rem 1rem; margin-bottom:0.5rem;
                 color:#FFD0D0; font-size:0.92rem; font-weight:800;'>
              {i}. {h}
            </div>
            """, unsafe_allow_html=True)

    # ── زوايا المحتوى ─────────────────────────────────────────────
    angles = cached.get("content_angles", [])
    if angles:
        st.markdown("#### 🎬 زوايا محتوى جديدة")
        ac1, ac2 = st.columns(2)
        for i, a in enumerate(angles):
            with (ac1 if i % 2 == 0 else ac2):
                fmt = a.get("format", "")
                fmt_color = "#FF2D55" if "ريلز" in fmt else "#C13584" if "بوست" in fmt else "#1DA1F2"
                st.markdown(f"""
                <div style='background:#1A1206; border:1.5px solid rgba(212,175,55,0.20);
                     border-radius:0.6rem; padding:0.8rem; margin-bottom:0.6rem; height:100%;'>
                  <div style='display:flex; justify-content:space-between; margin-bottom:0.4rem;'>
                    <span style='color:#FFE060; font-weight:900; font-size:0.88rem;'>
                      {a.get('angle','')}
                    </span>
                    <span style='color:{fmt_color}; font-size:0.75rem; font-weight:800;
                         background:rgba(255,255,255,0.06); padding:0.1rem 0.5rem;
                         border-radius:999px;'>{fmt}</span>
                  </div>
                  <div style='color:#C0A870; font-size:0.82rem; line-height:1.5;'>
                    {a.get('description','')}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── الهاشتاقات الرائجة ────────────────────────────────────────
    t_tags = cached.get("trending_hashtags", {})
    if t_tags:
        st.markdown("#### #️⃣ الهاشتاقات الرائجة المقترحة")
        th1, th2 = st.columns(2)
        with th1:
            viral = t_tags.get("viral", [])
            if viral:
                st.markdown("**🔥 فيروسية**")
                st.markdown(
                    " ".join(f"<span class='hashtag-pill'>{h}</span>" for h in viral),
                    unsafe_allow_html=True
                )
            niche = t_tags.get("niche", [])
            if niche:
                st.markdown("**🎯 متخصصة**")
                st.markdown(
                    " ".join(f"<span class='hashtag-pill'>{h}</span>" for h in niche),
                    unsafe_allow_html=True
                )
        with th2:
            buying = t_tags.get("buying", [])
            if buying:
                st.markdown("**🛍️ شرائية**")
                st.markdown(
                    " ".join(f"<span class='hashtag-pill'>{h}</span>" for h in buying),
                    unsafe_allow_html=True
                )

    # ── أوقات النشر وفرص إضافية ───────────────────────────────────
    times = cached.get("best_post_times", {})
    gap   = cached.get("competitor_gap", "")
    season = cached.get("seasonal_angle", "")

    if times or gap or season:
        st.markdown("---")
        bt1, bt2, bt3 = st.columns(3)
        if times:
            with bt1:
                st.markdown("#### 🕐 أفضل أوقات النشر")
                for plat, t in times.items():
                    st.markdown(
                        f"<div style='color:#D4B870; font-size:0.83rem; margin-bottom:0.3rem;'>"
                        f"<strong>{plat}:</strong> {t}</div>",
                        unsafe_allow_html=True
                    )
        if gap:
            with bt2:
                st.markdown("#### 💎 فرصة غير مستغلة")
                st.markdown(
                    f"<div style='background:rgba(80,200,80,0.08); border:1.5px solid rgba(80,200,80,0.30); "
                    f"border-radius:0.6rem; padding:0.8rem; color:#A0EFA0; font-size:0.85rem; "
                    f"line-height:1.5;'>{gap}</div>",
                    unsafe_allow_html=True
                )
        if season:
            with bt3:
                st.markdown("#### 📅 الزاوية الموسمية")
                st.markdown(
                    f"<div style='background:rgba(255,200,50,0.08); border:1.5px solid rgba(255,200,50,0.30); "
                    f"border-radius:0.6rem; padding:0.8rem; color:#FFE8A0; font-size:0.85rem; "
                    f"line-height:1.5;'>{season}</div>",
                    unsafe_allow_html=True
                )

    # ── جاسوس المنافسين ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🕵️ جاسوس المنافسين")
    comp_name = st.text_input("اسم المنافس أو علامته التجارية", placeholder="مثال: Arabian Oud, Chanel...")
    if comp_name and st.button("تحليل المنافس", key="analyze_comp_btn"):
        with st.spinner("🕵️ جاري التجسس والتحليل..."):
            comp_data = analyze_competitor(perfume_info, comp_name)
            
            c1, c2 = st.columns(2)
            with c1:
                st.error(f"📉 نقطة ضعفهم: {comp_data.get('competitor_weakness')}")
                st.success(f"🚀 ميزتنا: {comp_data.get('our_advantage')}")
            with c2:
                st.warning(f"⚔️ زاوية الهجوم: {comp_data.get('attack_angle')}")
                st.info(f"🎬 محتوى مقترح: {comp_data.get('suggested_content')}")


# ─── Main Studio Page ──────────────────────────────────────────────────────────
def show_studio_page():
    st.markdown(STUDIO_CSS, unsafe_allow_html=True)

    # تحميل المفاتيح في بداية الصفحة
    secrets = _get_secrets()
    has_gemini     = bool(secrets.get("gemini"))
    has_openrouter = bool(secrets.get("openrouter"))
    has_luma       = bool(secrets.get("luma"))
    has_runway     = bool(secrets.get("runway"))
    has_fal        = bool(secrets.get("fal"))
    has_webhook    = bool(secrets.get("webhook"))

    # ─── History Sidebar (سجل التحليلات) ──────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📜 سجل التحليلات (History)")
        
        try:
            from modules.supabase_db import fetch_perfume_history
            _has_supabase = True
        except ImportError:
            _has_supabase = False
            fetch_perfume_history = lambda n: []
        
        # زر تحديث السجل
        if st.button("🔄 تحديث السجل", key="refresh_hist", use_container_width=True):
            st.session_state.history_items = fetch_perfume_history(15)
        
        # تحميل أولي للسجل إذا لم يكن موجوداً
        if "history_items" not in st.session_state:
            st.session_state.history_items = fetch_perfume_history(15)

        if not _has_supabase:
            st.caption("Supabase غير مفعل (اختياري)")
        elif not st.session_state.history_items:
            st.caption("لا يوجد سجل محفوظ في Supabase")
        else:
            for item in st.session_state.history_items:
                # عرض اسم العطر والعلامة التجارية
                label = f"{item.get('brand', '—')} | {item.get('product_name', '—')}"
                if st.button(label, key=f"hist_{item.get('id')}", use_container_width=True, help=f"تاريخ: {item.get('created_at')}"):
                    # استعادة البيانات
                    st.session_state.input_mode = "manual"
                    st.session_state.perfume_info_auto = {
                        "brand": item.get("brand"),
                        "product_name": item.get("product_name"),
                        "type": item.get("type"),
                        "gender": item.get("gender"),
                        "style": item.get("style"),
                        "mood": item.get("mood"),
                        "notes_guess": item.get("notes"),
                        "confidence": 1.0
                    }
                    st.toast(f"✅ تم استرجاع بيانات: {item.get('product_name')}")
                    st.rerun()

    st.markdown("""
    <div class="studio-hero">
      <h1>🎬 استديو مهووس الذكي</h1>
      <p class="sub">توليد صور · فيديو مباشر · تعليقات · سيناريوهات · هاشتاقات · لجميع المنصات</p>
      <div class="version-badge">v13.1 · GEMINI 2.0 + CLAUDE 3.5 + IMAGEN 3 + LUMA + RUNWAY</div>
    </div>
    """, unsafe_allow_html=True)


    # عرض حالة المفاتيح مع تسمية المشكلة
    api_keys = {
        "Gemini": secrets.get("gemini"),
        "OpenRouter": secrets.get("openrouter"),
        "Luma": secrets.get("luma"),
        "RunwayML": secrets.get("runway"),
        "Fal.ai": secrets.get("fal"),
        "ImgBB": secrets.get("imgbb"),
        "ElevenLabs": secrets.get("elevenlabs"),
    }
    api_status = []
    issues = []
    for name, key in api_keys.items():
        if key:
            api_status.append(f"🟢 {name}")
        else:
            api_status.append(f"🔴 {name}")
            issues.append(f"❌ مفتاح {name} مفقود أو غير صحيح")
    st.markdown(f"""
    <div style='background:rgba(212,175,55,0.06); border:1px solid rgba(212,175,55,0.20);
         border-radius:0.6rem; padding:0.6rem 1rem; margin-bottom:1rem;
         display:flex; gap:1.5rem; flex-wrap:wrap;'>
      {"".join(f"<span style='color:#D4B870; font-size:0.85rem; font-weight:700;'>{s}</span>" for s in api_status)}
    </div>
    """, unsafe_allow_html=True)
    if issues:
        st.markdown(
            "<div style='background:rgba(239,68,68,0.12); border:1.5px solid #ef4444; border-radius:0.65rem; "
            f"padding:0.8rem 1rem; font-weight:700; color:#FFB0B0;'>{'<br>'.join(issues)}</div>",
            unsafe_allow_html=True
        )

    if not has_gemini:
        st.markdown("<div class='warning-box'>⚠️ <strong>GEMINI_API_KEY</strong> غير موجود — توليد الصور وتحليلها معطل. أضفه في الإعدادات</div>", unsafe_allow_html=True)

    # ─── Step 1: Input Mode ──────────────────────────────────────────────────
    st.markdown('<div class="step-badge">① اختر طريقة الإدخال</div>', unsafe_allow_html=True)

    if "input_mode" not in st.session_state:
        st.session_state.input_mode = "image"

    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        is_img = st.session_state.input_mode == "image"
        if st.button(
            f"📸  رفع صورة العطر\n{'← محدد' if is_img else 'انقر للاختيار'}",
            type="primary" if is_img else "secondary",
            key="mode_image"
        ):
            st.session_state.input_mode = "image"
            st.rerun()
    with mode_col2:
        is_man = st.session_state.input_mode == "manual"
        if st.button(
            f"🔗  رابط المنتج / يدوي\n{'← محدد' if is_man else 'انقر للاختيار'}",
            use_container_width=True,
            type="primary" if is_man else "secondary",
            key="mode_manual"
        ):
            st.session_state.input_mode = "manual"
            st.rerun()

    st.markdown("---")

    # ─── Step 2: Input ───────────────────────────────────────────────────────
    perfume_info = None
    image_bytes  = None

    if st.session_state.input_mode == "image":
        st.markdown('<div class="step-badge">② رفع صورة العطر</div>', unsafe_allow_html=True)

        col_img, col_char = st.columns([1, 1])
        with col_img:
            uploaded = st.file_uploader(
                "📸 ارفع صورة العطر (يفضل خلفية بيضاء)",
                type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed",
                key="perfume_upload"
            )
            if uploaded:
                st.image(uploaded, use_container_width=True, caption="✅ صورة العطر")
                image_bytes = uploaded.getvalue()

        with col_char:
            st.markdown("**👤 شخصية مهووس (Brand Identity)**")

            # ── مرجع شخصية مهووس المدمج ──────────────────────────
            BUILTIN_REFS = {
                "none":       ("بدون مرجع",        None),
                "official":   ("رسمي",              "assets/character/mahwous_character_official.jpeg"),
                "hoodie":     ("هودي",              "assets/character/mahwous_hoodie.jpg"),
                "thobe":      ("ثوب",               "assets/character/mahwous_thobe.jpg"),
                "thobe_car":  ("ثوب + سيارة",       "assets/character/mahwous_thobe_car.jpg"),
                "tomford":    ("توم فورد",           "assets/character/mahwous_tomford.png"),
                "upload":     ("رفع صورة يدوياً",   None),
            }
            ref_choice = st.selectbox(
                "👤 مرجع مهووس",
                options=list(BUILTIN_REFS.keys()),
                format_func=lambda k: BUILTIN_REFS[k][0],
                key="char_ref_choice",
                help="اختر مرجعاً مدمجاً أو ارفع صورة مخصصة لشخصية مهووس"
            )

            if ref_choice == "upload":
                char_img = st.file_uploader(
                    "📤 ارفع صورة مرجعية",
                    type=["jpg", "jpeg", "png"],
                    key="char_upload",
                    help="mahwous_character.png — يحافظ على ثبات الشخصية"
                )
                if char_img:
                    st.image(char_img, caption="✅ مرجع مهووس", use_container_width=True)
                    _ref_val = char_img.getvalue()
                    st.session_state.char_reference = _ref_val
                    st.session_state.char_reference_bytes = _ref_val
                else:
                    st.session_state.char_reference_bytes = None
            elif ref_choice != "none":
                asset_path = BUILTIN_REFS[ref_choice][1]
                ref_bytes = load_asset_bytes(asset_path)
                if ref_bytes:
                    st.image(ref_bytes, caption=f"✅ {BUILTIN_REFS[ref_choice][0]}", use_container_width=True)
                    st.session_state.char_reference_bytes = ref_bytes
                else:
                    st.warning("⚠️ تعذّر تحميل الصورة المرجعية")
                    st.session_state.char_reference_bytes = None
            else:
                st.session_state.char_reference_bytes = None

        if not uploaded:
            _show_how_it_works()
            return
        # ── Auto-Analyze ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="step-badge">③ تحليل العطر</div>', unsafe_allow_html=True)

        analyze_key = f"analyzed_{hash(image_bytes)}"
        if analyze_key not in st.session_state:
            if has_gemini:
                with st.spinner("🔍 تحليل صورة العطر بـ Gemini 2.0..."):
                    try:
                        info = analyze_perfume_image(image_bytes)
                        st.session_state[analyze_key] = info
                        st.session_state.gen_count = st.session_state.get("gen_count", 0) + 1
                    except Exception as e:
                        st.error(f"❌ فشل التحليل: {e}")
                        return
            else:
                info = build_manual_info(
                    brand=st.session_state.get("manual_brand", "Mahwous"),
                    product_name=st.session_state.get("manual_product", "عطر فاخر"),
                    colors=["gold", "black"],
                    bottle_shape="elegant luxury flacon",
                    mood="فاخر وغامض",
                    notes_guess="عود وعنبر"
                )
                st.session_state[analyze_key] = info

        perfume_info = st.session_state.get(analyze_key, {})
        _info_card(perfume_info)

        with st.expander("✏️ تعديل بيانات التحليل"):
            c1, c2, c3 = st.columns(3)
            perfume_info["product_name"] = c1.text_input("اسم العطر", perfume_info.get("product_name", ""))
            perfume_info["brand"]        = c2.text_input("العلامة التجارية", perfume_info.get("brand", ""))
            perfume_info["type"]         = c3.text_input("النوع", perfume_info.get("type", "EDP"))
            c4, c5, c6 = st.columns(3)
            perfume_info["gender"] = c4.selectbox("الجنس", ["masculine", "feminine", "unisex"], index=2)
            perfume_info["style"]  = c5.selectbox("الطابع", ["luxury","oriental","niche","sport","modern","classic"], index=0)
            perfume_info["mood"]   = c6.text_input("المزاج", perfume_info.get("mood", "فاخر"))
            perfume_info["bottle_shape"] = st.text_area("شكل الزجاجة", perfume_info.get("bottle_shape", ""), height=60)
            perfume_info["notes_guess"]  = st.text_input("ملاحظات العطر المتوقعة", perfume_info.get("notes_guess", ""))


    else:  # Manual mode
        st.markdown('<div class="step-badge">② إدخال رابط المنتج</div>', unsafe_allow_html=True)
        product_url = st.text_input("🔗 رابط المنتج (متجر، موقع الماركة، فراغرانتيكا...)", placeholder="https://...")
        
        if st.button("🔍 استخراج المعلومات من الرابط", key="extract_perfume_info", use_container_width=True):
            with st.spinner("🔍 جاري تصفح الرابط وتحليل البيانات..."):
                info = analyze_perfume_url(product_url)
                if info.get("success") is False:
                    st.error(info.get("error", "لم يتم استخراج المعلومات"))
                else:
                    st.success("✅ تم استخراج معلومات العطر بنجاح!")
                    st.session_state["perfume_info_auto"] = info
                    st.rerun()
        perfume_info = st.session_state.get("perfume_info_auto", {})
        if perfume_info:
            _info_card(perfume_info)

    if not perfume_info:
        return

    st.markdown("---")

    # ─── Smart Trends: Auto-trigger after product is known ───────────────────
    _show_smart_trends_panel(perfume_info)

    st.markdown("---")

    # ─── Main Tabs ───────────────────────────────────────────────────────────
    tab_images, tab_video, tab_single, tab_captions, tab_scenario, tab_content, tab_publish, tab_trends = st.tabs([
        "🖼️ توليد الصور",
        "🎬 توليد الفيديو",
        "🎨 صورة مخصصة",
        "✍️ التعليقات",
        "🎭 السيناريو",
        "📝 المحتوى",
        "📤 نشر",
        "🔥 ترند ذكي",
    ])

    # ════════════════════════════════════════════════════════════
    # TAB 1: توليد الصور لجميع المنصات
    # ════════════════════════════════════════════════════════════
    with tab_images:
        st.markdown('<div class="step-badge">④ اختر المنصات</div>', unsafe_allow_html=True)
        selected_platforms = platform_selector()

        if not selected_platforms:
            st.warning("⚠️ اختر منصة واحدة على الأقل")
        else:
            st.markdown(f"<div style='color:#D4B870; font-size:0.85rem; margin:0.5rem 0;'>✓ {len(selected_platforms)} منصة محددة</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="step-badge">⑤ إعدادات التوليد</div>', unsafe_allow_html=True)

        opt1, opt2, opt3 = st.columns(3)
        with opt1:
            outfit = st.selectbox(
                "👔 الزي",
                list(MAHWOUS_OUTFITS.keys()),
                format_func=lambda x: {
                    "suit": "🤵 البدلة الفاخرة", "hoodie": "🏆 الهودي الأيقوني",
                    "thobe": "👘 الثوب الملكي", "casual": "👕 الكاجوال الأنيق",
                    "western": "🤠 غربي (Leather) 🆕"
                }.get(x, x),
                key="outfit_select"
            )
        with opt2:
            scene = st.selectbox(
                "🎭 المكان",
                ["store", "beach", "desert", "studio", "garden", "rooftop", "car"],
                format_func=lambda x: {
                    "store": "🏪 متجر العطور", "beach": "🌅 شاطئ الغروب",
                    "desert": "🏜️ صحراء ذهبية", "studio": "🎬 استديو فاخر",
                    "garden": "🌹 حديقة ملكية", "rooftop": "🌆 سطح ناطحة سحاب",
                    "car": "🚗 سيارة فارهة"
                }.get(x, x),
                key="scene_select"
            )
        with opt3:
            include_char = st.checkbox("👤 تضمين شخصية مهووس", value=True, key="include_char")
            ramadan_mode = st.checkbox("🌙 وضع رمضان", value=False, key="ramadan_mode")

        # زر التوليد
        if not has_gemini:
            st.error("❌ GEMINI_API_KEY مطلوب لتوليد الصور — أضفه في الإعدادات")
        elif not selected_platforms:
            st.warning("⚠️ اختر منصة واحدة على الأقل")
        else:
            if st.button(
                f"🚀 توليد {len(selected_platforms)} صورة الآن",
                type="primary",
                use_container_width=True,
                key="generate_images_btn"
            ):
                with st.spinner("⚡ جاري التوليد المتوازي..."):
                    try:
                        # إذا تم اختيار جميع المقاسات الثلاثة استخدم التوليد المتوازي
                        if set(selected_platforms) == set(PLATFORMS.keys()):
                            results = generate_concurrent_images(
                                info=perfume_info,
                                outfit=outfit,
                                scene=scene,
                                include_character=include_char,
                                ramadan_mode=ramadan_mode
                            )
                        else:
                            results = generate_platform_images(
                                info=perfume_info,
                                selected_platforms=selected_platforms,
                                outfit=outfit,
                                scene=scene,
                                include_character=include_char,
                                ramadan_mode=ramadan_mode
                            )
                        st.session_state.generated_images = results
                        st.session_state.gen_count = st.session_state.get("gen_count", 0) + len(selected_platforms)
                        st.success(f"✅ تم توليد {len([r for r in results.values() if r.get('bytes')])} صورة بنجاح!")
                    except Exception as e:
                        st.error(f"❌ فشل التوليد: {e}")

        # ─── زر المزامنة ───
        if "generated_images" in st.session_state:
            st.markdown("---")
            sync_col1, sync_col2 = st.columns(2)
            with sync_col1:
                if st.button("🔗 إرسال إلى Make.com", use_container_width=True, key="sync_make"):
                    from modules.ai_engine import send_to_make, build_make_payload
                    payload = build_make_payload(
                        perfume_info, 
                        {k: "base64_data" for k in st.session_state.generated_images}, 
                        st.session_state.get("video_url_ready", ""),
                        st.session_state.get("captions_data", {})
                    )
                    res = send_to_make(payload)
                    if res["success"]: st.success("✅ تم الإرسال لـ Make.com!")
                    else: st.error(f"❌ فشل: {res['error']}")
            with sync_col2:
                if st.button("🗄️ حفظ في Supabase", use_container_width=True, key="sync_supabase"):
                    try:
                        from modules.supabase_db import save_perfume_to_supabase
                        res = save_perfume_to_supabase(
                            perfume_info,
                            st.session_state.generated_images,
                            st.session_state.get("video_url_ready", "")
                        )
                        if res["success"]: st.success("✅ تم الحفظ في Supabase!")
                        else: st.error(f"❌ فشل: {res['error']}")
                    except ImportError:
                        st.warning("⚠️ Supabase غير مفعل — أضف SUPABASE_URL و SUPABASE_KEY في الإعدادات")

        # عرض الصور المولدة
        if "generated_images" in st.session_state and st.session_state.generated_images:
            results = st.session_state.generated_images
            st.markdown("---")
            st.markdown('<div class="step-badge">⑥ الصور المولدة</div>', unsafe_allow_html=True)

            # ZIP download
            zip_data = _create_zip(results, perfume_info)
            brand_name = perfume_info.get("brand", "mahwous").replace(" ", "_").lower()
            st.download_button(
                f"📦 تحميل جميع الصور ZIP ({len([r for r in results.values() if r.get('bytes')])} صورة)",
                zip_data,
                f"{brand_name}_mahwous_studio.zip",
                "application/zip",
                use_container_width=True,
                key="download_zip"
            )

            # عرض الصور في شبكة
            cols = st.columns(3)
            col_idx = 0
            for key, data in results.items():
                if data.get("bytes"):
                    with cols[col_idx % 3]:
                        st.image(data["bytes"], caption=f"{data['label']} ({data['w']}×{data['h']})", use_container_width=True)
                        st.download_button(
                            f"⬇️ {data['emoji']}",
                            data["bytes"],
                            f"{key}.jpg",
                            "image/jpeg",
                            use_container_width=True,
                            key=f"dl_{key}"
                        )
                        
                        # زر رفع الدقة
                        if st.button(f"🔍 رفع الدقة 4K", key=f"upscale_{key}", use_container_width=True):
                            with st.spinner("✨ جاري رفع دقة الصورة وتحسين التفاصيل..."):
                                up_res = upscale_image_fal(data["bytes"])
                                if up_res["success"]:
                                    st.success("تم رفع الدقة!")
                                    st.image(up_res["bytes"], caption=f"✨ {data['label']} (Upscaled)", use_container_width=True)
                                    st.download_button(
                                        "⬇️ تحميل 4K",
                                        up_res["bytes"],
                                        f"{key}_upscaled.jpg",
                                        "image/jpeg",
                                        use_container_width=True,
                                        key=f"dl_up_{key}"
                                    )
                                else:
                                    st.error(f"فشل: {up_res.get('error')}")
                    col_idx += 1

    # ════════════════════════════════════════════════════════════
    # TAB 2: توليد الفيديو المباشر
    # ════════════════════════════════════════════════════════════
    with tab_video:
        _show_video_generation_tab(perfume_info)

    # ════════════════════════════════════════════════════════════
    # TAB 3: صورة مخصصة
    # ════════════════════════════════════════════════════════════
    with tab_single:
        if has_gemini or has_fal:
            _show_single_image_tab(perfume_info)
        else:
            st.error("❌ GEMINI_API_KEY أو FAL_API_KEY مطلوب لتوليد الصور — أضف أحدهما في الإعدادات")

    # ════════════════════════════════════════════════════════════
    # TAB 4: التعليقات
    # ════════════════════════════════════════════════════════════
    with tab_captions:
        st.markdown("### ✍️ توليد التعليقات لجميع المنصات")
        if st.button("✍️ توليد التعليقات الآن", type="primary", use_container_width=True, key="gen_captions"):
            with st.spinner("✍️ توليد التعليقات..."):
                try:
                    captions = generate_all_captions(perfume_info)
                    st.session_state.captions_data = captions
                except Exception as e:
                    st.error(f"❌ {e}")

        if "captions_data" in st.session_state:
            captions = st.session_state.captions_data
            if "error" in captions:
                st.error(captions["error"])
            else:
                platform_names = {
                    # المقاسات الثلاثة الجديدة (v13.0)
                    "post_1_1":   "📸 منشور مربع 1:1",
                    "story_9_16": "📱 قصة عمودية 9:16",
                    "wide_16_9":  "🎬 عريض أفقي 16:9",
                    # مفاتيح قديمة للتوافق مع generate_all_captions التي قد تُنتج مفاتيح بأسماء المنصات
                    "instagram_post": "📸 Instagram Post", "instagram_story": "📱 Instagram Story",
                    "tiktok": "🎵 TikTok", "youtube_short": "▶️ YouTube Short",
                    "youtube_thumb": "🎬 YouTube Thumbnail", "twitter": "🐦 Twitter/X",
                    "facebook": "👍 Facebook", "snapchat": "👻 Snapchat",
                    "linkedin": "💼 LinkedIn", "pinterest": "📌 Pinterest",
                    "whatsapp": "💬 WhatsApp", "telegram": "✈️ Telegram"
                }
                for plat_key, plat_label in platform_names.items():
                    if plat_key in captions:
                        data = captions[plat_key]
                        with st.expander(plat_label):
                            caption_text = data.get("caption", data.get("description", ""))
                            if caption_text:
                                st.text_area("التعليق", caption_text, height=120, key=f"cap_{plat_key}")
                            title = data.get("title", "")
                            if title:
                                st.text_input("العنوان", title, key=f"title_{plat_key}")
                            hashtags = data.get("hashtags", [])
                            if hashtags:
                                tags_html = " ".join([f"<span class='hashtag-pill'>{t}</span>" for t in hashtags[:15]])
                                st.markdown(tags_html, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # TAB 5: السيناريو
    # ════════════════════════════════════════════════════════════
    with tab_scenario:
        st.markdown("### 🎭 توليد سيناريو الفيديو")

        sc1, sc2 = st.columns(2)
        with sc1:
            scen_type = st.selectbox("نوع المشهد", ["مهووس مع العطر", "العطر يتكلم وحده", "مهووس بدون عطر"], key="scen_type")
            scen_scene = st.selectbox("المكان", ["store","beach","desert","studio","garden","rooftop","car"],
                                       format_func=lambda x: {"store":"🏪 متجر","beach":"🌅 شاطئ","desert":"🏜️ صحراء",
                                                               "studio":"🎬 استديو","garden":"🌹 حديقة","rooftop":"🌆 سطح","car":"🚗 سيارة"}.get(x,x),
                                       key="scen_scene")
        with sc2:
            scen_outfit = st.selectbox("الزي", list(MAHWOUS_OUTFITS.keys()),
                                        format_func=lambda x: {"suit":"🤵 البدلة","hoodie":"🏆 الهودي","thobe":"👘 الثوب","casual":"👕 الكاجوال","western":"🤠 غربي 🆕"}.get(x,x),
                                        key="scen_outfit")
            scen_dur = st.select_slider("المدة", [5,7,10,15], value=7, key="scen_dur")

        if st.button("🎬 توليد السيناريو", type="primary", use_container_width=True, key="gen_scenario"):
            with st.spinner("🎬 توليد السيناريو..."):
                try:
                    scenario = generate_scenario(perfume_info, scen_type, scen_scene, scen_outfit, scen_dur)
                    st.session_state.scenario_data = scenario
                except Exception as e:
                    st.error(f"❌ {e}")

        if "scenario_data" in st.session_state:
            sc = st.session_state.scenario_data
            st.markdown(f"### 🎬 {sc.get('title', 'السيناريو')}")
            st.info(f"🎯 الهوك: {sc.get('hook', '')}")

            for i, scene_data in enumerate(sc.get("scenes", []), 1):
                st.markdown(f"""
                <div class="scene-card">
                  <strong style="color:#FFE060;">المشهد {i} — {scene_data.get('time', '')}</strong><br>
                  <span style="color:#D0B070;">🎬 {scene_data.get('action', '')}</span><br>
                  <span style="color:#A0C0F0;">📷 {scene_data.get('camera', '')}</span><br>
                  <span style="color:#A0F0C0;">🎵 {scene_data.get('audio', '')}</span>
                </div>
                """, unsafe_allow_html=True)

            st.success(f"📣 CTA: {sc.get('cta', '')}")

            with st.expander("📋 برومت الفيديو (Luma/RunwayML)"):
                st.markdown(f'<div class="flow-prompt">{sc.get("video_prompt", "")}</div>', unsafe_allow_html=True)
                st.code(sc.get("video_prompt", ""), language="text")

            with st.expander("📋 برومت Google Flow/Veo"):
                st.markdown(f'<div class="flow-prompt">{sc.get("flow_prompt", "")}</div>', unsafe_allow_html=True)
                st.code(sc.get("flow_prompt", ""), language="text")

        # ── تعليق صوتي ElevenLabs ────────────────────────────────
        st.markdown("---")
        st.markdown("### 🎙️ التعليق الصوتي (ElevenLabs)")
        voiceover_text = st.text_area(
            "نص التعليق الصوتي",
            value=st.session_state.get("scenario_data", {}).get("hook", ""),
            height=100,
            key="voiceover_text_input",
            placeholder="أدخل النص الذي تريد تحويله إلى صوت..."
        )
        if st.button("🎙️ توليد التعليق الصوتي", use_container_width=True, key="gen_voiceover_btn"):
            secrets = _get_secrets()
            if not secrets.get("elevenlabs"):
                st.error("❌ ELEVENLABS_API_KEY مفقود — أضفه في إعدادات API")
            elif not voiceover_text.strip():
                st.warning("⚠️ أدخل نصاً للتعليق الصوتي أولاً")
            else:
                with st.spinner("🎙️ جاري توليد التعليق الصوتي..."):
                    try:
                        audio_bytes = generate_voiceover_elevenlabs(
                            voiceover_text,
                            voice_id=st.session_state.get("voice_id", "default"),
                            api_key=st.session_state.get("elevenlabs_key", "")
                        )
                        st.session_state.voiceover_bytes = audio_bytes
                    except Exception as e:
                        st.error(f"❌ فشل التوليد: {e}")

        if "voiceover_bytes" in st.session_state:
            st.audio(st.session_state.voiceover_bytes, format="audio/mpeg")
            st.download_button(
                "⬇️ تحميل الصوت (MP3)",
                st.session_state.voiceover_bytes,
                "voiceover.mp3",
                "audio/mpeg",
                use_container_width=True,
                key="dl_voiceover"
            )

    # ════════════════════════════════════════════════════════════
    # TAB 6: المحتوى
    # ════════════════════════════════════════════════════════════
    with tab_content:
        st.markdown("### 📝 توليد المحتوى الكامل")

        content_tabs = st.tabs(["📖 الأوصاف", "#️⃣ الهاشتاقات", "📖 القصة"])

        with content_tabs[0]:
            if st.button("📖 توليد الأوصاف", type="primary", use_container_width=True, key="gen_desc"):
                with st.spinner("📖 توليد الأوصاف..."):
                    try:
                        descs = generate_descriptions(perfume_info)
                        st.session_state.descriptions_data = descs
                    except Exception as e:
                        st.error(f"❌ {e}")
            if "descriptions_data" in st.session_state:
                descs = st.session_state.descriptions_data
                for key, label in [("short","📱 قصير"), ("medium","📸 متوسط"), ("long","📖 طويل"), ("ad","📣 إعلان")]:
                    if key in descs:
                        with st.expander(label):
                            st.text_area("", descs[key], height=120, key=f"desc_{key}")
                if "seo" in descs:
                    with st.expander("🔍 SEO"):
                        seo = descs["seo"]
                        st.text_input("العنوان", seo.get("title",""), key="seo_title")
                        st.text_input("الميتا", seo.get("meta",""), key="seo_meta")
                        st.text_area("المحتوى", seo.get("content",""), height=100, key="seo_content")

        with content_tabs[1]:
            if st.button("#️⃣ توليد الهاشتاقات", type="primary", use_container_width=True, key="gen_hash"):
                with st.spinner("#️⃣ توليد الهاشتاقات..."):
                    try:
                        hashtags = generate_hashtags(perfume_info)
                        st.session_state.hashtags_data = hashtags
                    except Exception as e:
                        st.error(f"❌ {e}")
            if "hashtags_data" in st.session_state:
                ht = st.session_state.hashtags_data
                for cat, label in [("arabic","🇸🇦 عربية"), ("english","🌍 إنجليزية"), ("brand","🏷️ علامة"), ("trending","🔥 ترند")]:
                    if cat in ht:
                        st.markdown(f"**{label}**")
                        tags = ht[cat]
                        if isinstance(tags, list):
                            tags_html = " ".join([f"<span class='hashtag-pill'>{t}</span>" for t in tags])
                            st.markdown(tags_html, unsafe_allow_html=True)

        with content_tabs[2]:
            if st.button("📖 توليد قصة العطر", type="primary", use_container_width=True, key="gen_story"):
                with st.spinner("📖 توليد القصة..."):
                    try:
                        story = generate_perfume_story(perfume_info)
                        st.session_state.story_data = story
                    except Exception as e:
                        st.error(f"❌ {e}")
            if "story_data" in st.session_state:
                st.text_area("📖 قصة العطر", st.session_state.story_data, height=300, key="story_text")

    # ════════════════════════════════════════════════════════════
    # TAB 7: نشر المحتوى
    # ════════════════════════════════════════════════════════════
    with tab_publish:
        st.markdown("""
        <div class="video-card">
          <h3>📤 نشر المحتوى</h3>
          <div style='color:#A090D0; font-size:0.85rem;'>
            إرسال الصور والفيديو والتعليقات إلى Make.com لنشرها تلقائياً
          </div>
        </div>
        """, unsafe_allow_html=True)

        secrets = _get_secrets()
        has_webhook = bool(secrets.get("webhook"))

        # ── آخر عملية نشر (دائم عبر الجلسة) ───────────────────────
        last_pub = st.session_state.get("publish_last_result")
        if last_pub:
            platforms_str = " · ".join(last_pub.get("platforms", []))
            if last_pub.get("success"):
                st.markdown(f"""
                <div class='video-status-done'>
                  ✅ <strong>تم النشر بنجاح!</strong><br>
                  🕐 {last_pub['timestamp']} &nbsp;|&nbsp;
                  📡 كود الاستجابة: {last_pub.get('status_code', '—')}<br>
                  🎯 المنصات: {platforms_str or '—'}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='video-status-error'>
                  ❌ <strong>فشل النشر</strong><br>
                  🕐 {last_pub['timestamp']} &nbsp;|&nbsp; {last_pub.get('error', 'خطأ غير معروف')}<br>
                  🎯 المنصات المحاولة: {platforms_str or '—'}
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑️ مسح سجل النشر", key="clear_publish_log"):
                st.session_state.pop("publish_last_result", None)
                st.rerun()

            st.markdown("---")

        # ── حالة المحتوى المتاح ──────────────────────────────────
        has_images   = bool(st.session_state.get("generated_images"))
        has_video    = bool(st.session_state.get("video_url_ready"))
        has_captions = bool(st.session_state.get("captions_data"))

        st.markdown("#### 📋 ملخص المحتوى المتاح للنشر")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            if has_images:
                img_count = len([v for v in st.session_state.generated_images.values() if v.get("bytes")])
                st.markdown(f"<span class='api-badge-ok'>🖼️ {img_count} صور جاهزة</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='api-badge-no'>🖼️ لا توجد صور — ولّد صوراً أولاً</span>", unsafe_allow_html=True)
        with sc2:
            if has_video:
                st.markdown("<span class='api-badge-ok'>🎬 فيديو جاهز</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='api-badge-no'>🎬 لا يوجد فيديو بعد</span>", unsafe_allow_html=True)
        with sc3:
            if has_captions:
                st.markdown("<span class='api-badge-ok'>✍️ تعليقات جاهزة</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='api-badge-no'>✍️ لا توجد تعليقات — ولّد تعليقات أولاً</span>", unsafe_allow_html=True)

        st.markdown("---")

        # ── إعدادات المنصة ───────────────────────────────────────
        if not has_webhook:
            st.markdown("""
            <div class='warning-box'>
              ⚠️ <strong>MAKE_WEBHOOK_URL</strong> غير محدد — أضفه في <strong>إعدادات API</strong> لتفعيل النشر التلقائي
            </div>
            """, unsafe_allow_html=True)

        # اختيار المنصات المراد النشر عليها
        st.markdown("#### 🎯 اختر المقاسات المراد نشرها")
        publish_plat_opts = {
            "post_1_1":   "📸 منشور مربع 1:1",
            "story_9_16": "📱 قصة عمودية 9:16",
            "wide_16_9":  "🎬 عريض أفقي 16:9",
        }
        p1, p2, p3 = st.columns(3)
        selected_publish_platforms = []
        for i, (key, label) in enumerate(publish_plat_opts.items()):
            col = [p1, p2, p3][i % 3]
            if col.checkbox(label, value=True, key=f"pub_{key}"):
                selected_publish_platforms.append(key)

        # معاينة الـ payload
        with st.expander("👁️ معاينة البيانات المُرسلة (Payload)"):
            preview_images = {}
            if has_images:
                for key, data in st.session_state.generated_images.items():
                    if data.get("bytes") and key in selected_publish_platforms:
                        preview_images[key] = f"[صورة {data['w']}×{data['h']} — {len(data['bytes'])//1024} KB]"
            preview_payload = {
                "perfume": {
                    "brand": perfume_info.get("brand", ""),
                    "product_name": perfume_info.get("product_name", ""),
                },
                "images_count": len(preview_images),
                "images": preview_images,
                "video_url": st.session_state.get("video_url_ready", ""),
                "captions_platforms": list(st.session_state.get("captions_data", {}).keys()),
                "selected_platforms": selected_publish_platforms,
            }
            st.json(preview_payload)

        st.markdown("---")

        # ── زر النشر ─────────────────────────────────────────────
        if not has_images and not has_video:
            st.warning("⚠️ ولّد صوراً أو فيديو أولاً قبل النشر")
        elif not has_webhook:
            st.info("💡 أضف MAKE_WEBHOOK_URL في الإعدادات ثم انقر النشر")
        else:
            if st.button("📤 نشر الآن عبر Make.com", type="primary", use_container_width=True, key="publish_btn"):
                # بناء image_urls من الصور المولّدة (base64 data URIs)
                image_urls = {}
                if has_images:
                    for key, data in st.session_state.generated_images.items():
                        if data.get("bytes") and key in selected_publish_platforms:
                            b64 = base64.b64encode(data["bytes"]).decode()
                            image_urls[key] = f"data:image/jpeg;base64,{b64}"

                video_url  = st.session_state.get("video_url_ready", "")
                captions   = st.session_state.get("captions_data", {})

                payload = build_make_payload(perfume_info, image_urls, video_url, captions)
                payload["selected_platforms"] = selected_publish_platforms

                with st.spinner("📤 جاري الإرسال إلى Make.com..."):
                    result = send_to_make(payload)

                if result.get("success"):
                    st.session_state.publish_last_result = {
                        "success":    True,
                        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "platforms":  selected_publish_platforms,
                        "status_code": result.get("status_code", "—"),
                        "response":   str(result.get("response", ""))[:200],
                    }
                    st.session_state.gen_count = st.session_state.get("gen_count", 0) + 1
                else:
                    st.session_state.publish_last_result = {
                        "success":   False,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "platforms": selected_publish_platforms,
                        "error":     result.get("error", "خطأ غير معروف"),
                    }
                st.rerun()

        # ── مزامنة Supabase ───────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 🗄️ حفظ في Supabase")
        if st.button("🗄️ مزامنة مع Supabase", use_container_width=True, key="sync_supabase_btn"):
            try:
                from modules.supabase_db import save_perfume_to_supabase
                images_with_urls = {}
                if has_images:
                    for key, data in st.session_state.generated_images.items():
                        url_val = data.get("url")
                        if url_val:
                            images_with_urls[key] = {"url": url_val}
                result_sb = save_perfume_to_supabase(
                    info=perfume_info,
                    images=images_with_urls,
                    video_url=st.session_state.get("video_url_ready", "")
                )
                if result_sb.get("success"):
                    st.success("✅ تم الحفظ في Supabase بنجاح!")
                else:
                    st.error(f"❌ فشل الحفظ في Supabase: {result_sb.get('error', 'خطأ غير معروف')}")
            except ImportError:
                st.warning("⚠️ Supabase غير مفعل — أضف SUPABASE_URL و SUPABASE_KEY في الإعدادات")

    # ════════════════════════════════════════════════════════════
    # TAB 8: ترند ذكي
    # ════════════════════════════════════════════════════════════
    with tab_trends:
        _show_trends_tab(perfume_info)
