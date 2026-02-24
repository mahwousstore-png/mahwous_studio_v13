"""
🌟 Gemini All-In-One Engine v1.0
مفتاح واحد (GEMINI_API_KEY) يكفي لـ:
  • النصوص   → gemini-2.5-flash
  • الصور    → imagen-4.0-generate-001 + gemini-2.0-flash-exp (fallback)
  • الفيديو  → veo-3.1-generate-preview (يتطلب فوترة)
  • الصوت   → gemini-2.5-flash-preview-tts (مجاني!)
"""

import base64
import io
import json
import time
import requests
import streamlit as st
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
# BASE URL
# ══════════════════════════════════════════════════════════════════════════════
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

# النماذج
MODEL_TEXT      = "gemini-2.5-flash"
MODEL_TEXT_FAST = "gemini-2.0-flash"
MODEL_IMAGE_1   = "imagen-4.0-generate-001"
MODEL_IMAGE_2   = "gemini-2.0-flash-exp-image-generation"   # مجاني كـ fallback
MODEL_VIDEO     = "veo-3.1-generate-preview"
MODEL_TTS       = "gemini-2.5-flash-preview-tts"

# أصوات TTS المتاحة (تدعم العربية)
TTS_VOICES = {
    "Kore":    "🎙️ كور — نبرة هادئة واحترافية",
    "Charon":  "🎙️ شارون — صوت عميق وقوي",
    "Puck":    "🎙️ باك — خفيف وودود",
    "Fenrir":  "🎙️ فنرير — جريء ومميز",
    "Aoede":   "🎙️ آيود — ناعم ودافئ",
    "Leda":    "🎙️ ليدا — أنثوي رسمي",
    "Orus":    "🎙️ أوروس — ذكوري رسمي",
}


# ══════════════════════════════════════════════════════════════════════════════
# مفتاح API
# ══════════════════════════════════════════════════════════════════════════════
def _get_key() -> str:
    """جلب مفتاح Google Gemini من session أو secrets"""
    for sk in ["gemini_key", "google_key"]:
        v = st.session_state.get(sk, "")
        if v:
            return v
    try:
        for k in ["GEMINI_API_KEY", "GOOGLE_KEY", "GOOGLE_API_KEY"]:
            v = st.secrets.get(k, "")
            if v:
                return v
    except Exception:
        pass
    return ""


def _check_key() -> str:
    key = _get_key()
    if not key:
        raise ValueError("❌ مفتاح Gemini مفقود — أضفه في الإعدادات")
    return key


# ══════════════════════════════════════════════════════════════════════════════
# 1. توليد النصوص
# ══════════════════════════════════════════════════════════════════════════════
def gemini_text(prompt: str, system: str = "", model: str = MODEL_TEXT) -> str:
    """توليد نص بـ Gemini 2.5 Flash"""
    key = _check_key()
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.85, "maxOutputTokens": 8192},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    models = [model, MODEL_TEXT_FAST, "gemini-2.0-flash-lite"]
    for m in models:
        try:
            r = requests.post(
                f"{GEMINI_BASE}/models/{m}:generateContent?key={key}",
                json=body, timeout=60
            )
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                continue
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            continue
    raise ValueError("فشل توليد النص — تأكد من صحة المفتاح")


def gemini_json(prompt: str, system: str = "") -> dict:
    """توليد JSON منظّم بـ Gemini"""
    key = _check_key()
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.85
        },
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    for m in [MODEL_TEXT, MODEL_TEXT_FAST]:
        try:
            r = requests.post(
                f"{GEMINI_BASE}/models/{m}:generateContent?key={key}",
                json=body, timeout=60
            )
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                continue
            raw = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw.strip())
            return parsed[0] if isinstance(parsed, list) else parsed
        except Exception:
            continue
    raise ValueError("فشل توليد JSON")


# ══════════════════════════════════════════════════════════════════════════════
# 2. توليد الصور
# ══════════════════════════════════════════════════════════════════════════════
def gemini_image(prompt: str, aspect: str = "1:1") -> bytes:
    """
    توليد صورة — يجرب Imagen 4.0 أولاً، ثم Gemini 2.0 Flash كـ fallback
    """
    key = _check_key()

    # ── المحاولة 1: Imagen 4.0 ──────────────────────────────────────────────
    for img_model in ["imagen-4.0-generate-001", "imagen-3.0-generate-002"]:
        try:
            r = requests.post(
                f"{GEMINI_BASE}/models/{img_model}:predict?key={key}",
                json={
                    "instances": [{"prompt": prompt}],
                    "parameters": {
                        "sampleCount": 1,
                        "aspectRatio": aspect,
                        "personGeneration": "allow_all",
                        "safetyFilterLevel": "block_few"
                    }
                },
                timeout=90
            )
            if r.status_code in [403, 404, 429]:
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                continue
            preds = data.get("predictions", [])
            if preds and preds[0].get("bytesBase64Encoded"):
                return base64.b64decode(preds[0]["bytesBase64Encoded"])
        except Exception:
            continue

    # ── المحاولة 2: Gemini 2.0 Flash image generation (مجاني) ──────────────
    try:
        r = requests.post(
            f"{GEMINI_BASE}/models/{MODEL_IMAGE_2}:generateContent?key={key}",
            json={
                "contents": [{"parts": [{"text": f"Generate this image: {prompt}"}]}],
                "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
            },
            timeout=90
        )
        r.raise_for_status()
        data = r.json()
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if part.get("inlineData", {}).get("mimeType", "").startswith("image"):
                return base64.b64decode(part["inlineData"]["data"])
    except Exception:
        pass

    raise ValueError(
        "فشل توليد الصورة.\n"
        "• Imagen 4.0 يتطلب تفعيل الفوترة في Google Cloud Console\n"
        "• تأكد من صحة GEMINI_API_KEY"
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3. توليد الصوت (TTS)
# ══════════════════════════════════════════════════════════════════════════════
def gemini_tts(text: str, voice: str = "Charon", language: str = "ar") -> bytes:
    """
    توليد صوت عربي بـ Gemini 2.5 Flash TTS
    يُرجع bytes (PCM raw → يمكن تحويله لـ WAV)
    """
    key = _check_key()

    # بروبت يوجه النموذج للتحدث بالعربية
    styled_text = f"تكلّم بالعربية بصوت واضح وطبيعي: {text}"

    body = {
        "contents": [{"parts": [{"text": styled_text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": voice}
                }
            }
        }
    }

    for tts_model in ["gemini-2.5-flash-preview-tts", "gemini-2.0-flash-preview-tts"]:
        try:
            r = requests.post(
                f"{GEMINI_BASE}/models/{tts_model}:generateContent?key={key}",
                json=body, timeout=60
            )
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                continue
            parts = data["candidates"][0]["content"]["parts"]
            for part in parts:
                if part.get("inlineData"):
                    return base64.b64decode(part["inlineData"]["data"])
        except Exception as e:
            if "404" not in str(e):
                raise e
            continue

    raise ValueError(
        "فشل توليد الصوت.\n"
        "• gemini-2.5-flash-preview-tts يتطلب تفعيل البيلينج أو الوصول المبكر\n"
        "• تأكد من صحة GEMINI_API_KEY"
    )


def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000,
               channels: int = 1, sample_width: int = 2) -> bytes:
    """تحويل PCM خام إلى WAV قابل للتشغيل"""
    import struct
    data_size = len(pcm_data)
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE',
        b'fmt ', 16, 1, channels, sample_rate,
        sample_rate * channels * sample_width, channels * sample_width,
        sample_width * 8, b'data', data_size
    )
    return header + pcm_data


# ══════════════════════════════════════════════════════════════════════════════
# 4. توليد الفيديو (Veo 3.1)
# ══════════════════════════════════════════════════════════════════════════════
def gemini_video_start(prompt: str, aspect: str = "9:16",
                        duration: int = 8, image_bytes: bytes = None) -> dict:
    """
    بدء توليد فيديو بـ Veo 3.1 (عملية غير متزامنة)
    يُرجع dict يحتوي على name عملية اللونج-رانينج لمتابعتها
    """
    key = _check_key()

    config = {
        "aspectRatio": aspect,
        "durationSeconds": str(duration),
        "generateAudio": True,
        "numberOfVideos": 1,
    }

    instance: dict = {"prompt": prompt}
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        instance["image"] = {
            "bytesBase64Encoded": b64,
            "mimeType": "image/jpeg"
        }

    body = {
        "instances": [instance],
        "parameters": config
    }

    try:
        r = requests.post(
            f"{GEMINI_BASE}/models/{MODEL_VIDEO}:predictLongRunning?key={key}",
            json=body, timeout=30
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            err = data["error"]
            code = err.get("code", 0)
            msg  = err.get("message", "خطأ غير معروف")
            if code == 403:
                raise ValueError("❌ Veo 3.1 يتطلب تفعيل الفوترة في Google Cloud Console\n→ اذهب إلى console.cloud.google.com/billing")
            elif code == 400:
                raise ValueError(f"❌ بروبت غير مناسب أو إعداد خاطئ: {msg}")
            raise ValueError(f"❌ {code}: {msg}")
        op_name = data.get("name", "")
        if not op_name:
            raise ValueError("لم يتم إرجاع معرف العملية")
        return {"operation": op_name, "state": "pending"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            raise ValueError("❌ Veo 3.1 يتطلب تفعيل الفوترة في Google Cloud Console")
        raise ValueError(f"❌ HTTP {e.response.status_code}: {e.response.text[:200]}")


def gemini_video_status(operation_name: str) -> dict:
    """
    فحص حالة عملية توليد الفيديو
    """
    key = _check_key()
    try:
        r = requests.get(
            f"{GEMINI_BASE}/{operation_name}?key={key}",
            timeout=20
        )
        r.raise_for_status()
        data = r.json()

        if data.get("done"):
            resp = data.get("response", {})
            videos = resp.get("generatedSamples", []) or resp.get("generatedVideos", [])
            if videos:
                video_info = videos[0]
                video_uri  = (video_info.get("video", {}).get("uri") or
                              video_info.get("videoUri", "") or
                              video_info.get("uri", ""))
                return {"state": "completed", "video_uri": video_uri, "raw": data}
            return {"state": "failed", "error": "لم يتم إرجاع فيديو"}

        # لا يزال قيد المعالجة
        metadata = data.get("metadata", {})
        progress = metadata.get("progressPercent", 0)
        return {"state": "processing", "progress": progress, "raw": data}

    except Exception as e:
        return {"state": "error", "error": str(e)[:200]}


def gemini_video_download(video_uri: str) -> bytes:
    """تحميل الفيديو المُولَّد"""
    key = _check_key()
    # إضافة key للـ URI إذا كان مسار Gemini API
    if "generativelanguage.googleapis.com" in video_uri:
        sep = "&" if "?" in video_uri else "?"
        url = f"{video_uri}{sep}key={key}&alt=media"
    else:
        url = video_uri
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    return r.content


