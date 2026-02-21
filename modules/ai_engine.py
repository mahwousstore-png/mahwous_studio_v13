"""
🤖 محرك الذكاء الاصطناعي - مهووس v13.0
OpenRouter (Claude 3.5) + Gemini 2.0 Flash + Imagen 3 + Luma AI + RunwayML
توليد الصور والفيديوهات بشكل كامل ومباشر من داخل التطبيق
"""

import streamlit as st
import requests
import base64
import json
import time
import re
import io
from datetime import datetime
from PIL import Image

# ─── API Configs ──────────────────────────────────────────────────────────────
def _get_secrets() -> dict:
    """استرجاع مفاتيح API من session_state أو st.secrets"""
    return {
        "openrouter": (
            st.session_state.get("openrouter_key", "") or
            st.secrets.get("OPENROUTER_API_KEY", "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")
        ),
        "gemini": (
            st.session_state.get("gemini_key", "") or
            st.secrets.get("GEMINI_API_KEY", "")
        ),
        "luma": (
            st.session_state.get("luma_key", "") or
            st.secrets.get("LUMA_API_KEY", "")
        ),
        "runway": (
            st.session_state.get("runway_key", "") or
            st.secrets.get("RUNWAY_API_KEY", "")
        ),
        "kling": (
            st.session_state.get("kling_key", "") or
            st.secrets.get("KLING_API_KEY", "")
        ),
        "webhook": (
            st.session_state.get("webhook_url", "") or
            st.secrets.get("WEBHOOK_PUBLISH_CONTENT", "")
        ),
    }


# ─── Model Endpoints ──────────────────────────────────────────────────────────
GEMINI_BASE      = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_VISION    = f"{GEMINI_BASE}/gemini-2.0-flash:generateContent"
GEMINI_TEXT      = f"{GEMINI_BASE}/gemini-2.0-flash:generateContent"
GEMINI_IMAGEN    = f"{GEMINI_BASE}/imagen-3.0-generate-002:predict"
GEMINI_IMAGEN_FAST = f"{GEMINI_BASE}/imagen-3.0-fast-generate-001:predict"

OPENROUTER_URL   = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"

# Luma Dream Machine
LUMA_BASE        = "https://api.lumalabs.ai/dream-machine/v1"
LUMA_GENERATIONS = f"{LUMA_BASE}/generations"

# RunwayML Gen-3
RUNWAY_BASE      = "https://api.dev.runwayml.com/v1"
RUNWAY_GEN3      = f"{RUNWAY_BASE}/image_to_video"

# ─── Platform Sizes ────────────────────────────────────────────────────────────
PLATFORMS = {
    "instagram_post":   {"w": 1080, "h": 1080, "label": "📸 Instagram Post",    "aspect": "1:1",  "emoji": "📸"},
    "instagram_story":  {"w": 1080, "h": 1920, "label": "📱 Instagram Story",   "aspect": "9:16", "emoji": "📱"},
    "tiktok":           {"w": 1080, "h": 1920, "label": "🎵 TikTok",            "aspect": "9:16", "emoji": "🎵"},
    "youtube_short":    {"w": 1080, "h": 1920, "label": "▶️ YouTube Short",     "aspect": "9:16", "emoji": "▶️"},
    "youtube_thumb":    {"w": 1280, "h": 720,  "label": "🎬 YouTube Thumbnail", "aspect": "16:9", "emoji": "🎬"},
    "twitter":          {"w": 1200, "h": 675,  "label": "🐦 Twitter/X",         "aspect": "16:9", "emoji": "🐦"},
    "facebook":         {"w": 1200, "h": 630,  "label": "👍 Facebook",          "aspect": "16:9", "emoji": "👍"},
    "snapchat":         {"w": 1080, "h": 1920, "label": "👻 Snapchat",          "aspect": "9:16", "emoji": "👻"},
    "linkedin":         {"w": 1200, "h": 627,  "label": "💼 LinkedIn",          "aspect": "16:9", "emoji": "💼"},
    "pinterest":        {"w": 1000, "h": 1500, "label": "📌 Pinterest",         "aspect": "2:3",  "emoji": "📌"},
}

# ─── Character DNA ─────────────────────────────────────────────────────────────
MAHWOUS_DNA = """Photorealistic 3D animated character 'Mahwous' — Gulf Arab perfume expert:
FACE (LOCK ALL): Black neatly styled hair swept forward. Short dark groomed beard. Warm expressive brown eyes with thick defined eyebrows. Golden-brown skin. Confident friendly expression.
STYLE: Pixar/Disney premium 3D render quality. Cinematic depth of field. Professional 3-point lighting.
CONSISTENCY: NEVER change any facial feature. SAME face every frame. Reference-locked character."""

MAHWOUS_OUTFITS = {
    "suit":   "wearing elegant black luxury suit with gold embroidery on lapels, crisp white dress shirt, gold silk tie, gold pocket square — ultra-luxury formal look",
    "hoodie": "wearing premium black oversized hoodie with gold MAHWOUS lettering embroidered on chest — contemporary street-luxury",
    "thobe":  "wearing pristine bright white Saudi thobe with black and gold bisht cloak draped over shoulders — royal Arabian elegance",
    "casual": "wearing relaxed white linen shirt, sleeves rolled up, casual yet refined — effortlessly stylish",
}

QUALITY = """Technical specs: 4K ultra-resolution, RAW render quality, 8-bit color depth. 
Lighting: 3-point cinematic — key light warm gold, fill soft, rim metallic.
Color grade: rich warm tones, deep shadows, lifted blacks, golden highlights.
DOF: shallow depth of field, creamy bokeh background.
STRICT: NO TEXT anywhere, NO watermarks, NO subtitles, NO logos, NO UI elements. Clean frame only."""

ASPECT_RATIO_MAP = {
    "1:1":  "1:1",
    "9:16": "9:16",
    "16:9": "16:9",
    "2:3":  "3:4",
    "4:3":  "4:3",
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
def generate_text_openrouter(prompt: str, system: str = None, temperature: float = 0.75, max_tokens: int = 4096) -> str:
    secrets = _get_secrets()
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


def _openrouter_chat(prompt: str, api_key: str) -> str:
    """دالة مساعدة للمحادثة عبر OpenRouter"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mahwousstore.streamlit.app",
        "X-Title": "Mahwous AI Studio v13"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.75,
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_text_gemini(prompt: str, temperature: float = 0.7) -> str:
    secrets = _get_secrets()
    if not secrets["gemini"]:
        raise ValueError("Gemini API key مفقود")
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096}
    }
    r = requests.post(GEMINI_TEXT, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def smart_generate_text(prompt: str, system: str = None, temperature: float = 0.75) -> str:
    def try_openrouter():
        return generate_text_openrouter(prompt, system, temperature)
    try:
        return with_retry(try_openrouter)
    except Exception:
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            return with_retry(lambda: generate_text_gemini(full_prompt, temperature))
        except Exception as e:
            raise Exception(f"فشل توليد النص عبر جميع النماذج: {e}")


# ─── Gemini 2.0 Flash Vision ──────────────────────────────────────────────────
def analyze_perfume_image(image_bytes: bytes) -> dict:
    secrets = _get_secrets()
    if not secrets["gemini"]:
        raise ValueError("GEMINI_API_KEY مطلوب لتحليل الصور")
    b64 = base64.b64encode(image_bytes).decode()
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
            {"text": """You are a master perfume expert with 30 years of experience. 
Analyze this perfume bottle image with extreme precision. Return ONLY valid JSON, nothing else:
{
  "product_name": "exact full perfume name from label",
  "brand": "exact brand name",
  "type": "EDP/EDT/Parfum/EDC/Extrait/Oil",
  "size": "volume e.g. 100ml",
  "colors": ["primary color", "secondary color", "accent color"],
  "bottle_shape": "ultra-detailed bottle shape: geometry, curves, proportions, height-to-width ratio",
  "bottle_cap": "cap material, shape, color, finish",
  "bottle_material": "glass type, finish, transparency",
  "label_style": "label design, typography style, colors",
  "style": "luxury/sport/modern/classic/oriental/niche",
  "gender": "masculine/feminine/unisex",
  "mood": "2-3 words for overall vibe",
  "notes_guess": "top/heart/base notes guess from visual",
  "bottle_uniqueness": "what makes this bottle distinctive",
  "image_quality": "good/poor",
  "confidence": 0.0
}"""}
        ]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
    }
    def do_request():
        r = requests.post(GEMINI_VISION, headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return clean_json(text)
    return with_retry(do_request)


# ─── ✅ توليد الصور بـ Imagen 3 (مُفعَّل بالكامل) ─────────────────────────────
def generate_image_gemini(prompt: str, aspect_ratio: str = "1:1",
                           reference_b64: str = None, fast_mode: bool = False) -> bytes | None:
    """
    توليد صورة بـ Imagen 3 — مُفعَّل بالكامل
    fast_mode=True يستخدم imagen-3.0-fast للسرعة
    """
    secrets = _get_secrets()
    if not secrets["gemini"]:
        return None

    ar = ASPECT_RATIO_MAP.get(aspect_ratio, "1:1")
    endpoint = GEMINI_IMAGEN_FAST if fast_mode else GEMINI_IMAGEN
    headers = {"Content-Type": "application/json", "x-goog-api-key": secrets["gemini"]}

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": ar,
            "safetyFilterLevel": "block_only_high",
            "personGeneration": "allow_adult",
            "addWatermark": False,
            "enhancePrompt": True,
        }
    }

    def do_request():
        r = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        if r.status_code == 200:
            preds = r.json().get("predictions", [])
            if preds:
                b64 = preds[0].get("bytesBase64Encoded", "")
                if b64:
                    return base64.b64decode(b64)
        elif r.status_code == 429:
            time.sleep(8)
            raise Exception("Rate limit - retrying")
        elif r.status_code == 400:
            err = r.json().get("error", {}).get("message", "")
            raise Exception(f"Imagen 400: {err}")
        else:
            raise Exception(f"Imagen error {r.status_code}: {r.text[:200]}")
        return None

    try:
        return with_retry(do_request, max_attempts=3, delay=4.0)
    except Exception as e:
        st.warning(f"⚠️ تعذّر توليد الصورة: {e}")
        return None


# ─── ✅ توليد الفيديو بـ Luma Dream Machine (مُفعَّل بالكامل) ─────────────────
def generate_video_luma(
    prompt: str,
    image_bytes: bytes = None,
    duration: int = 5,
    aspect_ratio: str = "9:16",
    loop: bool = False
) -> dict:
    """
    توليد فيديو بـ Luma Dream Machine API
    يدعم: text-to-video و image-to-video
    يُعيد: {"id": ..., "state": ..., "video_url": ..., "error": ...}
    """
    secrets = _get_secrets()
    if not secrets["luma"]:
        return {"error": "LUMA_API_KEY غير موجود — أضفه في الإعدادات"}

    headers = {
        "Authorization": f"Bearer {secrets['luma']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "loop": loop,
    }

    # إذا تم تمرير صورة مرجعية → image-to-video
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        payload["keyframes"] = {
            "frame0": {
                "type": "image",
                "url": f"data:image/jpeg;base64,{b64}"
            }
        }

    try:
        r = requests.post(LUMA_GENERATIONS, headers=headers, json=payload, timeout=30)
        if r.status_code in [200, 201]:
            data = r.json()
            gen_id = data.get("id", "")
            return {
                "id": gen_id,
                "state": data.get("state", "pending"),
                "video_url": data.get("assets", {}).get("video", ""),
                "error": None
            }
        else:
            err = r.json().get("detail", r.text[:200])
            return {"error": f"Luma API خطأ {r.status_code}: {err}"}
    except Exception as e:
        return {"error": f"خطأ في الاتصال بـ Luma: {e}"}


def check_luma_status(generation_id: str) -> dict:
    """
    التحقق من حالة توليد الفيديو في Luma
    يُعيد: {"state": "completed/processing/failed", "video_url": ..., "progress": ...}
    """
    secrets = _get_secrets()
    if not secrets["luma"]:
        return {"state": "error", "error": "LUMA_API_KEY غير موجود"}

    headers = {
        "Authorization": f"Bearer {secrets['luma']}",
        "Accept": "application/json",
    }

    try:
        r = requests.get(f"{LUMA_GENERATIONS}/{generation_id}", headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            state = data.get("state", "unknown")
            video_url = data.get("assets", {}).get("video", "")
            return {
                "state": state,
                "video_url": video_url,
                "progress": data.get("progress", 0),
                "error": data.get("failure_reason", None)
            }
        else:
            return {"state": "error", "error": f"خطأ {r.status_code}"}
    except Exception as e:
        return {"state": "error", "error": str(e)}


def poll_luma_video(generation_id: str, max_wait: int = 300, interval: int = 10) -> dict:
    """
    انتظار اكتمال توليد الفيديو في Luma (polling)
    max_wait: أقصى وقت انتظار بالثواني
    interval: الفاصل الزمني بين كل فحص
    """
    start = time.time()
    while time.time() - start < max_wait:
        status = check_luma_status(generation_id)
        state = status.get("state", "")
        if state == "completed":
            return status
        elif state in ["failed", "error"]:
            return status
        time.sleep(interval)
    return {"state": "timeout", "error": "انتهى وقت الانتظار — حاول لاحقاً"}


# ─── ✅ توليد الفيديو بـ RunwayML Gen-3 (مُفعَّل بالكامل) ────────────────────
def generate_video_runway(
    prompt: str,
    image_bytes: bytes = None,
    duration: int = 5,
    ratio: str = "720:1280"
) -> dict:
    """
    توليد فيديو بـ RunwayML Gen-3 Alpha Turbo
    يدعم: text-to-video و image-to-video
    """
    secrets = _get_secrets()
    if not secrets["runway"]:
        return {"error": "RUNWAY_API_KEY غير موجود — أضفه في الإعدادات"}

    headers = {
        "Authorization": f"Bearer {secrets['runway']}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06",
    }

    payload = {
        "promptText": prompt,
        "model": "gen3a_turbo",
        "duration": duration,
        "ratio": ratio,
        "watermark": False,
    }

    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        payload["promptImage"] = f"data:image/jpeg;base64,{b64}"

    try:
        r = requests.post(RUNWAY_GEN3, headers=headers, json=payload, timeout=30)
        if r.status_code in [200, 201]:
            data = r.json()
            return {
                "id": data.get("id", ""),
                "state": "pending",
                "video_url": "",
                "error": None
            }
        else:
            err = r.json().get("error", r.text[:200])
            return {"error": f"RunwayML خطأ {r.status_code}: {err}"}
    except Exception as e:
        return {"error": f"خطأ في الاتصال بـ RunwayML: {e}"}


def check_runway_status(task_id: str) -> dict:
    """التحقق من حالة توليد الفيديو في RunwayML"""
    secrets = _get_secrets()
    if not secrets["runway"]:
        return {"state": "error", "error": "RUNWAY_API_KEY غير موجود"}

    headers = {
        "Authorization": f"Bearer {secrets['runway']}",
        "X-Runway-Version": "2024-11-06",
    }

    try:
        r = requests.get(f"{RUNWAY_BASE}/tasks/{task_id}", headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            status = data.get("status", "PENDING")
            output = data.get("output", [])
            video_url = output[0] if output else ""
            state_map = {
                "SUCCEEDED": "completed",
                "FAILED": "failed",
                "PENDING": "processing",
                "RUNNING": "processing",
                "THROTTLED": "processing",
            }
            return {
                "state": state_map.get(status, "processing"),
                "video_url": video_url,
                "progress": data.get("progressRatio", 0),
                "error": data.get("failure", None)
            }
        else:
            return {"state": "error", "error": f"خطأ {r.status_code}"}
    except Exception as e:
        return {"state": "error", "error": str(e)}


# ─── Prompt Builders ──────────────────────────────────────────────────────────
def build_mahwous_product_prompt(info: dict, outfit: str = "suit",
                                  scene: str = "store", platform_aspect: str = "1:1") -> str:
    outfit_desc = MAHWOUS_OUTFITS.get(outfit, MAHWOUS_OUTFITS["suit"])
    scenes = {
        "store":   "Inside a breathtaking luxury dark perfume boutique — backlit golden shelves of rare fragrances, warm amber spotlights, polished obsidian floor reflecting light",
        "beach":   "At a cinematic golden-hour beach — warm amber sky, gentle foamy waves, dramatic sunset casting long shadows, sand glimmering",
        "desert":  "Vast golden Arabian desert at dusk — towering dunes with razor-sharp edges, amber sky with scattered stars, warm desert breeze particles",
        "studio":  "Inside a minimalist luxury dark studio — floating golden bokeh particles, dramatic rim lighting from above, velvety dark backdrop",
        "garden":  "In a lush royal fragrance garden at magic hour — cascading rose petals, golden mist, ornate marble fountain in background",
        "rooftop": "On a glass-barrier luxury rooftop at night — twinkling city skyline below, starry sky above, ambient evening glow",
        "car":     "Rear seat of a Rolls-Royce Phantom — cream leather interior, city lights blurring past rain-dotted windows, subtle warm console glow",
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

CRITICAL BOTTLE RULE: The bottle must be 100% photorealistic, matching the original design exactly. NO distortion, NO simplification, NO invented details.

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
Placement: centered on aged dark marble slab. Soft golden light from upper-right. Silk fabric draped elegantly beside bottle. Tiny ambient golden particles floating.
Mood: museum-quality product shot — luxurious, aspirational, editorial.
Specular highlights on glass, subtle caustics from bottle. Perfect label legibility.
Aspect ratio: {platform_aspect}.
{QUALITY}"""


def build_ramadan_product_prompt(info: dict, platform_aspect: str = "9:16") -> str:
    product_name = info.get("product_name", "luxury perfume")
    brand = info.get("brand", "premium brand")
    colors = ", ".join(info.get("colors", ["gold", "black"]))
    return f"""Luxury Ramadan perfume advertisement. 
Subject: {product_name} by {brand} bottle. Colors: {colors}.
Setting: Ornate Ramadan scene — glowing golden crescent moon and fanoos lantern hanging above, scattered rose petals and oud chips, soft warm candlelight.
Bottle centered prominently, surrounded by tasteful Islamic geometric gold ornaments.
Atmosphere: warm amber and deep gold tones, reverent and aspirational.
Aspect ratio: {platform_aspect}.
{QUALITY}"""


def build_video_prompt(info: dict, scene: str = "store", outfit: str = "suit",
                        duration: int = 7, camera_move: str = "push_in",
                        scene_type: str = "مهووس مع العطر", mood_extra: str = "") -> str:
    """بناء برومت فيديو سينمائي متكامل"""
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
AUDIO: Elegant ambient music, subtle golden chime sound effects.

STRICT RULES:
- NO text on screen. NO watermarks. NO subtitles.
- NO perfume spraying. Replace with: golden luminous particles floating gently.
- Mahwous mouth CLOSED when perfume speaks.
- MAINTAIN exact bottle design — photorealistic, no distortion.
- Professional cinema quality. Smooth transitions."""


# ─── Generate All Platform Images ─────────────────────────────────────────────
def generate_platform_images(info: dict, selected_platforms: list, outfit: str, scene: str,
                               include_character: bool = True, progress_callback=None,
                               ramadan_mode: bool = False) -> dict:
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

        img_bytes = generate_image_gemini(prompt, plat["aspect"])
        results[plat_key] = {
            "bytes":   img_bytes,
            "label":   plat["label"],
            "emoji":   plat["emoji"],
            "w":       plat["w"],
            "h":       plat["h"],
            "aspect":  plat["aspect"],
            "prompt":  prompt,
        }

    if progress_callback:
        progress_callback(1.0, "✅ اكتملت جميع الصور!")
    return results


# ─── Generate All Platform Captions ───────────────────────────────────────────
def generate_all_captions(info: dict) -> dict:
    system = """أنت أفضل كاتب محتوى عطور فاخرة في الخليج العربي.
أسلوبك: شعري، عاطفي، فاخر، مع هوك جذاب في كل منصة.
اللغة: عربية خليجية راقية — ليست فصحى متصلبة، ليست عامية ركيكة.
الأيقونات: استخدم إيموجي ذكي ومناسب بحد أقصى 3-4 لكل نص."""

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

اكتب 5 أوصاف تسويقية باللغة العربية الفصحى الراقية. JSON فقط:
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
  "brand":    ["#brand_specific × 5 — علامة تجارية"],
  "trending": ["#trending_now × 5 — الأكثر انتشاراً الآن"]
}}"""
    text = smart_generate_text(prompt, temperature=0.6)
    try:
        return clean_json(text)
    except:
        return {}


def generate_scenario(info: dict, scene_type: str = "مهووس مع العطر",
                       scene: str = "store", outfit: str = "suit",
                       duration: int = 7) -> dict:
    """توليد سيناريو فيديو كامل"""
    system = """أنت مخرج فيديو سينمائي متخصص في إعلانات العطور الفاخرة.
أسلوبك: سينمائي، درامي، فاخر. تكتب سيناريوهات جاهزة للتنفيذ."""

    prompt = f"""اكتب سيناريو فيديو {duration} ثانية لعطر "{info.get('product_name', 'عطر فاخر')}" من "{info.get('brand', 'علامة فاخرة')}".
نوع المشهد: {scene_type} | المكان: {scene} | الزي: {outfit}
المزاج: {info.get('mood', 'فاخر وغامض')}

أجب بـ JSON فقط:
{{
  "title": "عنوان السيناريو",
  "hook": "الهوك الجذاب في أول 2 ثانية",
  "scenes": [
    {{"time": "0-2s", "action": "وصف المشهد", "camera": "حركة الكاميرا", "audio": "الصوت/الموسيقى"}},
    {{"time": "2-5s", "action": "وصف المشهد", "camera": "حركة الكاميرا", "audio": "الصوت/الموسيقى"}},
    {{"time": "5-7s", "action": "وصف المشهد", "camera": "حركة الكاميرا", "audio": "الصوت/الموسيقى"}}
  ],
  "cta": "دعوة للعمل في النهاية",
  "video_prompt": "البرومت الكامل للفيديو بالإنجليزية لـ Luma/RunwayML",
  "flow_prompt": "البرومت الكامل لـ Google Flow/Veo بالإنجليزية"
}}"""

    text = smart_generate_text(prompt, system, temperature=0.8)
    try:
        return clean_json(text)
    except:
        return {
            "title": f"إعلان {info.get('product_name', 'العطر')}",
            "hook": "لقطة مقربة على العطر مع موسيقى هادئة",
            "scenes": [
                {"time": "0-2s", "action": "لقطة تقديمية للعطر", "camera": "push-in", "audio": "موسيقى هادئة"},
                {"time": "2-5s", "action": "مهووس يمسك العطر", "camera": "orbit", "audio": "صوت عميق"},
                {"time": "5-7s", "action": "لقطة نهائية مع الشعار", "camera": "static", "audio": "fade out"},
            ],
            "cta": "اكتشف العطر الآن",
            "video_prompt": build_video_prompt(info, scene, outfit, duration),
            "flow_prompt": build_video_prompt(info, scene, outfit, duration),
        }


def generate_perfume_story(info: dict) -> str:
    """توليد قصة عطر سردية"""
    prompt = f"""اكتب قصة سردية شعرية وعاطفية عن عطر "{info.get('product_name', 'العطر')}" من "{info.get('brand', 'العلامة')}".
المزاج: {info.get('mood', 'فاخر وغامض')} | الملاحظات: {info.get('notes_guess', 'عود وعنبر')}
الأسلوب: أدبي راقٍ، يربط العطر بمشاعر ولحظات حياتية فاخرة.
الطول: 200-250 كلمة. اللغة: عربية فصحى جذابة."""
    try:
        return smart_generate_text(prompt, temperature=0.9)
    except:
        return f"عطر {info.get('product_name', '')} من {info.get('brand', '')} — رحلة عطرية لا تُنسى..."


def build_manual_info(name, brand, type_, size, gender, style, colors, bottle_shape, mood, notes) -> dict:
    return {
        "product_name": name, "brand": brand, "type": type_, "size": size,
        "gender": gender, "style": style, "colors": colors if isinstance(colors, list) else [colors],
        "bottle_shape": bottle_shape, "mood": mood, "notes_guess": notes,
        "bottle_cap": "polished cap", "bottle_material": "premium glass",
        "label_style": "elegant label", "bottle_uniqueness": "",
        "image_quality": "good", "confidence": 0.8
    }


def send_to_make(data: dict) -> bool:
    """إرسال البيانات إلى Make.com webhook"""
    secrets = _get_secrets()
    if not secrets["webhook"]:
        return False
    try:
        r = requests.post(secrets["webhook"], json=data, timeout=15)
        return r.status_code in [200, 201, 202, 204]
    except:
        return False
