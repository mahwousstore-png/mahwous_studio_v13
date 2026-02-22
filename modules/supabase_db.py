"""
🗄️ Supabase Database — مهووس AI Studio v13.0
حفظ بيانات العطور والصور في قاعدة بيانات Supabase
"""

import streamlit as st
import requests


def _get_supabase_config() -> tuple:
    """استرجاع إعدادات Supabase من session_state أو st.secrets"""
    def _s(session_key, secret_key, default=""):
        val = st.session_state.get(session_key, "")
        if val:
            return val
        try:
            return st.secrets.get(secret_key, default)
        except Exception:
            return default

    url = _s("supabase_url", "SUPABASE_URL")
    key = _s("supabase_key", "SUPABASE_API_KEY")
    return url, key


def save_perfume_to_supabase(info: dict, image_urls: dict = None,
                              video_url: str = "") -> dict:
    """
    حفظ بيانات العطر في Supabase.

    info: dict — معلومات العطر (brand, product_name, gender, notes_guess, ...)
    image_urls: dict — روابط الصور لكل مقاس (post_1_1, story_9_16, wide_16_9)
    video_url: str — رابط الفيديو

    يعيد dict يحتوي على success وid عند النجاح، أو error عند الفشل.
    """
    url, key = _get_supabase_config()

    if not url or not key:
        return {"success": False, "error": "SUPABASE_URL أو SUPABASE_API_KEY غير محدد في الإعدادات"}

    # تأكد من أن الرابط ينتهي بدون /
    url = url.rstrip("/")

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    images = image_urls or {}
    payload = {
        "brand":         info.get("brand", ""),
        "product_name":  info.get("product_name", ""),
        "gender":        info.get("gender", ""),
        "perfume_type":  info.get("type", ""),
        "notes":         info.get("notes_guess", ""),
        "mood":          info.get("mood", ""),
        "style":         info.get("style", ""),
        "image_post_1_1":    images.get("post_1_1", images.get("instagram_post", "")),
        "image_story_9_16":  images.get("story_9_16", images.get("instagram_story", "")),
        "image_wide_16_9":   images.get("wide_16_9", images.get("twitter", "")),
        "video_url":     video_url,
    }

    try:
        r = requests.post(
            f"{url}/rest/v1/perfumes",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if r.status_code in (200, 201):
            data = r.json()
            record_id = data[0].get("id", "") if isinstance(data, list) and data else ""
            return {"success": True, "id": record_id}
        return {
            "success": False,
            "error": f"خطأ Supabase {r.status_code}: {r.text[:200]}",
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}
