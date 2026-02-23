"""
🤖 محرك الذكاء الاصطناعي — Mahwous AI Studio v13.1
Gemini 2.0 Flash + Imagen 3 + Claude 3.5 Sonnet + Luma + RunwayML + Fal.ai + ElevenLabs
"""

import streamlit as st
import requests
import json
import base64
import os
import time
import concurrent.futures
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
# الثوابت
# ══════════════════════════════════════════════════════════════════════════════

PLATFORMS = {
    "instagram_post":  {"label": "Instagram Post",   "emoji": "📸", "w": 1080, "h": 1080, "aspect": "1:1"},
    "instagram_story": {"label": "Instagram Story",  "emoji": "📱", "w": 1080, "h": 1920, "aspect": "9:16"},
    "tiktok":          {"label": "TikTok",            "emoji": "🎵", "w": 1080, "h": 1920, "aspect": "9:16"},
    "youtube_short":   {"label": "YouTube Short",    "emoji": "▶️", "w": 1080, "h": 1920, "aspect": "9:16"},
    "youtube_thumb":   {"label": "YouTube Thumbnail","emoji": "🎬", "w": 1280, "h": 720,  "aspect": "16:9"},
    "twitter":         {"label": "Twitter/X",         "emoji": "🐦", "w": 1200, "h": 675,  "aspect": "16:9"},
    "facebook":        {"label": "Facebook",          "emoji": "👍", "w": 1200, "h": 630,  "aspect": "16:9"},
    "snapchat":        {"label": "Snapchat",          "emoji": "👻", "w": 1080, "h": 1920, "aspect": "9:16"},
    "linkedin":        {"label": "LinkedIn",          "emoji": "💼", "w": 1200, "h": 627,  "aspect": "16:9"},
    "pinterest":       {"label": "Pinterest",         "emoji": "📌", "w": 1000, "h": 1500, "aspect": "2:3"},
}

MAHWOUS_OUTFITS = {
    "suit":    "elegant black suit with golden embroidery and golden tie, luxury brand ambassador",
    "hoodie":  "signature black hoodie with golden Mahwous logo, streetwear luxury style",
    "thobe":   "royal white thobe with golden trim and embroidery, traditional Arab luxury",
    "casual":  "smart casual dark outfit with golden chain accessory, modern elegant style",
    "western": "stylish leather western jacket with dark jeans, bold masculine style",
}

FAL_VIDEO_MODELS = {
    "kling":  "fal-ai/kling-video/v1.6/standard/image-to-video",
    "veo":    "fal-ai/veo2",
    "svd":    "fal-ai/stable-video",
}

# ══════════════════════════════════════════════════════════════════════════════
# الأسرار / المفاتيح
# ══════════════════════════════════════════════════════════════════════════════

def _get_secrets() -> dict:
    """جلب مفاتيح API من Streamlit secrets أو session_state"""
    def _get(toml_key: str, session_key: str, env_key: str = "") -> str:
        # 1) session_state
        val = st.session_state.get(session_key, "")
        if val:
            return val
        # 2) streamlit secrets
        try:
            return st.secrets.get(toml_key, "")
        except Exception:
            pass
        # 3) env var
        if env_key:
            return os.environ.get(env_key, "")
        return ""

    return {
        "gemini":     _get("GEMINI_API_KEY",      "gemini_key",      "GEMINI_API_KEY"),
        "openrouter": _get("OPENROUTER_API_KEY",   "openrouter_key",  "OPENROUTER_API_KEY"),
        "luma":       _get("LUMA_API_KEY",         "luma_key",        "LUMA_API_KEY"),
        "runway":     _get("RUNWAY_API_KEY",        "runway_key",      "RUNWAY_API_KEY"),
        "fal":        _get("FAL_API_KEY",           "fal_key",         "FAL_API_KEY"),
        "imgbb":      _get("IMGBB_API_KEY",         "imgbb_key",       "IMGBB_API_KEY"),
        "elevenlabs": _get("ELEVENLABS_API_KEY",    "elevenlabs_key",  "ELEVENLABS_API_KEY"),
        "webhook":    _get("MAKE_WEBHOOK_URL",      "webhook_url",     "MAKE_WEBHOOK_URL"),
        "supabase_url": _get("SUPABASE_URL",        "supabase_url",    "SUPABASE_URL"),
        "supabase_key": _get("SUPABASE_KEY",        "supabase_key",    "SUPABASE_KEY"),
    }


def check_api_health() -> dict:
    """فحص صحة كل API"""
    secrets = _get_secrets()
    results = {}

    # Gemini
    if secrets.get("gemini"):
        try:
            r = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={secrets['gemini']}",
                timeout=8
            )
            results["gemini"] = {"ok": r.status_code == 200, "msg": "متصل" if r.status_code == 200 else f"خطأ {r.status_code}"}
        except Exception as e:
            results["gemini"] = {"ok": False, "msg": str(e)[:50]}
    else:
        results["gemini"] = {"ok": False, "msg": "مفتاح مفقود"}

    # Luma
    if secrets.get("luma"):
        try:
            r = requests.get("https://api.lumalabs.ai/dream-machine/v1/generations",
                             headers={"Authorization": f"Bearer {secrets['luma']}"}, timeout=8)
            results["luma"] = {"ok": r.status_code in [200, 404], "msg": "متصل" if r.status_code in [200, 404] else f"خطأ {r.status_code}"}
        except Exception as e:
            results["luma"] = {"ok": False, "msg": str(e)[:50]}
    else:
        results["luma"] = {"ok": False, "msg": "مفتاح مفقود"}

    # OpenRouter
    if secrets.get("openrouter"):
        try:
            r = requests.get("https://openrouter.ai/api/v1/models",
                             headers={"Authorization": f"Bearer {secrets['openrouter']}"}, timeout=8)
            results["openrouter"] = {"ok": r.status_code == 200, "msg": "متصل" if r.status_code == 200 else f"خطأ {r.status_code}"}
        except Exception as e:
            results["openrouter"] = {"ok": False, "msg": str(e)[:50]}
    else:
        results["openrouter"] = {"ok": False, "msg": "مفتاح مفقود"}

    # Fal
    results["fal"] = {"ok": bool(secrets.get("fal")), "msg": "مفعّل" if secrets.get("fal") else "مفتاح مفقود"}

    return results


# ══════════════════════════════════════════════════════════════════════════════
# تحليل صورة العطر
# ══════════════════════════════════════════════════════════════════════════════

def analyze_perfume_image(image_bytes: bytes) -> dict:
    """تحليل صورة العطر بـ Gemini 2.0 Flash Vision"""
    secrets = _get_secrets()
    api_key = secrets.get("gemini")
    if not api_key:
        raise ValueError("GEMINI_API_KEY مفقود — أضفه في إعدادات API")

    b64 = base64.b64encode(image_bytes).decode()
    prompt = """أنت خبير تقييم عطور فاخرة. حلّل هذه الصورة وأعطني JSON فقط:
{
  "brand": "اسم العلامة التجارية",
  "product_name": "اسم المنتج الكامل",
  "type": "EDP/EDT/EDP Intense/Parfum",
  "size": "حجم الزجاجة (مل)",
  "gender": "masculine/feminine/unisex",
  "style": "luxury/oriental/niche/sport/modern/classic",
  "colors": ["#hex1", "#hex2"],
  "bottle_shape": "وصف شكل الزجاجة بالإنجليزية",
  "mood": "المزاج العطري المتوقع (عربي)",
  "notes_guess": "ملاحظات العطر المتوقعة (عربي)",
  "confidence": 0.95
}"""

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
            ]
        }],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800}
    }

    # FIX: استخدام gemini-2.0-flash-lite بدلاً من gemini-2.0-flash لتجنب 429
    # مع retry logic للتعامل مع rate limits
    models_to_try = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]

    last_error = None
    for model in models_to_try:
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                json=payload, timeout=30
            )
            if resp.status_code == 429:
                last_error = f"429 Rate Limit on {model}"
                time.sleep(2)
                continue
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            if "```" in text:
                text = text.split("```")[1].lstrip("json").strip()
            return json.loads(text)
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                last_error = str(e)
                time.sleep(2)
                continue
            raise
        except Exception as e:
            last_error = str(e)
            continue

    raise ValueError(f"فشل تحليل الصورة بجميع النماذج: {last_error}")


# ══════════════════════════════════════════════════════════════════════════════
# توليد الصور
# ══════════════════════════════════════════════════════════════════════════════

def _build_image_prompt(info: dict, platform_key: str, outfit: str, scene: str,
                         include_character: bool, ramadan_mode: bool) -> str:
    brand        = info.get("brand", "luxury brand")
    product_name = info.get("product_name", "luxury fragrance")
    colors       = info.get("colors", ["gold", "black"])
    colors_str   = ", ".join(colors[:3]) if isinstance(colors, list) else "gold and black"
    mood         = info.get("mood", "luxurious and sophisticated")
    plat         = PLATFORMS.get(platform_key, {})
    aspect       = plat.get("aspect", "1:1")
    outfit_desc  = MAHWOUS_OUTFITS.get(outfit, MAHWOUS_OUTFITS["suit"])

    scene_descriptions = {
        "store":   "inside a luxury perfume boutique with golden shelves, marble floors, warm ambient lighting",
        "beach":   "at a golden sunset beach, soft waves, sand dunes, warm orange horizon",
        "desert":  "in a vast golden sand desert at sunset, dunes, dramatic sky",
        "studio":  "in a professional photography studio with dramatic chiaroscuro lighting, black backdrop",
        "garden":  "in a royal rose garden with fountains, green hedges, soft natural light",
        "rooftop": "on the rooftop of a luxury skyscraper at night, city lights bokeh",
        "car":     "inside the interior of a luxury sports car, leather seats, soft ambient lighting",
    }
    scene_desc = scene_descriptions.get(scene, "in an elegant luxury setting")

    ramadan_elements = ""
    if ramadan_mode:
        ramadan_elements = "Ramadan Kareem atmosphere with golden crescent moon, traditional lanterns, star motifs, warm glowing lights, "

    if include_character:
        char_desc = (
            "Mahwous, a charismatic Arab male brand ambassador with black neatly styled hair, "
            "short trimmed brown beard, warm expressive brown eyes"
        )
        return (
            f"Ultra-realistic professional commercial photo, {char_desc}, "
            f"wearing {outfit_desc}, confidently holding the {brand} {product_name} perfume bottle, "
            f"{scene_desc}. {ramadan_elements}"
            f"Mood: {mood}. Colors: {colors_str}. "
            f"Cinematic lighting, luxury advertising photography, 4K, sharp focus, "
            f"photorealistic, aspect ratio {aspect}. "
            f"DO NOT include any text or watermarks."
        )
    else:
        return (
            f"Ultra-realistic luxury product photography of {brand} {product_name} perfume bottle, "
            f"elegant flacon with {colors_str} color palette, {scene_desc}. "
            f"{ramadan_elements}Mood: {mood}. "
            f"Professional studio lighting, reflective marble surface, soft bokeh background, "
            f"luxury brand advertisement, 4K sharp, aspect ratio {aspect}. "
            f"DO NOT include any text or watermarks."
        )


def generate_image_gemini(prompt: str, aspect: str = "1:1") -> Optional[bytes]:
    """توليد صورة بـ Imagen 3 عبر Gemini API"""
    secrets = _get_secrets()
    api_key = secrets.get("gemini")
    if not api_key:
        raise ValueError("GEMINI_API_KEY مفقود")

    aspect_map = {"1:1": "1:1", "9:16": "9:16", "16:9": "16:9", "2:3": "2:3"}
    ar = aspect_map.get(aspect, "1:1")

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": ar,
            "safetyFilterLevel": "block_few",
            "personGeneration": "allow_adult"
        }
    }

    # FIX: استخدام Gemini Imagen API المباشرة أولاً (بدلاً من Vertex AI الذي يتطلب OAuth2)
    # Vertex AI endpoint يتطلب Bearer token من Google OAuth2 وليس API key مباشر
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}",
        json=payload,
        timeout=60
    )

    if resp.status_code == 200:
        data = resp.json()
    else:
        raise ValueError(f"Imagen API error {resp.status_code}: {resp.text[:300]}")

    predictions = data.get("predictions", [])
    if not predictions:
        raise ValueError("لم يتم إرجاع صور من Imagen 3")

    b64_img = predictions[0].get("bytesBase64Encoded") or predictions[0].get("imageBytes", "")
    if not b64_img:
        raise ValueError("لم يتم إرجاع بيانات الصورة")

    return base64.b64decode(b64_img)


def smart_generate_image(prompt: str, aspect: str = "1:1") -> Optional[bytes]:
    """توليد صورة ذكي: يجرب Fal.ai أولاً ثم Gemini Imagen"""
    # FIX: Fal.ai أكثر موثوقية للصور — نبدأ به
    try:
        return _generate_image_fal_flux(prompt, aspect)
    except Exception:
        pass
    # Fallback إلى Gemini Imagen
    try:
        return generate_image_gemini(prompt, aspect)
    except Exception:
        pass
    raise ValueError("فشل توليد الصورة من جميع المزودين")


def _generate_image_fal_flux(prompt: str, aspect: str = "1:1") -> Optional[bytes]:
    """توليد صورة بـ Fal.ai Flux Dev"""
    secrets = _get_secrets()
    api_key = secrets.get("fal")
    if not api_key:
        raise ValueError("FAL_API_KEY مفقود")

    os.environ["FAL_KEY"] = api_key

    # FIX: تصحيح قيم image_size لتتوافق مع Fal.ai API
    # القيم الصحيحة: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
    aspect_map = {
        "1:1":  "square_hd",
        "9:16": "portrait_16_9",
        "16:9": "landscape_16_9",
        "2:3":  "portrait_4_3",
        "4:3":  "landscape_4_3",
    }
    img_size = aspect_map.get(aspect, "square_hd")

    # FIX: endpoint صحيح لـ Fal.ai Flux Dev
    resp = requests.post(
        "https://fal.run/fal-ai/flux/dev",
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "image_size": img_size,
            "num_inference_steps": 28,
            "num_images": 1,
            "enable_safety_checker": False,
            "output_format": "jpeg"
        },
        timeout=120
    )
    resp.raise_for_status()
    result = resp.json()
    images = result.get("images", [])
    if not images:
        raise ValueError("لم يتم إرجاع صور من Fal.ai")
    img_url = images[0].get("url", "")
    if not img_url:
        raise ValueError("رابط الصورة فارغ من Fal.ai")
    img_resp = requests.get(img_url, timeout=30)
    img_resp.raise_for_status()
    return img_resp.content


def generate_platform_images(info: dict, selected_platforms: list,
                              outfit: str = "suit", scene: str = "store",
                              include_character: bool = True,
                              ramadan_mode: bool = False) -> dict:
    """توليد صور لمنصات محددة"""
    results = {}
    for platform_key in selected_platforms:
        plat = PLATFORMS.get(platform_key, {})
        if not plat:
            continue
        prompt = _build_image_prompt(info, platform_key, outfit, scene, include_character, ramadan_mode)
        try:
            img_bytes = smart_generate_image(prompt, plat.get("aspect", "1:1"))
            results[platform_key] = {
                "bytes": img_bytes,
                "w": plat["w"], "h": plat["h"],
                "label": plat["label"],
                "emoji": plat["emoji"],
            }
        except Exception as e:
            results[platform_key] = {
                "bytes": None, "error": str(e),
                "w": plat["w"], "h": plat["h"],
                "label": plat["label"],
                "emoji": plat["emoji"],
            }
    return results


def generate_concurrent_images(info: dict, outfit: str = "suit", scene: str = "store",
                                include_character: bool = True,
                                ramadan_mode: bool = False) -> dict:
    """توليد صور لجميع المنصات بشكل متوازي"""
    all_platforms = list(PLATFORMS.keys())

    def _gen_one(platform_key):
        plat = PLATFORMS[platform_key]
        prompt = _build_image_prompt(info, platform_key, outfit, scene, include_character, ramadan_mode)
        try:
            img_bytes = smart_generate_image(prompt, plat.get("aspect", "1:1"))
            return platform_key, {
                "bytes": img_bytes,
                "w": plat["w"], "h": plat["h"],
                "label": plat["label"], "emoji": plat["emoji"]
            }
        except Exception as e:
            return platform_key, {
                "bytes": None, "error": str(e),
                "w": plat["w"], "h": plat["h"],
                "label": plat["label"], "emoji": plat["emoji"]
            }

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_gen_one, pk): pk for pk in all_platforms}
        for future in concurrent.futures.as_completed(futures):
            pk, data = future.result()
            results[pk] = data
    return results


def generate_image_remix_fal(prompt: str, image_bytes: bytes, strength: float = 0.6) -> Optional[bytes]:
    """ريمكس صورة (تغيير الخلفية مع الحفاظ على الشكل)"""
    secrets = _get_secrets()
    api_key = secrets.get("fal")
    if not api_key:
        raise ValueError("FAL_API_KEY مفقود")

    b64 = base64.b64encode(image_bytes).decode()
    data_uri = f"data:image/jpeg;base64,{b64}"

    # FIX: endpoint صحيح لـ image-to-image في Fal.ai
    resp = requests.post(
        "https://fal.run/fal-ai/flux/dev/image-to-image",
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "image_url": data_uri,
            "strength": strength,
            "num_inference_steps": 28,
            "num_images": 1,
            "output_format": "jpeg"
        },
        timeout=120
    )
    resp.raise_for_status()
    result = resp.json()
    images = result.get("images", [])
    if not images:
        raise ValueError("لم يتم إرجاع صور من Fal.ai image-to-image")
    img_url = images[0].get("url", "")
    if not img_url:
        raise ValueError("رابط الصورة فارغ")
    img_resp = requests.get(img_url, timeout=30)
    img_resp.raise_for_status()
    return img_resp.content


# ══════════════════════════════════════════════════════════════════════════════
# توليد النصوص (Claude 3.5 via OpenRouter)
# ══════════════════════════════════════════════════════════════════════════════

def _call_claude(prompt: str, max_tokens: int = 2000) -> str:
    """استدعاء Claude 3.5 Sonnet عبر OpenRouter"""
    secrets = _get_secrets()
    api_key = secrets.get("openrouter")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY مفقود — أضفه في إعدادات API")

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mahwousstore.com",
            "X-Title": "Mahwous AI Studio"
        },
        json={
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.8
        },
        timeout=60
    )
    resp.raise_for_status()
    data = resp.json()
    # FIX: التحقق من وجود 'choices' قبل الوصول إليه
    if "choices" not in data or not data["choices"]:
        raise ValueError(f"استجابة OpenRouter غير متوقعة: {json.dumps(data)[:200]}")
    return data["choices"][0]["message"]["content"].strip()


def _parse_json_response(text: str) -> dict:
    """تحويل استجابة النص إلى JSON"""
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if part.startswith("json"):
                text = part[4:].strip()
                break
            elif "{" in part or "[" in part:
                text = part.strip()
                break
    text = text.strip()
    return json.loads(text)


def generate_all_captions(info: dict) -> dict:
    """توليد تعليقات لجميع المنصات"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    mood    = info.get("mood", "فاخر")
    notes   = info.get("notes_guess", "عود وعنبر")

    prompt = f"""أنت خبير تسويق رقمي للعطور الفاخرة. اكتب تعليقات تسويقية احترافية باللغة العربية الخليجية الراقية.

العطر: {brand} - {product}
المزاج: {mood}
الملاحظات: {notes}
الكلمات المفتاحية للـ SEO: شراء عطور فاخرة، أفضل عطور نيش في السعودية، عطور أصلية للبيع، متجر عطور موثوق

أعطني JSON فقط (بدون نص إضافي):
{{
  "instagram_post": {{
    "caption": "تعليق جذاب للإنستقرام 150 كلمة يشمل قصة العطر وكلمات شرائية",
    "hashtags": ["#عطور_فاخرة", "#شراء_عطور_فاخرة", "#BrandName"]
  }},
  "instagram_story": {{
    "caption": "تعليق قصير للستوري 50 كلمة مع دعوة للشراء",
    "hashtags": ["#عطور_فاخرة", "#شراء_عطور_فاخرة"]
  }},
  "tiktok": {{
    "caption": "تعليق TikTok بأسلوب فيروسي 80 كلمة مع هوك صادم",
    "hashtags": ["#عطور_تيك_توك", "#عطور_فاخرة"]
  }},
  "twitter": {{
    "caption": "تعليق Twitter موجز 280 حرف مع هاشتاقات"
  }},
  "youtube_short": {{
    "caption": "وصف YouTube Short 100 كلمة مع كلمات مفتاحية SEO"
  }},
  "facebook": {{
    "caption": "تعليق Facebook 120 كلمة للجمهور الخليجي"
  }}
}}"""

    try:
        text = _call_claude(prompt, max_tokens=2500)
        return _parse_json_response(text)
    except Exception as e:
        return {"error": str(e)}


def generate_descriptions(info: dict) -> dict:
    """توليد أوصاف تسويقية بأطوال مختلفة"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    mood    = info.get("mood", "فاخر")
    notes   = info.get("notes_guess", "")

    prompt = f"""اكتب أوصافاً تسويقية للعطر التالي باللغة العربية الراقية:
العطر: {brand} - {product} | المزاج: {mood} | الملاحظات: {notes}

أعطني JSON فقط:
{{
  "short": "وصف قصير 30 كلمة للشبكات الاجتماعية",
  "medium": "وصف متوسط 80 كلمة للمنتج",
  "long": "وصف طويل 200 كلمة للموقع مع كلمات SEO (شراء عطور فاخرة، أفضل عطور نيش في السعودية)",
  "ad": "نص إعلاني 60 كلمة مع CTA واضح",
  "seo": {{
    "title": "عنوان SEO للصفحة",
    "meta": "Meta description 160 حرف",
    "content": "محتوى SEO 150 كلمة بكلمات مفتاحية"
  }}
}}"""

    try:
        text = _call_claude(prompt, max_tokens=2000)
        return _parse_json_response(text)
    except Exception as e:
        return {"error": str(e)}


def generate_hashtags(info: dict) -> dict:
    """توليد هاشتاقات منظمة"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    gender  = info.get("gender", "unisex")

    prompt = f"""اقترح هاشتاقات تسويقية للعطر: {brand} - {product} (للجنس: {gender})

أعطني JSON فقط:
{{
  "arabic": ["#عطر_رجالي", "#عطور_فاخرة", "#عطور_راقية", "#عطور_رجالية", "#عطر_مميز"],
  "english": ["#LuxuryFragrance", "#PerfumeCommunity", "#Perfume"],
  "brand": ["#{brand_no_spaces}", "#MahwousStore", "#عطور_مهووس"],
  "trending": ["#شراء_عطور_فاخرة", "#أفضل_عطور_نيش_في_السعودية", "#عطور_أصلية_للبيع", "#متجر_عطور_موثوق"]
}}"""

    try:
        text = _call_claude(prompt, max_tokens=800)
        return _parse_json_response(text)
    except Exception as e:
        return {"error": str(e)}


def generate_scenario(info: dict, scene_type: str = "مهووس مع العطر",
                       scene: str = "store", outfit: str = "suit",
                       duration: int = 7) -> dict:
    """توليد سيناريو فيديو احترافي"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    mood    = info.get("mood", "فاخر")

    prompt = f"""اكتب سيناريو فيديو احترافي {duration} ثواني للعطر: {brand} - {product}
المزاج: {mood} | نوع المشهد: {scene_type} | الموقع: {scene} | الزي: {outfit}

أعطني JSON فقط:
{{
  "title": "عنوان الفيديو",
  "hook": "الهوك الصادم في أول ثانيتين",
  "scenes": [
    {{"time": "0-2s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت"}},
    {{"time": "2-5s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت"}},
    {{"time": "5-{duration}s", "action": "وصف الحركة", "camera": "نوع اللقطة", "audio": "الصوت"}}
  ],
  "cta": "دعوة لاتخاذ إجراء",
  "video_prompt": "برومت الفيديو بالإنجليزية لـ Luma/RunwayML ({duration}-second cinematic video...)",
  "flow_prompt": "برومت مختصر لـ Google Flow/Veo"
}}"""

    try:
        text = _call_claude(prompt, max_tokens=1500)
        return _parse_json_response(text)
    except Exception as e:
        return {"error": str(e)}


def generate_perfume_story(info: dict) -> str:
    """توليد قصة شعرية للعطر"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")
    mood    = info.get("mood", "فاخر")
    notes   = info.get("notes_guess", "")

    prompt = f"""اكتب قصة شعرية راقية وجذابة عن العطر: {brand} - {product}
المزاج: {mood} | الملاحظات: {notes}
القصة يجب أن تكون باللغة العربية الفصيحة الراقية، 150-200 كلمة، تصف تجربة ارتداء العطر بأسلوب سردي شعري.
لا تضف أي تعليق قبل أو بعد القصة، فقط القصة مباشرة."""

    try:
        return _call_claude(prompt, max_tokens=600)
    except Exception as e:
        return f"خطأ في توليد القصة: {e}"


def analyze_competitor(info: dict, competitor_name: str) -> dict:
    """تحليل المنافس"""
    brand   = info.get("brand", "Unknown")
    product = info.get("product_name", "Unknown")

    prompt = f"""أنت خبير استراتيجي في تسويق العطور الفاخرة.
قارن بين: {brand} - {product} و {competitor_name}

أعطني JSON فقط:
{{
  "competitor_weakness": "أبرز نقطة ضعف عند المنافس",
  "our_advantage": "أبرز ميزة تنافسية لنا",
  "attack_angle": "زاوية الهجوم التسويقية الأمثل",
  "suggested_content": "محتوى مقترح للتفوق على المنافس"
}}"""

    try:
        text = _call_claude(prompt, max_tokens=600)
        return _parse_json_response(text)
    except Exception as e:
        return {"competitor_weakness": "—", "our_advantage": "—", "attack_angle": "—", "suggested_content": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# توليد الفيديو
# ══════════════════════════════════════════════════════════════════════════════

def _img_to_url_imgbb(image_bytes: bytes) -> Optional[str]:
    """رفع الصورة إلى ImgBB والحصول على رابط"""
    secrets = _get_secrets()
    api_key = secrets.get("imgbb")
    if not api_key or not image_bytes:
        return None
    try:
        b64 = base64.b64encode(image_bytes).decode()
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": b64},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["data"]["url"]
    except Exception:
        pass
    return None


def generate_video_luma(prompt: str, image_bytes: Optional[bytes] = None,
                         duration: int = 5, aspect_ratio: str = "9:16",
                         loop: bool = False) -> dict:
    """توليد فيديو بـ Luma Dream Machine"""
    secrets = _get_secrets()
    api_key = secrets.get("luma")
    if not api_key:
        return {"error": "LUMA_API_KEY مفقود — أضفه في إعدادات API"}

    # FIX: إضافة model parameter المطلوب (ray-2 هو النموذج الحالي)
    payload: dict = {
        "prompt": prompt,
        "model": "ray-2",
        "aspect_ratio": aspect_ratio,
        "loop": loop,
    }

    # FIX: إضافة resolution إذا كان duration محدداً
    if duration and duration > 0:
        payload["duration"] = f"{duration}s"

    if image_bytes:
        img_url = _img_to_url_imgbb(image_bytes)
        if img_url:
            payload["keyframes"] = {"frame0": {"type": "image", "url": img_url}}

    try:
        resp = requests.post(
            "https://api.lumalabs.ai/dream-machine/v1/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=payload,
            timeout=30
        )
        if resp.status_code in [200, 201]:
            data = resp.json()
            return {"id": data.get("id", ""), "state": data.get("state", "pending"), "provider": "luma"}
        return {"error": f"Luma API error {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def check_luma_status(generation_id: str) -> dict:
    """فحص حالة توليد Luma"""
    secrets = _get_secrets()
    api_key = secrets.get("luma")
    if not api_key or not generation_id:
        return {"state": "error", "error": "مفتاح أو معرف مفقود"}
    try:
        resp = requests.get(
            f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            state = data.get("state", "")
            video_url = ""
            if state == "completed":
                video_url = data.get("assets", {}).get("video", "")
            return {"state": state, "video_url": video_url, "progress": data.get("progress", 0)}
        return {"state": "error", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"state": "error", "error": str(e)}


def poll_luma_video(generation_id: str, timeout: int = 300) -> dict:
    """انتظار اكتمال فيديو Luma"""
    start = time.time()
    while time.time() - start < timeout:
        status = check_luma_status(generation_id)
        if status.get("state") == "completed":
            return status
        if status.get("state") in ["failed", "error"]:
            return status
        time.sleep(10)
    return {"state": "timeout", "error": "انتهت المهلة الزمنية"}


def generate_video_runway(prompt: str, image_bytes: Optional[bytes] = None,
                           aspect_ratio: str = "9:16", duration: int = 5) -> dict:
    """توليد فيديو بـ RunwayML Gen-4 Turbo"""
    secrets = _get_secrets()
    api_key = secrets.get("runway")
    if not api_key:
        return {"error": "RUNWAY_API_KEY مفقود — أضفه في إعدادات API"}

    # FIX: تصحيح ratio map وفق API version 2024-11-06
    # القيم الصحيحة: "1280:720", "720:1280", "1104:832", "960:960", "832:1104", "1584:672"
    ratio_map = {
        "9:16": "720:1280",
        "16:9": "1280:720",
        "1:1":  "960:960",
    }
    ratio = ratio_map.get(aspect_ratio, "720:1280")

    # FIX: تصحيح payload structure وفق API الحالي
    # model الصحيح: "gen4_turbo" (وليس "gen3a_turbo" الذي لا يزال مدعوماً لكن gen4_turbo أفضل)
    payload: dict = {
        "model": "gen4_turbo",
        "promptText": prompt,
        "ratio": ratio,
        "duration": min(max(duration, 2), 10),  # يجب أن يكون بين 2 و 10
    }

    # FIX: promptImage يجب أن يكون data URI أو HTTPS URL
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        payload["promptImage"] = f"data:image/jpeg;base64,{b64}"

    try:
        resp = requests.post(
            "https://api.dev.runwayml.com/v1/image_to_video",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-11-06"
            },
            json=payload,
            timeout=30
        )
        if resp.status_code in [200, 201]:
            data = resp.json()
            return {"id": data.get("id", ""), "state": "pending", "provider": "runway"}
        return {"error": f"RunwayML API error {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def check_runway_status(generation_id: str) -> dict:
    """فحص حالة توليد RunwayML"""
    secrets = _get_secrets()
    api_key = secrets.get("runway")
    if not api_key or not generation_id:
        return {"state": "error", "error": "مفتاح أو معرف مفقود"}
    try:
        resp = requests.get(
            f"https://api.dev.runwayml.com/v1/tasks/{generation_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "X-Runway-Version": "2024-11-06"
            },
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status", "")
            state_map = {"SUCCEEDED": "completed", "FAILED": "failed", "RUNNING": "processing", "PENDING": "pending"}
            state = state_map.get(status, status.lower())
            video_url = ""
            if state == "completed":
                output = data.get("output", [])
                video_url = output[0] if output else ""
            return {"state": state, "video_url": video_url, "progress": data.get("progressRatio", 0)}
        return {"state": "error", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"state": "error", "error": str(e)}


def generate_video_fal(prompt: str, model: str = "kling",
                        aspect_ratio: str = "9:16",
                        image_bytes: Optional[bytes] = None) -> dict:
    """توليد فيديو بـ Fal.ai"""
    secrets = _get_secrets()
    api_key = secrets.get("fal")
    if not api_key:
        return {"error": "FAL_API_KEY مفقود — أضفه في إعدادات API"}

    os.environ["FAL_KEY"] = api_key
    model_id = FAL_VIDEO_MODELS.get(model, FAL_VIDEO_MODELS["kling"])

    try:
        import fal_client

        args: dict = {"prompt": prompt, "aspect_ratio": aspect_ratio}
        if image_bytes:
            b64 = base64.b64encode(image_bytes).decode()
            args["image_url"] = f"data:image/jpeg;base64,{b64}"

        result = fal_client.run(model_id, arguments=args)
        video_url = (
            result.get("video", {}).get("url") or
            result.get("video_url") or
            result.get("url", "")
        )
        if video_url:
            return {"state": "completed", "video_url": video_url, "id": "fal_sync"}
        return {"state": "error", "error": "لم يتم إرجاع فيديو"}
    except Exception as e:
        return {"error": str(e)}


def check_fal_video_status(generation_id: str) -> dict:
    """فحص حالة توليد Fal (للتوافق — عادةً فوري)"""
    return {"state": "completed", "video_url": generation_id}


# ══════════════════════════════════════════════════════════════════════════════
# التعليق الصوتي
# ══════════════════════════════════════════════════════════════════════════════

def generate_voiceover_elevenlabs(text: str, voice_id: str = "default",
                                   api_key: str = "") -> bytes:
    """توليد تعليق صوتي بـ ElevenLabs"""
    secrets = _get_secrets()
    key = api_key or secrets.get("elevenlabs", "")
    if not key:
        raise ValueError("ELEVENLABS_API_KEY مفقود — أضفه في إعدادات API")
    if not text or not text.strip():
        raise ValueError("النص فارغ")

    # الصوت الافتراضي
    v_id = voice_id if voice_id and voice_id != "default" else "pNInz6obpgDQGcFmaJgB"

    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        },
        timeout=30
    )
    if resp.status_code == 200:
        return resp.content
    raise ValueError(f"ElevenLabs error {resp.status_code}: {resp.text[:200]}")


# ══════════════════════════════════════════════════════════════════════════════
# Make.com Webhook
# ══════════════════════════════════════════════════════════════════════════════

def build_make_payload(info: dict, image_urls: dict,
                        video_url: str, captions: dict) -> dict:
    """بناء payload لإرساله إلى Make.com"""
    return {
        "source": "Mahwous AI Studio v13.1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "perfume": {
            "brand":        info.get("brand", ""),
            "product_name": info.get("product_name", ""),
            "type":         info.get("type", ""),
            "gender":       info.get("gender", ""),
            "mood":         info.get("mood", ""),
        },
        "images": image_urls,
        "video_url": video_url,
        "captions": captions,
    }


def send_to_make(payload: dict) -> dict:
    """إرسال payload إلى Make.com Webhook"""
    secrets = _get_secrets()
    webhook_url = secrets.get("webhook", "")
    if not webhook_url:
        return {"success": False, "error": "MAKE_WEBHOOK_URL غير محدد — أضفه في الإعدادات"}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=30)
        return {
            "success": resp.status_code in [200, 201, 202, 204],
            "status_code": resp.status_code,
            "response": resp.text[:500]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# أدوات مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def build_manual_info(brand: str, product_name: str, colors: list,
                       bottle_shape: str, mood: str, notes_guess: str) -> dict:
    """بناء معلومات العطر يدوياً"""
    return {
        "brand": brand,
        "product_name": product_name,
        "type": "EDP",
        "gender": "unisex",
        "style": "luxury",
        "colors": colors or ["gold", "black"],
        "bottle_shape": bottle_shape,
        "mood": mood,
        "notes_guess": notes_guess,
        "confidence": 1.0
    }


def build_video_prompt(info: dict, scene: str = "store", outfit: str = "suit",
                        camera: str = "orbit", duration: int = 7,
                        aspect: str = "9:16", extra: str = "") -> str:
    """بناء برومت الفيديو"""
    brand    = info.get("brand", "luxury brand")
    product  = info.get("product_name", "luxury fragrance")
    mood     = info.get("mood", "luxurious and sophisticated")
    outfit_d = MAHWOUS_OUTFITS.get(outfit, MAHWOUS_OUTFITS["suit"])

    scene_map = {
        "store":   "luxury perfume boutique with golden shelves and warm ambient lighting",
        "beach":   "golden sunset beach with soft waves and sand dunes",
        "desert":  "vast golden sand desert at sunset with dramatic sky",
        "studio":  "professional photography studio with dramatic chiaroscuro lighting",
        "garden":  "royal rose garden with fountains and soft natural light",
        "rooftop": "rooftop of a luxury skyscraper at night with city lights bokeh",
        "car":     "interior of a luxury sports car with leather seats"
    }
    scene_desc = scene_map.get(scene, "elegant luxury setting")

    camera_map = {
        "push_in":  "slow push-in cinematic camera movement",
        "zoom":     "dramatic slow zoom",
        "orbit":    "smooth 360-degree orbit rotation",
        "static":   "perfectly still camera, static shot",
        "low_rise": "low-angle rising camera movement",
        "dolly":    "smooth dolly track movement",
        "crane":    "crane shot from above, sweeping movement"
    }
    cam_desc = camera_map.get(camera, "cinematic camera movement")

    prompt = (
        f"{duration}-second cinematic {aspect} video for luxury perfume advertising. "
        f"Mahwous, a charismatic Arab male brand ambassador with black hair, short beard, wearing {outfit_d}, "
        f"elegantly showcasing {brand} {product} perfume in {scene_desc}. "
        f"Camera: {cam_desc}. Mood: {mood}. "
        f"Style: ultra-cinematic, slow-motion highlights, dramatic lighting, luxury commercial quality."
    )
    if extra:
        prompt += f" Additional elements: {extra}."
    return prompt


def load_asset_bytes(path: str) -> Optional[bytes]:
    """تحميل ملف asset من المسار المحلي"""
    if not path:
        return None
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        # محاولة مسارات بديلة
        alt_paths = [
            path,
            os.path.join(".", path),
            os.path.join(os.path.dirname(__file__), "..", path),
        ]
        for p in alt_paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    return f.read()
    except Exception:
        pass
    return None
