"""
🤖 محرك الذكاء الاصطناعي - مهووس AI Studio v13.0
Fal.ai (Flux LoRA) + Luma Dream Machine + OpenRouter (Claude 3.5) + Make.com
"""

import streamlit as st
import requests
import base64
import json
import time
import re
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from PIL import Image

# ─── API Configs ──────────────────────────────────────────────────────────────
def _get_secrets() -> dict:
    """استرجاع مفاتيح API من session_state أو st.secrets (مع تجاهل غياب secrets.toml)"""
    def _s(session_key, secret_key, default=""):
        # أولاً: من session_state (المُدخل يدوياً في الواجهة)
        val = st.session_state.get(session_key, "")
        if val:
            return val
        # ثانياً: من st.secrets (إذا وُجد الملف)
        try:
            return st.secrets.get(secret_key, default)
        except Exception:
            return default
    return {
        "fal":        _s("fal_key",        "FAL_API_KEY"),
        "luma":       _s("luma_key",       "LUMA_API_KEY"),
        "openrouter": _s("openrouter_key", "OPENROUTER_API_KEY"),
        "kling":      _s("kling_key",      "KLING_API_KEY"),
        "gemini":     _s("gemini_key",     "GEMINI_API_KEY"),
        "runway":     _s("runway_key",     "RUNWAY_API_KEY"),
        "webhook":    _s("webhook_url",    "MAKE_WEBHOOK_URL"),
        "imgbb":      _s("imgbb_key",      "IMGBB_API_KEY"),
        "elevenlabs": _s("elevenlabs_key", "ELEVENLABS_API_KEY"),
    }


def load_asset_bytes(relative_path: str):
    """تحميل ملف من مجلد assets كبيانات خام (None عند الفشل)"""
    try:
        with open(relative_path, "rb") as f:
            return f.read()
    except Exception:
        return None


# ─── Model Endpoints ──────────────────────────────────────────────────────────
OPENROUTER_URL   = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"

FAL_BASE         = "https://fal.run"
FAL_FLUX_MODEL   = "fal-ai/flux/dev"
FAL_FLUX_LORA    = "fal-ai/flux-lora"

FAL_VIDEO_MODELS = {
    "kling": "fal-ai/kling-video/v1.6/standard/text-to-video",
    "veo":   "fal-ai/veo2",
    "svd":   "fal-ai/stable-video",
}

LUMA_BASE        = "https://api.lumalabs.ai/dream-machine/v1"
LUMA_GENERATIONS = f"{LUMA_BASE}/generations"

GEMINI_BASE           = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_VISION         = f"{GEMINI_BASE}/gemini-2.0-flash:generateContent"
GEMINI_IMAGEN         = f"{GEMINI_BASE}/imagen-3.0-generate-002:predict"
GEMINI_IMAGEN_DEFAULT = "imagen-3.0-generate-002"

LUMA_DEFAULT_MODEL = "ray-2"

RUNWAY_BASE      = "https://api.dev.runwayml.com/v1"
RUNWAY_GEN3      = f"{RUNWAY_BASE}/image_to_video"

# ─── Platform Sizes ────────────────────────────────────────────────────────────
PLATFORMS = {
    "post_1_1":         {"w": 1080, "h": 1080, "label": "📸 Post 1:1",          "aspect": "1:1",  "emoji": "📸", "fal_ratio": "1:1"},
    "story_9_16":       {"w": 1080, "h": 1920, "label": "📱 Story 9:16",        "aspect": "9:16", "emoji": "📱", "fal_ratio": "9:16"},
    "wide_16_9":        {"w": 1280, "h": 720,  "label": "🖼️ Wide 16:9",         "aspect": "16:9", "emoji": "🖼️", "fal_ratio": "16:9"},
    "instagram_post":   {"w": 1080, "h": 1080, "label": "📸 Instagram Post",    "aspect": "1:1",  "emoji": "📸", "fal_ratio": "1:1"},
    "instagram_story":  {"w": 1080, "h": 1920, "label": "📱 Instagram Story",   "aspect": "9:16", "emoji": "📱", "fal_ratio": "9:16"},
    "tiktok":           {"w": 1080, "h": 1920, "label": "🎵 TikTok",            "aspect": "9:16", "emoji": "🎵", "fal_ratio": "9:16"},
    "youtube_short":    {"w": 1080, "h": 1920, "label": "▶️ YouTube Short",     "aspect": "9:16", "emoji": "▶️", "fal_ratio": "9:16"},
    "youtube_thumb":    {"w": 1280, "h": 720,  "label": "🎬 YouTube Thumbnail", "aspect": "16:9", "emoji": "🎬", "fal_ratio": "16:9"},
    "twitter":          {"w": 1200, "h": 675,  "label": "🐦 Twitter/X",         "aspect": "16:9", "emoji": "🐦", "fal_ratio": "16:9"},
    "facebook":         {"w": 1200, "h": 630,  "label": "👍 Facebook",          "aspect": "16:9", "emoji": "👍", "fal_ratio": "16:9"},
    "snapchat":         {"w": 1080, "h": 1920, "label": "👻 Snapchat",          "aspect": "9:16", "emoji": "👻", "fal_ratio": "9:16"},
    "linkedin":         {"w": 1200, "h": 627,  "label": "💼 LinkedIn",          "aspect": "16:9", "emoji": "💼", "fal_ratio": "16:9"},
    "pinterest":        {"w": 1000, "h": 1500, "label": "📌 Pinterest",         "aspect": "2:3",  "emoji": "📌", "fal_ratio": "2:3"},
}

# ─── Character DNA (ثبات الشخصية) ─────────────────────────────────────────────
MAHWOUS_DNA = """Photorealistic 3D animated character 'Mahwous' — Gulf Arab perfume expert:
FACE (LOCK ALL): Black neatly styled hair swept forward. Short dark groomed beard (brown/chestnut). Warm expressive brown eyes with thick defined eyebrows. Golden-brown skin. Confident friendly expression.
STYLE: Pixar/Disney premium 3D render quality. Cinematic depth of field. Professional 3-point lighting.
CONSISTENCY: NEVER change any facial feature. SAME face every frame. Reference-locked character."""

MAHWOUS_OUTFITS = {
    "suit":   "wearing elegant black luxury suit with gold embroidery on lapels and cuffs, crisp white dress shirt, gold silk tie, gold pocket square — ultra-luxury formal look",
    "hoodie": "wearing premium black oversized hoodie with gold MAHWOUS lettering embroidered on chest — contemporary street-luxury",
    "thobe":  "wearing pristine bright white Saudi thobe with black and gold bisht cloak draped over shoulders — royal Arabian elegance",
    "casual": "wearing relaxed white linen shirt, sleeves rolled up, casual yet refined — effortlessly stylish",
}

QUALITY = """Technical specs: 4K ultra-resolution, RAW render quality.
Lighting: 3-point cinematic — key light warm gold, fill soft, rim metallic.
Color grade: rich warm tones, deep shadows, lifted blacks, golden highlights.
DOF: shallow depth of field, creamy bokeh background.
STRICT: NO TEXT anywhere, NO watermarks, NO subtitles, NO logos, NO UI elements. Clean frame only."""

FAL_ASPECT_MAP = {
    "1:1":  "square",
    "9:16": "portrait_16_9",
    "16:9": "landscape_16_9",
    "2:3":  "portrait_4_3",
    "4:3":  "landscape_4_3",
}


# ─── Retry Decorator ──────────────────────────────────────────────────────────
def with_retry(func, max_attempts: int = 3, delay: float = 2.0):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay * (attempt + 1))
    return None


# ─── JSON Cleaner ─────────────────────────────────────────────────────────────
def clean_json(text: str) -> dict:
    if not text:
        raise ValueError("النص فارغ")
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n?\s*```\s*$", "", text, flags=re.MULTILINE)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    fixed = re.sub(r',\s*([}\]])', r'\1', text)
    fixed = fixed.replace("'", '"')
    try:
        return json.loads(fixed)
    except:
        raise ValueError(f"فشل تحليل JSON: {text[:200]}")


# ─── OpenRouter Text Generation ───────────────────────────────────────────────
def generate_text_openrouter(prompt: str, system: str = None,
                              temperature: float = 0.75, max_tokens: int = 4096) -> str:
    secrets = _get_secrets()
    if not secrets["openrouter"]:
        raise ValueError("OPENROUTER_API_KEY مفقود")
    headers = {
        "Authorization": f"Bearer {secrets['openrouter']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mahwousstore.streamlit.app",
        "X-Title": "Mahwous AI Studio v13"
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_text_gemini(prompt: str, temperature: float = 0.7) -> str:
    secrets = _get_secrets()
    if not secrets["gemini"]:
        raise ValueError("GEMINI_API_KEY مفقود")
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096}
    }
    r = requests.post(GEMINI_VISION, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def generate_text_openai_compat(prompt: str, system: str = None,
                                 temperature: float = 0.75, max_tokens: int = 4096) -> str:
    """توليد نص عبر OpenAI-compatible API (fallback ثالث)"""
    import os
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        raise ValueError("OPENAI_API_KEY غير موجود في البيئة")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except ImportError:
        # fallback بدون مكتبة openai
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": "gpt-4.1-mini", "messages": messages,
                   "max_tokens": max_tokens, "temperature": temperature}
        r = requests.post(f"{base_url}/chat/completions",
                          headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def smart_generate_text(prompt: str, system: str = None, temperature: float = 0.75) -> str:
    """توليد نص ذكي مع fallback تلقائي: OpenRouter → Gemini → OpenAI-compat"""
    # المحاولة 1: OpenRouter (Claude 3.5)
    try:
        return with_retry(lambda: generate_text_openrouter(prompt, system, temperature))
    except Exception:
        pass
    # المحاولة 2: Gemini
    try:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        return with_retry(lambda: generate_text_gemini(full_prompt, temperature))
    except Exception:
        pass
    # المحاولة 3: OpenAI-compatible (gpt-4.1-mini)
    try:
        return with_retry(lambda: generate_text_openai_compat(prompt, system, temperature))
    except Exception as e:
        raise Exception(f"فشل توليد النص عبر جميع النماذج (OpenRouter + Gemini + OpenAI): {e}")


# ─── Gemini Vision: تحليل صورة العطر ─────────────────────────────────────────
def analyze_perfume_image(image_bytes: bytes) -> dict:
    secrets = _get_secrets()
    if not secrets["gemini"]:
        raise ValueError("GEMINI_API_KEY مطلوب لتحليل الصور")
    b64 = base64.b64encode(image_bytes).decode()
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
            {"text": """You are a master perfume expert. Analyze this perfume bottle image precisely.
Return ONLY valid JSON:
{
  "product_name": "exact full perfume name from label",
  "brand": "exact brand name",
  "type": "EDP/EDT/Parfum/EDC/Extrait/Oil",
  "size": "volume e.g. 100ml",
  "colors": ["primary color", "secondary color", "accent color"],
  "bottle_shape": "ultra-detailed bottle shape description",
  "bottle_cap": "cap material, shape, color, finish",
  "bottle_material": "glass type, finish, transparency",
  "label_style": "label design, typography style, colors",
  "style": "luxury/sport/modern/classic/oriental/niche",
  "gender": "masculine/feminine/unisex",
  "mood": "2-3 words for overall vibe",
  "notes_guess": "top/heart/base notes guess from visual",
  "bottle_uniqueness": "what makes this bottle distinctive",
  "image_quality": "good/poor",
  "confidence": 0.95
}"""}
        ]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
    }
    r = requests.post(GEMINI_VISION, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return clean_json(text)


# ─── Build Manual Info ────────────────────────────────────────────────────────
def build_manual_info(product_name: str, brand: str, perfume_type: str = "EDP",
                       size: str = "100ml", gender: str = "unisex",
                       style: str = "luxury", colors: list = None,
                       bottle_shape: str = "", mood: str = "",
                       notes: str = "") -> dict:
    """بناء معلومات العطر يدوياً"""
    return {
        "brand": brand,
        "product_name": product_name,
        "type": perfume_type,
        "size": size,
        "gender": gender,
        "style": style,
        "notes_guess": notes or "عود وعنبر ومسك",
        "mood": mood or "فاخر وغامض",
        "colors": colors or ["gold", "black", "amber"],
        "bottle_shape": bottle_shape or f"elegant luxury perfume bottle for {product_name} by {brand}",
        "bottle_cap": "polished metallic cap",
        "bottle_material": "premium crystal glass",
        "label_style": "elegant minimalist label with brand typography",
        "bottle_uniqueness": f"signature {brand} design",
        "confidence": 0.8,
    }


# ─── Prompt Builders ──────────────────────────────────────────────────────────
def build_mahwous_product_prompt(info: dict, outfit: str = "suit",
                                  scene: str = "store", platform_aspect: str = "1:1") -> str:
    outfit_desc = MAHWOUS_OUTFITS.get(outfit, MAHWOUS_OUTFITS["suit"])
    scenes = {
        "store":   "Inside a breathtaking luxury dark perfume boutique — backlit golden shelves of rare fragrances, warm amber spotlights, polished obsidian floor reflecting light",
        "beach":   "At a cinematic golden-hour beach — warm amber sky, gentle foamy waves, dramatic sunset casting long shadows",
        "desert":  "Vast golden Arabian desert at dusk — towering dunes with razor-sharp edges, amber sky with scattered stars",
        "studio":  "Inside a minimalist luxury dark studio — floating golden bokeh particles, dramatic rim lighting from above",
        "garden":  "In a lush royal fragrance garden at magic hour — cascading rose petals, golden mist, ornate marble fountain",
        "rooftop": "On a glass-barrier luxury rooftop at night — twinkling city skyline below, starry sky above",
        "car":     "Rear seat of a Rolls-Royce Phantom — cream leather interior, city lights blurring past rain-dotted windows",
    }
    scene_desc = scenes.get(scene, scenes["store"])
    product_name = info.get("product_name", "luxury perfume")
    brand = info.get("brand", "premium brand")
    bottle_shape = info.get("bottle_shape", "elegant glass perfume bottle")
    bottle_cap = info.get("bottle_cap", "polished cap")
    colors = ", ".join(info.get("colors", ["gold", "black"]))
    uniqueness = info.get("bottle_uniqueness", "")
    label = info.get("label_style", "elegant label")

    return f"""{MAHWOUS_DNA}
Outfit: {outfit_desc}
Setting: {scene_desc}

He cradles the perfume bottle reverently with both hands at chest height:
— Product: {product_name} by {brand}
— Bottle: {bottle_shape}. Cap: {bottle_cap}. Colors: {colors}. Label: {label}.
{f"— Distinctive: {uniqueness}" if uniqueness else ""}

CRITICAL BOTTLE RULE: The bottle must be 100% photorealistic, matching the original design exactly.
Expression: warm expert confidence, slight knowing smile, eyes engaging camera.
Composition: subject centered, slight 3/4 angle, negative space around bottle.
Aspect ratio: {platform_aspect}.
{QUALITY}"""


def build_product_only_prompt(info: dict, platform_aspect: str = "1:1") -> str:
    product_name = info.get("product_name", "luxury perfume")
    brand = info.get("brand", "premium brand")
    bottle_shape = info.get("bottle_shape", "elegant glass bottle")
    bottle_cap = info.get("bottle_cap", "polished cap")
    colors = ", ".join(info.get("colors", ["gold", "black"]))
    material = info.get("bottle_material", "premium glass")
    uniqueness = info.get("bottle_uniqueness", "")

    return f"""Museum-quality luxury perfume product photography.
Subject: {product_name} by {brand}
Bottle: {bottle_shape}. Material: {material}. Cap: {bottle_cap}. Colors: {colors}.
{f"Distinctive: {uniqueness}" if uniqueness else ""}

STRICT: Reproduce the exact original bottle with zero creative liberty.
Placement: centered on aged dark marble slab. Soft golden light from upper-right.
Silk fabric draped elegantly beside bottle. Tiny ambient golden particles floating.
Mood: museum-quality product shot — luxurious, aspirational, editorial.
Aspect ratio: {platform_aspect}.
{QUALITY}"""


def build_ramadan_product_prompt(info: dict, platform_aspect: str = "9:16") -> str:
    product_name = info.get("product_name", "luxury perfume")
    brand = info.get("brand", "premium brand")
    colors = ", ".join(info.get("colors", ["gold", "black"]))
    return f"""Luxury Ramadan perfume advertisement.
Subject: {product_name} by {brand} bottle. Colors: {colors}.
Setting: Ornate Ramadan scene — glowing golden crescent moon and fanoos lantern hanging above,
scattered rose petals and oud chips, soft warm candlelight.
Bottle centered prominently, surrounded by tasteful Islamic geometric gold ornaments.
Atmosphere: warm amber and deep gold tones, reverent and aspirational.
Aspect ratio: {platform_aspect}.
{QUALITY}"""


def build_video_prompt(info: dict, scene: str = "store", outfit: str = "suit",
                        duration: int = 7, camera_move: str = "push_in",
                        scene_type: str = "مهووس مع العطر", mood_extra: str = "") -> str:
    outfit_desc = MAHWOUS_OUTFITS.get(outfit, MAHWOUS_OUTFITS["suit"])
    scenes = {
        "store":   "luxury dark perfume boutique, golden backlit shelves, obsidian floor",
        "beach":   "cinematic golden-hour beach, amber sky, foamy waves",
        "desert":  "vast golden Arabian desert at dusk, towering dunes",
        "studio":  "minimalist luxury dark studio, golden bokeh particles",
        "garden":  "lush royal fragrance garden, cascading rose petals, golden mist",
        "rooftop": "glass-barrier luxury rooftop at night, city skyline",
        "car":     "Rolls-Royce Phantom rear seat, cream leather, city lights",
    }
    cameras = {
        "push_in":  "Slow cinematic push-in toward subject",
        "zoom":     "Gradual zoom from wide to tight close-up",
        "orbit":    "Smooth slow orbital movement around subject",
        "static":   "Static locked-off cinematic frame",
        "low_rise": "Low angle slowly rising upward",
        "dolly":    "Smooth dolly track gliding alongside",
        "crane":    "Slow crane descent from above to eye level",
    }
    scene_desc = scenes.get(scene, scenes["store"])
    camera_desc = cameras.get(camera_move, cameras["push_in"])
    product_name = info.get("product_name", "luxury perfume")
    brand = info.get("brand", "premium brand")
    mood = info.get("mood", "luxurious and mysterious")

    if scene_type == "مهووس مع العطر":
        subject = f"""{MAHWOUS_DNA}
{outfit_desc}
Mahwous holds {product_name} by {brand} bottle reverently. Warm confident expression."""
    elif scene_type == "العطر يتكلم وحده":
        subject = f"""The {product_name} by {brand} perfume bottle, centered and glowing with golden inner light.
Subtle animated particles float around it. Cinematic product hero shot."""
    else:
        subject = f"""{MAHWOUS_DNA}
{outfit_desc}
Mahwous stands confidently without perfume. Charismatic presence."""

    return f"""Cinematic {duration}-second luxury perfume advertisement video.

SUBJECT: {subject}

SETTING: {scene_desc}

CAMERA: {camera_desc}. Smooth professional movement. No shaking.

MOOD: {mood}. {mood_extra if mood_extra else ""}

LIGHTING: Warm golden cinematic 3-point lighting. Rich shadows. Lifted blacks.
COLOR GRADE: Deep warm tones, golden highlights, luxury feel.

STRICT RULES:
- NO text on screen. NO watermarks. NO subtitles.
- NO perfume spraying. Replace with: golden luminous particles floating gently.
- Mahwous mouth CLOSED when perfume speaks.
- MAINTAIN exact bottle design — photorealistic, no distortion.
- Professional cinema quality. Smooth transitions."""


# ─── Fal.ai Image Generation ──────────────────────────────────────────────────
def generate_image_fal(prompt: str, aspect_ratio: str = "1:1",
                        width: int = 1080, height: int = 1080) -> bytes:
    """توليد صورة باستخدام Fal.ai (Flux Dev)"""
    secrets = _get_secrets()
    if not secrets["fal"]:
        raise ValueError("FAL_API_KEY مفقود — أضفه في إعدادات API")

    headers = {
        "Authorization": f"Key {secrets['fal']}",
        "Content-Type": "application/json",
    }

    # تحديد الأبعاد بناءً على نسبة العرض
    size_map = {
        "1:1":  {"width": 1024, "height": 1024},
        "9:16": {"width": 768,  "height": 1360},
        "16:9": {"width": 1360, "height": 768},
        "2:3":  {"width": 832,  "height": 1216},
    }
    size = size_map.get(aspect_ratio, {"width": 1024, "height": 1024})

    payload = {
        "prompt": prompt,
        "image_size": size,
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }

    # إرسال الطلب
    r = requests.post(
        f"{FAL_BASE}/{FAL_FLUX_MODEL}",
        headers=headers,
        json=payload,
        timeout=120
    )

    if r.status_code == 200:
        data = r.json()
        images = data.get("images", [])
        if images:
            img_url = images[0].get("url", "")
            if img_url:
                img_r = requests.get(img_url, timeout=60)
                img_r.raise_for_status()
                return img_r.content
        raise ValueError("لم يتم إرجاع صورة من Fal.ai")

    # محاولة الـ queue API إذا فشل الطلب المباشر
    elif r.status_code == 202:
        # Async queue
        queue_data = r.json()
        request_id = queue_data.get("request_id", "")
        if not request_id:
            raise ValueError("لم يتم الحصول على request_id من Fal.ai")
        return _poll_fal_queue(request_id, secrets["fal"])
    else:
        raise ValueError(f"خطأ Fal.ai {r.status_code}: {r.text[:300]}")


def _poll_fal_queue(request_id: str, api_key: str, max_wait: int = 120) -> bytes:
    """انتظار نتيجة من Fal.ai queue"""
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    status_url = f"{FAL_BASE}/queue/requests/{request_id}/status"
    result_url = f"{FAL_BASE}/queue/requests/{request_id}"

    start = time.time()
    while time.time() - start < max_wait:
        r = requests.get(status_url, headers=headers, timeout=30)
        if r.status_code == 200:
            status_data = r.json()
            status = status_data.get("status", "")
            if status == "COMPLETED":
                result_r = requests.get(result_url, headers=headers, timeout=30)
                result_r.raise_for_status()
                data = result_r.json()
                images = data.get("images", [])
                if images:
                    img_url = images[0].get("url", "")
                    if img_url:
                        img_r = requests.get(img_url, timeout=60)
                        img_r.raise_for_status()
                        return img_r.content
                raise ValueError("لم تُرجع Fal.ai صورة بعد الاكتمال")
            elif status in ("FAILED", "CANCELLED"):
                raise ValueError(f"فشل توليد الصورة في Fal.ai: {status}")
        time.sleep(3)
    raise TimeoutError("انتهت مهلة انتظار Fal.ai")


def _get_gemini_imagen_endpoint() -> str:
    """endpoint Gemini Imagen (قابل للضبط عبر GEMINI_IMAGEN_MODEL في البيئة/secrets)"""
    import os
    model = (
        st.session_state.get("gemini_imagen_model", "")
        or os.environ.get("GEMINI_IMAGEN_MODEL", "")
        or GEMINI_IMAGEN_DEFAULT
    )
    return f"{GEMINI_BASE}/{model}:predict"


def generate_image_gemini(prompt: str, aspect_ratio: str = "1:1") -> bytes:
    """توليد صورة باستخدام Gemini Imagen 3 (بديل)"""
    secrets = _get_secrets()
    if not secrets["gemini"]:
        raise ValueError("GEMINI_API_KEY مفقود")

    aspect_map = {
        "1:1": "1:1", "9:16": "9:16", "16:9": "16:9",
        "2:3": "3:4", "4:3": "4:3",
    }
    ar = aspect_map.get(aspect_ratio, "1:1")

    endpoint = _get_gemini_imagen_endpoint()
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": ar,
            "safetyFilterLevel": "block_some",
            "personGeneration": "allow_all",
        }
    }
    r = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    if r.status_code == 404:
        model_name = endpoint.split("/")[-1].replace(":predict", "")
        raise ValueError(
            f"نموذج Gemini Imagen غير متاح ({model_name}) — "
            f"تحقق من دعم الموديل في حسابك أو غيّر GEMINI_IMAGEN_MODEL. "
            f"404 Not Found"
        )
    r.raise_for_status()
    data = r.json()
    predictions = data.get("predictions", [])
    if not predictions:
        raise ValueError("لم يتم إرجاع صور من Imagen 3")
    b64_data = predictions[0].get("bytesBase64Encoded", "")
    if not b64_data:
        raise ValueError("بيانات الصورة فارغة من Imagen 3")
    return base64.b64decode(b64_data)


def smart_generate_image(prompt: str, aspect_ratio: str = "1:1",
                          width: int = 1080, height: int = 1080) -> bytes:
    """توليد صورة ذكي: Fal.ai أولاً ثم Gemini كـ fallback"""
    secrets = _get_secrets()

    if secrets["fal"]:
        try:
            return with_retry(
                lambda: generate_image_fal(prompt, aspect_ratio, width, height),
                max_attempts=2
            )
        except Exception as e:
            st.warning(f"⚠️ Fal.ai: {e} — جاري المحاولة مع Gemini Imagen...")

    if secrets["gemini"]:
        try:
            return with_retry(
                lambda: generate_image_gemini(prompt, aspect_ratio),
                max_attempts=2
            )
        except Exception as e:
            err = str(e)
            if "404" in err or "غير متاح" in err:
                raise Exception(
                    f"⚠️ Gemini Imagen: {err} — "
                    f"يمكنك تغيير الموديل عبر إعداد GEMINI_IMAGEN_MODEL في secrets"
                )
            raise Exception(f"فشل توليد الصورة عبر Gemini Imagen: {e}")

    raise ValueError("لا يوجد مفتاح API للصور. أضف FAL_API_KEY أو GEMINI_API_KEY في الإعدادات.")


# ─── Generate All Platform Images (3 مقاسات إجبارية) ─────────────────────────
def generate_platform_images(info: dict, selected_platforms: list, outfit: str,
                               scene: str, include_character: bool = True,
                               progress_callback=None, ramadan_mode: bool = False) -> dict:
    """توليد الصور لجميع المنصات المحددة"""
    results = {}
    total = len(selected_platforms)

    for i, plat_key in enumerate(selected_platforms):
        plat = PLATFORMS[plat_key]
        if progress_callback:
            progress_callback(i / total, f"⚡ توليد {plat['label']}...")

        if ramadan_mode:
            prompt = build_ramadan_product_prompt(info, plat["aspect"])
        elif include_character:
            prompt = build_mahwous_product_prompt(info, outfit, scene, plat["aspect"])
        else:
            prompt = build_product_only_prompt(info, plat["aspect"])

        try:
            img_bytes = smart_generate_image(prompt, plat["aspect"], plat["w"], plat["h"])
        except Exception as e:
            img_bytes = None
            st.error(f"❌ فشل توليد {plat['label']}: {e}")

        results[plat_key] = {
            "bytes":   img_bytes,
            "label":   plat["label"],
            "emoji":   plat["emoji"],
            "w":       plat["w"],
            "h":       plat["h"],
            "aspect":  plat["aspect"],
            "prompt":  prompt,
            "success": img_bytes is not None,
        }

    if progress_callback:
        progress_callback(1.0, "✅ اكتملت جميع الصور!")
    return results


# ─── Generate 3 Mandatory Sizes ───────────────────────────────────────────────
def generate_three_mandatory_sizes(info: dict, outfit: str = "suit",
                                    scene: str = "store",
                                    include_character: bool = True,
                                    ramadan_mode: bool = False,
                                    progress_callback=None) -> dict:
    """توليد 3 مقاسات إجبارية: 1:1 + 9:16 + 16:9"""
    mandatory = ["post_1_1", "story_9_16", "wide_16_9"]
    return generate_platform_images(
        info, mandatory, outfit, scene,
        include_character, progress_callback, ramadan_mode
    )


def generate_concurrent_images(info: dict, selected_platforms: list,
                                outfit: str = "suit", scene: str = "store",
                                include_character: bool = True,
                                ramadan_mode: bool = False,
                                progress_callback=None,
                                max_workers: int = 3) -> dict:
    """توليد صور لجميع المنصات بشكل متوازٍ باستخدام ThreadPoolExecutor"""
    results = {}
    total = len(selected_platforms)

    def _generate_one(plat_key):
        plat = PLATFORMS[plat_key]
        if ramadan_mode:
            prompt = build_ramadan_product_prompt(info, plat["aspect"])
        elif include_character:
            prompt = build_mahwous_product_prompt(info, outfit, scene, plat["aspect"])
        else:
            prompt = build_product_only_prompt(info, plat["aspect"])
        try:
            img_bytes = smart_generate_image(prompt, plat["aspect"], plat["w"], plat["h"])
        except Exception as e:
            img_bytes = None
        return plat_key, plat, prompt, img_bytes

    completed_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_generate_one, pk): pk for pk in selected_platforms}
        for future in as_completed(futures):
            plat_key, plat, prompt, img_bytes = future.result()
            completed_count += 1
            if progress_callback:
                progress_callback(
                    completed_count / total,
                    f"⚡ اكتمل {completed_count}/{total} — {plat['label']}"
                )
            results[plat_key] = {
                "bytes":   img_bytes,
                "label":   plat["label"],
                "emoji":   plat["emoji"],
                "w":       plat["w"],
                "h":       plat["h"],
                "aspect":  plat["aspect"],
                "prompt":  prompt,
                "success": img_bytes is not None,
            }

    if progress_callback:
        progress_callback(1.0, "✅ اكتملت جميع الصور!")
    return results


# ─── ImgBB Image Upload ───────────────────────────────────────────────────────
def upload_image_imgbb(image_bytes: bytes, api_key: str = None) -> str:
    """رفع صورة على ImgBB والحصول على رابط عام"""
    secrets = _get_secrets()
    key = api_key or secrets.get("imgbb", "")
    if not key:
        raise ValueError("IMGBB_API_KEY مفقود — أضفه في إعدادات API")

    b64 = base64.b64encode(image_bytes).decode()
    r = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": key, "image": b64},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise ValueError(f"فشل رفع الصورة على ImgBB: {data.get('error', {}).get('message', 'خطأ غير معروف')}")
    return data["data"]["url"]


# ─── ElevenLabs Voiceover ─────────────────────────────────────────────────────
ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"
ELEVENLABS_DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"  # Rachel (English)


def generate_voiceover_elevenlabs(text: str, voice_id: str = None,
                                   stability: float = 0.5,
                                   similarity_boost: float = 0.75) -> bytes:
    """توليد صوت تعليق باستخدام ElevenLabs"""
    secrets = _get_secrets()
    if not secrets.get("elevenlabs"):
        raise ValueError("ELEVENLABS_API_KEY مفقود — أضفه في إعدادات API")

    vid = voice_id or ELEVENLABS_DEFAULT_VOICE
    headers = {
        "xi-api-key": secrets["elevenlabs"],
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
        },
    }
    r = requests.post(
        f"{ELEVENLABS_BASE}/text-to-speech/{vid}",
        headers=headers,
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    return r.content


# ─── Luma Dream Machine Video ─────────────────────────────────────────────────
LUMA_MODELS = {
    "luma-photon":       "Luma Photon (موصى به)",
    "luma-photon-flash": "Luma Photon Flash (سريع)",
    "ray-2":             "Ray 2 (جودة عالية)",
    "ray-1-6":           "Ray 1.6",
}

def generate_video_luma(prompt: str, aspect_ratio: str = "9:16",
                         duration: int = 5, image_url: str = None,
                         image_bytes: bytes = None, loop: bool = False,
                         model: str = LUMA_DEFAULT_MODEL) -> dict:
    """توليد فيديو باستخدام Luma Dream Machine"""
    secrets = _get_secrets()
    if not secrets["luma"]:
        raise ValueError("LUMA_API_KEY مفقود — أضفه في إعدادات API")

    headers = {
        "Authorization": f"Bearer {secrets['luma']}",
        "Content-Type": "application/json",
    }

    # تحديد نسبة العرض
    luma_ratio_map = {
        "9:16": "9:16",
        "16:9": "16:9",
        "1:1":  "1:1",
    }
    ratio = luma_ratio_map.get(aspect_ratio, "9:16")

    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": ratio,
        "loop": loop,
    }

    # إضافة صورة مرجعية إذا وُجدت (image_bytes أو image_url)
    ref_url = image_url
    if image_bytes and not ref_url:
        # محاولة رفع الصورة على ImgBB أولاً للحصول على رابط عام
        secrets = _get_secrets()
        if secrets.get("imgbb"):
            try:
                ref_url = upload_image_imgbb(image_bytes, secrets["imgbb"])
            except Exception:
                ref_url = None
        if not ref_url:
            # fallback: base64 data URI
            b64 = base64.b64encode(image_bytes).decode()
            ref_url = f"data:image/jpeg;base64,{b64}"

    if ref_url:
        payload["keyframes"] = {
            "frame0": {
                "type": "image",
                "url": ref_url
            }
        }

    r = requests.post(LUMA_GENERATIONS, headers=headers, json=payload, timeout=60)
    if r.status_code not in (200, 201, 202):
        return {"error": f"خطأ Luma {r.status_code}: {r.text[:200]}"}
    data = r.json()
    return {
        "id": data.get("id", ""),
        "state": data.get("state", "queued"),
        "created_at": data.get("created_at", ""),
    }


def check_luma_status(generation_id: str) -> dict:
    """فحص حالة توليد الفيديو في Luma"""
    secrets = _get_secrets()
    if not secrets["luma"]:
        raise ValueError("LUMA_API_KEY مفقود")

    headers = {
        "Authorization": f"Bearer {secrets['luma']}",
        "Content-Type": "application/json",
    }
    r = requests.get(f"{LUMA_GENERATIONS}/{generation_id}", headers=headers, timeout=30)
    if r.status_code != 200:
        return {
            "id": generation_id,
            "state": "error",
            "video_url": "",
            "failure_reason": "",
            "error": f"خطأ Luma {r.status_code}: {r.text[:200]}",
        }
    data = r.json()
    return {
        "id": generation_id,
        "state": data.get("state", "queued"),
        "video_url": data.get("assets", {}).get("video", ""),
        "thumbnail_url": data.get("assets", {}).get("thumbnail", ""),
        "failure_reason": data.get("failure_reason", ""),
    }


def poll_luma_video(generation_id: str, max_wait: int = 300,
                     progress_callback=None) -> dict:
    """انتظار اكتمال الفيديو من Luma مع Polling"""
    start = time.time()
    attempt = 0
    while time.time() - start < max_wait:
        attempt += 1
        try:
            status = check_luma_status(generation_id)
            state = status.get("state", "")

            if progress_callback:
                elapsed = int(time.time() - start)
                progress_callback(
                    min(elapsed / max_wait, 0.95),
                    f"⏳ الفيديو قيد المعالجة... ({elapsed}s) — الحالة: {state}"
                )

            if state == "completed":
                return status
            elif state in ("failed", "cancelled", "error"):
                raise ValueError(f"فشل توليد الفيديو: {status.get('failure_reason', status.get('error', state))}")

            # انتظار تدريجي
            wait_time = min(10 + attempt * 2, 30)
            time.sleep(wait_time)
        except Exception as e:
            if "failed" in str(e).lower() or "cancelled" in str(e).lower():
                raise
            time.sleep(10)

    raise TimeoutError(f"انتهت مهلة انتظار الفيديو ({max_wait}s)")


# ─── RunwayML Video Generation ────────────────────────────────────────────────
def generate_video_runway(prompt: str, image_bytes: bytes = None,
                           aspect_ratio: str = "9:16", duration: int = 5) -> dict:
    """توليد فيديو باستخدام RunwayML Gen-3"""
    secrets = _get_secrets()
    if not secrets["runway"]:
        raise ValueError("RUNWAY_API_KEY مفقود")

    headers = {
        "Authorization": f"Bearer {secrets['runway']}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06",
    }

    ratio_map = {"9:16": "720:1280", "16:9": "1280:720", "1:1": "960:960"}
    resolution = ratio_map.get(aspect_ratio, "720:1280")

    payload = {
        "promptText": prompt,
        "model": "gen3a_turbo",
        "ratio": resolution,
        "duration": min(duration, 10),
    }

    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        payload["promptImage"] = f"data:image/jpeg;base64,{b64}"

    r = requests.post(RUNWAY_GEN3, headers=headers, json=payload, timeout=60)
    if r.status_code not in (200, 201, 202):
        return {"error": f"خطأ RunwayML {r.status_code}: {r.text[:200]}"}
    data = r.json()
    return {
        "id": data.get("id", ""),
        "status": data.get("status", "PENDING"),
    }


def check_runway_status(task_id: str) -> dict:
    """فحص حالة مهمة RunwayML"""
    secrets = _get_secrets()
    if not secrets["runway"]:
        raise ValueError("RUNWAY_API_KEY مفقود")

    headers = {
        "Authorization": f"Bearer {secrets['runway']}",
        "X-Runway-Version": "2024-11-06",
    }
    r = requests.get(f"{RUNWAY_BASE}/tasks/{task_id}", headers=headers, timeout=30)
    if r.status_code != 200:
        return {
            "id": task_id,
            "state": "error",
            "status": "FAILED",
            "video_url": "",
            "progress": 0,
            "error": f"خطأ RunwayML {r.status_code}: {r.text[:200]}",
            "failure_reason": "",
        }
    data = r.json()
    raw_status = data.get("status", "PENDING")
    # تحويل حالة RunwayML إلى صيغة موحدة مع Luma
    state_map = {
        "SUCCEEDED": "completed",
        "FAILED": "failed",
        "PENDING": "queued",
        "RUNNING": "dreaming",
        "THROTTLED": "queued",
    }
    return {
        "id": task_id,
        "state": state_map.get(raw_status, raw_status.lower()),
        "status": raw_status,
        "video_url": data.get("output", [None])[0] if data.get("output") else "",
        "progress": data.get("progressRatio", 0),
        "error": data.get("failure", ""),
        "failure_reason": data.get("failure", ""),
    }


# ─── Fal.ai Video Generation ──────────────────────────────────────────────────
def generate_video_fal(prompt: str, model: str = "kling",
                        aspect_ratio: str = "9:16",
                        image_bytes: bytes = None) -> dict:
    """توليد فيديو باستخدام Fal.ai (Kling/Veo/SVD)"""
    secrets = _get_secrets()
    if not secrets["fal"]:
        return {"success": False, "provider": "fal", "error": "FAL_API_KEY مفقود — أضفه في إعدادات API"}

    model_id = FAL_VIDEO_MODELS.get(model, FAL_VIDEO_MODELS["kling"])
    headers = {
        "Authorization": f"Key {secrets['fal']}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }

    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        payload["image_url"] = f"data:image/jpeg;base64,{b64}"

    try:
        r = requests.post(
            f"{FAL_BASE}/queue/submit/{model_id}",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if r.status_code not in (200, 202):
            return {"success": False, "provider": "fal", "error": f"خطأ Fal.ai {r.status_code}: {r.text[:200]}"}

        data = r.json()
        request_id = data.get("request_id", "")
        if not request_id:
            return {"success": False, "provider": "fal", "error": "لم يتم الحصول على request_id من Fal.ai"}

        # محاولة سريعة لمعرفة ما إذا كان الطلب قد اكتمل فوراً
        status_r = requests.get(
            f"{FAL_BASE}/queue/requests/{request_id}/status",
            headers=headers,
            timeout=15,
        )
        if status_r.status_code == 200 and status_r.json().get("status") == "COMPLETED":
            result_r = requests.get(
                f"{FAL_BASE}/queue/requests/{request_id}",
                headers=headers,
                timeout=30,
            )
            if result_r.status_code == 200:
                rd = result_r.json()
                video_url = (rd.get("video", {}).get("url") or rd.get("video_url") or "")
                if video_url:
                    return {"success": True, "provider": "fal", "state": "completed", "video_url": video_url}

        return {"success": True, "provider": "fal", "state": "queued", "id": request_id}

    except Exception as e:
        return {"success": False, "provider": "fal", "error": str(e)}


def check_fal_video_status(request_id: str) -> dict:
    """فحص حالة توليد الفيديو في Fal.ai"""
    secrets = _get_secrets()
    if not secrets["fal"]:
        return {"id": request_id, "state": "error", "video_url": "", "error": "FAL_API_KEY مفقود"}

    headers = {
        "Authorization": f"Key {secrets['fal']}",
        "Content-Type": "application/json",
    }

    r = requests.get(
        f"{FAL_BASE}/queue/requests/{request_id}/status",
        headers=headers,
        timeout=30,
    )
    if r.status_code != 200:
        return {
            "id": request_id,
            "state": "error",
            "video_url": "",
            "error": f"خطأ Fal.ai {r.status_code}: {r.text[:200]}",
        }

    fal_status_map = {
        "COMPLETED":   "completed",
        "FAILED":      "failed",
        "IN_PROGRESS": "dreaming",
        "IN_QUEUE":    "queued",
    }
    raw = r.json().get("status", "IN_QUEUE")
    state = fal_status_map.get(raw, "queued")

    if state == "completed":
        result_r = requests.get(
            f"{FAL_BASE}/queue/requests/{request_id}",
            headers=headers,
            timeout=30,
        )
        if result_r.status_code == 200:
            rd = result_r.json()
            video_url = (rd.get("video", {}).get("url") or rd.get("video_url") or "")
            return {"id": request_id, "state": "completed", "video_url": video_url, "provider": "fal"}
        return {"id": request_id, "state": "error", "video_url": "", "error": f"خطأ في استرجاع نتيجة Fal.ai: {result_r.status_code}"}

    return {"id": request_id, "state": state, "video_url": "", "provider": "fal", "progress": 0}


# ─── Generate All Captions ────────────────────────────────────────────────────
def generate_all_captions(info: dict) -> dict:
    system = """أنت أفضل كاتب محتوى عطور فاخرة في الخليج العربي.
أسلوبك: شعري، عاطفي، فاخر، مع هوك جذاب في كل منصة.
اللغة: عربية خليجية راقية — ليست فصحى متصلبة، ليست عامية ركيكة.
الأيقونات: استخدم إيموجي ذكي ومناسب بحد أقصى 3-4 لكل نص.
الكلمات المفتاحية الشرائية: "شراء عطور فاخرة"، "أفضل عطور نيش"، "عطور أصلية للبيع"، "متجر عطور موثوق"."""

    prompt = f"""العطر: {info.get('product_name', 'عطر فاخر')} من {info.get('brand', 'علامة مميزة')}
النوع: {info.get('type', 'EDP')} | الجنس: {info.get('gender', 'unisex')} | الطابع: {info.get('style', 'luxury')}
المزاج: {info.get('mood', 'فاخر وغامض')} | ملاحظات: {info.get('notes_guess', 'عود وعنبر')}

اكتب Captions احترافية ومخصصة لكل منصة. أجب بـ JSON صرف فقط:
{{
  "instagram_post": {{"caption": "نص 120-150 كلمة شعري وجذاب", "hashtags": ["#هاشتاق × 25"]}},
  "instagram_story": {{"caption": "نص قصير 50 كلمة + CTA", "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"]}},
  "tiktok": {{"caption": "150 حرف + هوك صادم", "hashtags": ["#fyp","#viral","#عطور_فاخرة"]}},
  "youtube_short": {{"title": "عنوان 60 حرف", "caption": "وصف 80-100 كلمة + CTA"}},
  "youtube_thumb": {{"title": "عنوان SEO", "description": "وصف 200-250 كلمة"}},
  "twitter": {{"caption": "نص 220 حرف + 2-3 هاشتاقات"}},
  "facebook": {{"caption": "نص قصصي 200-280 كلمة + 5 هاشتاقات"}},
  "snapchat": {{"caption": "نص شبابي 50-60 حرف"}},
  "linkedin": {{"caption": "نص مهني 150-180 كلمة"}},
  "pinterest": {{"caption": "وصف SEO 100-130 كلمة + 12 كلمة مفتاحية"}},
  "whatsapp": {{"caption": "رسالة ودية 70-90 كلمة"}},
  "telegram": {{"caption": "تحليل عميق 280-350 كلمة"}}
}}"""

    text = smart_generate_text(prompt, system, temperature=0.8)
    try:
        return clean_json(text)
    except Exception as e:
        return {"error": f"فشل توليد Captions: {e}"}


def generate_descriptions(info: dict) -> dict:
    prompt = f"""العطر: {info.get('product_name', 'عطر فاخر')} من {info.get('brand', 'علامة')}
النوع: {info.get('type', 'EDP')} | {info.get('gender', 'unisex')} | {info.get('style', 'luxury')}
المزاج: {info.get('mood', 'فاخر')} | الملاحظات: {info.get('notes_guess', 'عود وعنبر')}

اكتب 5 أوصاف تسويقية باللغة العربية الراقية. JSON فقط:
{{
  "short":  "وصف 60-80 كلمة مكثف للقصص والريلز",
  "medium": "وصف 120-150 كلمة للمنشورات الرئيسية",
  "long":   "مقال وصفي عاطفي وشعري 260-300 كلمة",
  "ad":     "إعلان مكثف ومقنع 30-40 كلمة",
  "seo": {{
    "title":    "عنوان SEO 55-60 حرف",
    "meta":     "وصف ميتا 145-155 حرف",
    "content":  "محتوى SEO 200-220 كلمة",
    "keywords": ["كلمة1","كلمة2","كلمة3","كلمة4","كلمة5","كلمة6","كلمة7","كلمة8","كلمة9","كلمة10"]
  }}
}}"""
    text = smart_generate_text(prompt, temperature=0.7)
    try:
        return clean_json(text)
    except:
        return {}


def generate_hashtags(info: dict) -> dict:
    prompt = f"""العطر: {info.get('product_name')} | {info.get('brand')} | {info.get('gender')} | {info.get('style')} | {info.get('mood')}

اختر 45 هاشتاق مثالي: مزيج من الوصول العالي والمتوسط والمتخصص. JSON فقط:
{{
  "arabic":   ["#هاشتاق_عربي × 20 — مزيج عام ومتخصص"],
  "english":  ["#english_hashtag × 15 — mix of high and niche"],
  "brand":    ["#brand_specific × 5"],
  "buying":   ["#شراء_عطور_فاخرة","#عطور_أصلية_للبيع","#متجر_عطور_موثوق","#أفضل_عطور_نيش","#عطور_نيش_السعودية"]
}}"""
    text = smart_generate_text(prompt, temperature=0.6)
    try:
        return clean_json(text)
    except:
        return {}


def generate_scenario(info: dict, scenario_type: str = "مهووس مع العطر",
                       scene: str = "store", outfit: str = "suit",
                       duration: int = 7) -> dict:
    """توليد سيناريو فيديو كامل مع برومت Luma/Runway"""
    system = """أنت كاتب سيناريو إبداعي محترف لتيك توك والريلز. أسلوبك: سينمائي، مثير، يبدأ بهوك صادم."""

    prompt = f"""اكتب سيناريو فيديو {duration} ثوانٍ لعطر "{info.get('product_name', 'عطر فاخر')}" من "{info.get('brand', 'علامة')}"
نوع المشهد: {scenario_type} | المكان: {scene} | الزي: {outfit}
المزاج: {info.get('mood', 'فاخر وغامض')} | الملاحظات: {info.get('notes_guess', 'عود وعنبر')}

أجب بـ JSON صرف فقط:
{{
  "title": "عنوان السيناريو",
  "hook": "الهوك الصادم في أول 3 ثوانٍ",
  "scenes": [
    {{"time": "0-3s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}},
    {{"time": "3-5s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}},
    {{"time": "5-7s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}}
  ],
  "cta": "دعوة للشراء غير مباشرة",
  "video_prompt": "برومت Luma Dream Machine بالإنجليزية",
  "flow_prompt": "برومت Google Flow/Veo بالإنجليزية"
}}"""

    text = smart_generate_text(prompt, system, temperature=0.85)
    try:
        return clean_json(text)
    except Exception as e:
        return {
            "title": f"سيناريو {info.get('product_name', '')}",
            "hook": "هوك جذاب",
            "scenes": [{"time": "0-7s", "action": text[:200], "camera": "medium shot", "audio": "موسيقى هادئة"}],
            "cta": "اطلب الآن",
            "video_prompt": build_video_prompt(info, scene, outfit, duration),
            "flow_prompt": build_video_prompt(info, scene, outfit, duration),
        }


def generate_perfume_story(info: dict) -> str:
    """توليد قصة عطر شعرية"""
    prompt = f"""أنت شاعر عطور فاخر. اكتب قصة شعرية قصيرة (150-200 كلمة) عن:
العطر: {info.get('product_name', 'عطر فاخر')} من {info.get('brand', 'علامة')}
المزاج: {info.get('mood', 'فاخر وغامض')}
الملاحظات: {info.get('notes_guess', 'عود وعنبر ومسك')}

الأسلوب: شعري، عاطفي، يصف رحلة الرائحة من أول رشة حتى الخاتمة.
اللغة: عربية فصحى راقية مع لمسة شعرية.
لا تذكر أسماء جغرافية."""
    return smart_generate_text(prompt, temperature=0.9)


# ─── Smart Trend Insights ─────────────────────────────────────────────────────
def generate_trend_insights(info: dict) -> dict:
    """تحليل ذكي للترندات والمواضيع الرائجة المتعلقة بالمنتج"""
    product_name = info.get("product_name", "عطر فاخر")
    brand        = info.get("brand", "علامة مميزة")
    gender       = info.get("gender", "unisex")
    style        = info.get("style", "luxury")
    mood         = info.get("mood", "فاخر وغامض")
    notes        = info.get("notes_guess", "عود وعنبر")
    perfume_type = info.get("type", "EDP")

    system = """أنت خبير تسويق رقمي متخصص في العطور الفاخرة في السوق الخليجي.
لديك معرفة عميقة بالترندات الحالية على TikTok وInstagram وTwitter في السعودية والخليج.
مهمتك: تحليل المنتج واقتراح مواضيع ترند ذكية وأفكار محتوى فيروسي."""

    prompt = f"""المنتج: {product_name} من {brand}
النوع: {perfume_type} | الجنس: {gender} | الطابع: {style}
المزاج: {mood} | الملاحظات: {notes}

بناءً على هذا العطر، حلّل وأجب بـ JSON صرف فقط:
{{
  "product_summary": "جملة واحدة تصف هوية العطر بدقة",
  "target_audience": "الجمهور المستهدف الأمثل (عمر، اهتمامات، منصة)",
  "trending_topics": [
    {{"topic": "موضوع الترند", "platform": "TikTok/Instagram/Twitter", "relevance": "سبب ارتباطه بالعطر", "hook": "هوك فيروسي جاهز"}},
    {{"topic": "موضوع الترند", "platform": "TikTok/Instagram/Twitter", "relevance": "سبب ارتباطه بالعطر", "hook": "هوك فيروسي جاهز"}},
    {{"topic": "موضوع الترند", "platform": "TikTok/Instagram/Twitter", "relevance": "سبب ارتباطه بالعطر", "hook": "هوك فيروسي جاهز"}},
    {{"topic": "موضوع الترند", "platform": "TikTok/Instagram/Twitter", "relevance": "سبب ارتباطه بالعطر", "hook": "هوك فيروسي جاهز"}},
    {{"topic": "موضوع الترند", "platform": "TikTok/Instagram/Twitter", "relevance": "سبب ارتباطه بالعطر", "hook": "هوك فيروسي جاهز"}}
  ],
  "viral_hooks": [
    "هوك صادم للثانية الأولى #1",
    "هوك صادم للثانية الأولى #2",
    "هوك صادم للثانية الأولى #3"
  ],
  "content_angles": [
    {{"angle": "زاوية المحتوى", "format": "ريلز/بوست/ستوري", "description": "وصف الفكرة في جملتين"}},
    {{"angle": "زاوية المحتوى", "format": "ريلز/بوست/ستوري", "description": "وصف الفكرة في جملتين"}},
    {{"angle": "زاوية المحتوى", "format": "ريلز/بوست/ستوري", "description": "وصف الفكرة في جملتين"}},
    {{"angle": "زاوية المحتوى", "format": "ريلز/بوست/ستوري", "description": "وصف الفكرة في جملتين"}}
  ],
  "trending_hashtags": {{
    "viral":   ["أكثر 8 هاشتاقات ترند الآن مرتبطة بالعطر"],
    "niche":   ["8 هاشتاقات متخصصة عالية الجودة"],
    "buying":  ["8 هاشتاقات شرائية مستهدفة لمحبي العطور الفاخرة في الخليج"]
  }},
  "best_post_times": {{
    "instagram": "أفضل وقت نشر على إنستجرام (المنطقة العربية)",
    "tiktok":    "أفضل وقت نشر على تيك توك",
    "twitter":   "أفضل وقت نشر على تويتر"
  }},
  "competitor_gap": "فرصة تسويقية غير مستغلة لهذا العطر تحديداً",
  "seasonal_angle": "زاوية موسمية أو مناسبة مرتبطة بالوقت الحالي"
}}"""

    text = smart_generate_text(prompt, system, temperature=0.75)
    try:
        return clean_json(text)
    except Exception as e:
        return {"error": f"فشل تحليل الترندات: {e}"}


# ─── Make.com Webhook Integration ─────────────────────────────────────────────
def send_to_make(payload: dict) -> dict:
    """إرسال البيانات إلى Make.com Webhook للنشر التلقائي"""
    secrets = _get_secrets()
    webhook_url = secrets.get("webhook", "")

    if not webhook_url:
        return {"success": False, "error": "MAKE_WEBHOOK_URL غير محدد في الإعدادات"}

    try:
        headers = {"Content-Type": "application/json"}
        r = requests.post(webhook_url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return {
            "success": True,
            "status_code": r.status_code,
            "response": r.text[:200],
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def build_make_payload(info: dict, image_urls: dict, video_url: str,
                        captions: dict) -> dict:
    """بناء الـ payload المرسل لـ Make.com"""
    return {
        "source": "Mahwous AI Studio v13.0",
        "timestamp": datetime.now().isoformat(),
        "perfume": {
            "brand": info.get("brand", ""),
            "product_name": info.get("product_name", ""),
            "type": info.get("type", ""),
            "gender": info.get("gender", ""),
            "style": info.get("style", ""),
            "mood": info.get("mood", ""),
        },
        "images": {
            "instagram_post_1x1": image_urls.get("instagram_post", ""),
            "instagram_story_9x16": image_urls.get("instagram_story", ""),
            "twitter_16x9": image_urls.get("twitter", ""),
            "tiktok_9x16": image_urls.get("tiktok", ""),
        },
        "video": {
            "url": video_url,
            "platform": "tiktok_reels",
        },
        "captions": {
            "instagram": captions.get("instagram_post", {}).get("caption", ""),
            "instagram_hashtags": " ".join(captions.get("instagram_post", {}).get("hashtags", [])),
            "twitter": captions.get("twitter", {}).get("caption", ""),
            "tiktok": captions.get("tiktok", {}).get("caption", ""),
            "facebook": captions.get("facebook", {}).get("caption", ""),
        },
        "seo_keywords": [
            "شراء عطور فاخرة",
            "أفضل عطور نيش في السعودية",
            "عطور أصلية للبيع",
            "متجر عطور موثوق",
            f"{info.get('brand', '')} {info.get('product_name', '')}",
        ],
    }
