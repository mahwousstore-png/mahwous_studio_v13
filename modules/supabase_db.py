"""
🔗 Supabase Integration - Mahwous AI Studio v13.0
تخزين بيانات العطور والمحتوى المولد في قاعدة بيانات Supabase
"""
import requests
import streamlit as st
from datetime import datetime

def _get_supabase_config():
    def _s(session_key, secret_key, default=""):
        val = st.session_state.get(session_key, "")
        if val: return val
        try: return st.secrets.get(secret_key, default)
        except Exception: return default
    return {
        "url": _s("supabase_url", "SUPABASE_URL"),
        "key": _s("supabase_key", "SUPABASE_KEY"),
    }

def save_perfume_to_supabase(info: dict, images: dict = None, video_url: str = None):
    config = _get_supabase_config()
    if not config["url"] or not config["key"]:
        return {"success": False, "error": "إعدادات Supabase غير مكتملة"}
    headers = {
        "apikey": config["key"],
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "created_at": datetime.now().isoformat(),
        "brand": info.get("brand"),
        "product_name": info.get("product_name"),
        "type": info.get("type"),
        "gender": info.get("gender"),
        "style": info.get("style"),
        "mood": info.get("mood"),
        "notes": info.get("notes_guess"),
        "image_1x1": (images.get("post_1_1") or {}).get("url") if images else None,
        "image_9x16": (images.get("story_9_16") or {}).get("url") if images else None,
        "image_16x9": (images.get("wide_16_9") or {}).get("url") if images else None,
        "video_url": video_url,
        "source": "Mahwous AI Studio v13"
    }
    try:
        r = requests.post(f"{config['url']}/rest/v1/perfumes", headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
