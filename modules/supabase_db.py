"""
🗄️ Supabase Database Module — Mahwous AI Studio v13.1
حفظ واسترجاع بيانات العطور من Supabase
"""

import requests
import json
import time


def _get_supabase_config():
    """جلب إعدادات Supabase"""
    import streamlit as st
    try:
        url = st.session_state.get("supabase_url") or st.secrets.get("SUPABASE_URL", "")
        key = st.session_state.get("supabase_key") or st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        url = st.session_state.get("supabase_url", "")
        key = st.session_state.get("supabase_key", "")
    return url, key


def save_perfume_to_supabase(info: dict, images: dict, video_url: str = "") -> dict:
    """حفظ بيانات العطر والصور في Supabase"""
    supabase_url, supabase_key = _get_supabase_config()
    if not supabase_url or not supabase_key:
        return {"success": False, "error": "SUPABASE_URL أو SUPABASE_KEY مفقود"}

    payload = {
        "brand":        info.get("brand", ""),
        "product_name": info.get("product_name", ""),
        "type":         info.get("type", ""),
        "gender":       info.get("gender", ""),
        "style":        info.get("style", ""),
        "mood":         info.get("mood", ""),
        "notes":        info.get("notes_guess", ""),
        "images":       json.dumps({k: v.get("url", "") for k, v in images.items() if v.get("url")}),
        "video_url":    video_url,
        "created_at":   time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    try:
        resp = requests.post(
            f"{supabase_url}/rest/v1/perfume_history",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload,
            timeout=15
        )
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_perfume_history(limit: int = 15) -> list:
    """استرجاع سجل العطور المحفوظة"""
    supabase_url, supabase_key = _get_supabase_config()
    if not supabase_url or not supabase_key:
        return []

    try:
        resp = requests.get(
            f"{supabase_url}/rest/v1/perfume_history?select=*&order=created_at.desc&limit={limit}",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            },
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []
