"""
اختبار توليد المحتوى الكامل لمنشور واحد:
- 3 صور بمقاسات مختلفة (Instagram Post 1:1, Story 9:16, Twitter 16:9)
- برومت فيديو عمودي (9:16 - TikTok/Reels)
- برومت فيديو أفقي (16:9 - YouTube)
- النصوص الكاملة (تعليقات + أوصاف + هاشتاقات + سيناريو)
"""
import os
import sys
import json
import time
import re
import requests
from pathlib import Path

sys.path.insert(0, '/home/ubuntu/mahwous_studio_v13')

# محاكاة streamlit
import unittest.mock as mock
st_mock = mock.MagicMock()
st_mock.session_state = {}
st_mock.secrets = mock.MagicMock()
st_mock.secrets.get = mock.MagicMock(return_value="")
st_mock.secrets.__getitem__ = mock.MagicMock(side_effect=KeyError)
sys.modules['streamlit'] = st_mock

from modules.ai_engine import (
    build_manual_info,
    build_mahwous_product_prompt,
    build_product_only_prompt,
    build_video_prompt,
    generate_text_openai_compat,
    clean_json,
    PLATFORMS,
)

OUTPUT_DIR = Path("/home/ubuntu/mahwous_studio_v13/test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("🎬 توليد محتوى كامل — Bvlgari Man Glacial Essence")
print("=" * 70)

# ─── معلومات العطر ──────────────────────────────────────────────────────────
info = build_manual_info(
    product_name="Bvlgari Man Glacial Essence",
    brand="Bvlgari",
    perfume_type="EDP",
    size="100ml",
    gender="masculine",
    style="luxury",
    colors=["silver", "white", "ice blue", "transparent"],
    bottle_shape="rectangular crystal-clear glass bottle with silver metallic cap and frosted ice-blue base gradient",
    mood="fresh icy masculine sophisticated",
    notes="bergamot, violet leaf, vetiver, musk, woods"
)

print(f"\n✅ العطر: {info['product_name']} من {info['brand']}")
print(f"   النوع: {info['type']} | الجنس: {info['gender']} | الطابع: {info['style']}")

# ─── بناء برومتات الصور الثلاث ──────────────────────────────────────────────
print("\n" + "─" * 50)
print("📸 بناء برومتات الصور (3 مقاسات)")
print("─" * 50)

prompts = {
    "post_1_1": {
        "platform": PLATFORMS["post_1_1"],
        "prompt": build_mahwous_product_prompt(info, outfit="suit", scene="store", platform_aspect="1:1"),
        "size": "1080x1080",
        "ratio": "1:1",
    },
    "story_9_16": {
        "platform": PLATFORMS["story_9_16"],
        "prompt": build_mahwous_product_prompt(info, outfit="suit", scene="studio", platform_aspect="9:16"),
        "size": "1080x1920",
        "ratio": "9:16",
    },
    "wide_16_9": {
        "platform": PLATFORMS["wide_16_9"],
        "prompt": build_mahwous_product_prompt(info, outfit="suit", scene="rooftop", platform_aspect="16:9"),
        "size": "1280x720",
        "ratio": "16:9",
    },
}

for key, data in prompts.items():
    plat = data["platform"]
    prompt_file = OUTPUT_DIR / f"prompt_{key}.txt"
    prompt_file.write_text(data["prompt"], encoding="utf-8")
    print(f"  ✅ {plat['label']} ({data['size']}) — {len(data['prompt'])} حرف — محفوظ: prompt_{key}.txt")

# ─── بناء برومتات الفيديو ────────────────────────────────────────────────────
print("\n" + "─" * 50)
print("🎬 بناء برومتات الفيديو (عمودي + أفقي)")
print("─" * 50)

video_prompts = {
    "vertical_9x16": {
        "aspect": "9:16",
        "platform": "TikTok / Instagram Reels",
        "prompt": build_video_prompt(info, scene="store", outfit="suit", duration=7,
                                     camera_move="push_in", scene_type="مهووس مع العطر"),
    },
    "horizontal_16x9": {
        "aspect": "16:9",
        "platform": "YouTube / Twitter",
        "prompt": build_video_prompt(info, scene="rooftop", outfit="suit", duration=10,
                                     camera_move="orbit", scene_type="مهووس مع العطر"),
    },
}

for key, data in video_prompts.items():
    vp_file = OUTPUT_DIR / f"video_prompt_{key}.txt"
    vp_file.write_text(data["prompt"], encoding="utf-8")
    print(f"  ✅ {data['platform']} ({data['aspect']}) — {len(data['prompt'])} حرف — محفوظ: video_prompt_{key}.txt")

# ─── توليد النصوص الكاملة ───────────────────────────────────────────────────
print("\n" + "─" * 50)
print("✍️ توليد النصوص الكاملة (OpenAI)")
print("─" * 50)

SYSTEM_CAPTIONS = """أنت أفضل كاتب محتوى عطور فاخرة في الخليج العربي.
أسلوبك: شعري، عاطفي، فاخر، مع هوك جذاب في كل منصة.
اللغة: عربية خليجية راقية.
الكلمات المفتاحية الإلزامية: "شراء عطور فاخرة"، "أفضل عطور نيش في السعودية"، "عطور أصلية للبيع"، "متجر عطور موثوق".
ممنوع أي نصوص إنجليزية في التعليقات."""

# 1. التعليقات
print("\n  ⏳ توليد التعليقات...")
captions_prompt = f"""العطر: {info['product_name']} من {info['brand']}
النوع: {info['type']} | الجنس: {info['gender']} | الطابع: {info['style']}
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

اكتب Captions احترافية لـ 3 منصات. أجب بـ JSON صرف فقط:
{{
  "instagram_post": {{
    "caption": "نص 120-150 كلمة شعري وجذاب يبدأ بهوك صادم، يذكر الكلمات المفتاحية بشكل طبيعي",
    "hashtags": ["#هاشتاق1", "#هاشتاق2", "#هاشتاق3", "#هاشتاق4", "#هاشتاق5", "#هاشتاق6", "#هاشتاق7", "#هاشتاق8", "#هاشتاق9", "#هاشتاق10", "#هاشتاق11", "#هاشتاق12", "#هاشتاق13", "#هاشتاق14", "#هاشتاق15"]
  }},
  "instagram_story": {{
    "caption": "نص قصير 40-50 كلمة + CTA قوي للشراء",
    "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"]
  }},
  "twitter": {{
    "caption": "نص 200-220 حرف + 2-3 هاشتاقات"
  }}
}}"""

try:
    captions_text = generate_text_openai_compat(captions_prompt, SYSTEM_CAPTIONS, temperature=0.8)
    captions_text = captions_text.strip()
    captions_text = re.sub(r"^```(?:json)?\s*\n?", "", captions_text, flags=re.MULTILINE)
    captions_text = re.sub(r"\n?\s*```\s*$", "", captions_text, flags=re.MULTILINE)
    captions = json.loads(captions_text)
    
    ig_post = captions.get("instagram_post", {})
    ig_story = captions.get("instagram_story", {})
    tw = captions.get("twitter", {})
    
    print(f"  ✅ Instagram Post: {len(ig_post.get('caption', ''))} حرف | {len(ig_post.get('hashtags', []))} هاشتاق")
    print(f"  ✅ Instagram Story: {len(ig_story.get('caption', ''))} حرف | {len(ig_story.get('hashtags', []))} هاشتاق")
    print(f"  ✅ Twitter: {len(tw.get('caption', ''))} حرف")
    
    captions_file = OUTPUT_DIR / "captions.json"
    captions_file.write_text(json.dumps(captions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 محفوظ: captions.json")
except Exception as e:
    print(f"  ❌ خطأ: {e}")
    captions = {}

# 2. الأوصاف التسويقية
print("\n  ⏳ توليد الأوصاف التسويقية...")
desc_prompt = f"""العطر: {info['product_name']} من {info['brand']}
النوع: {info['type']} | {info['gender']} | {info['style']}
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

اكتب 3 أوصاف تسويقية باللغة العربية الراقية. JSON فقط:
{{
  "short": "وصف 60-80 كلمة مكثف للقصص والريلز",
  "medium": "وصف 120-150 كلمة للمنشورات الرئيسية",
  "ad": "إعلان مكثف ومقنع 25-35 كلمة فقط"
}}"""

try:
    desc_text = generate_text_openai_compat(desc_prompt, temperature=0.7)
    desc_text = desc_text.strip()
    desc_text = re.sub(r"^```(?:json)?\s*\n?", "", desc_text, flags=re.MULTILINE)
    desc_text = re.sub(r"\n?\s*```\s*$", "", desc_text, flags=re.MULTILINE)
    descriptions = json.loads(desc_text)
    print(f"  ✅ وصف قصير: {len(descriptions.get('short', ''))} حرف")
    print(f"  ✅ وصف متوسط: {len(descriptions.get('medium', ''))} حرف")
    print(f"  ✅ إعلان: {len(descriptions.get('ad', ''))} حرف")
    desc_file = OUTPUT_DIR / "descriptions.json"
    desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 محفوظ: descriptions.json")
except Exception as e:
    print(f"  ❌ خطأ: {e}")
    descriptions = {}

# 3. الهاشتاقات
print("\n  ⏳ توليد الهاشتاقات...")
hashtags_prompt = f"""العطر: {info['product_name']} | {info['brand']} | {info['gender']} | {info['style']} | {info['mood']}

اختر 30 هاشتاق مثالي. JSON فقط:
{{
  "arabic": ["#هاشتاق_عربي × 15 — مزيج عام ومتخصص"],
  "english": ["#english_hashtag × 10 — mix of high and niche"],
  "buying": ["#شراء_عطور_فاخرة","#عطور_أصلية_للبيع","#متجر_عطور_موثوق","#أفضل_عطور_نيش_في_السعودية","#عطور_نيش"]
}}"""

try:
    hashtags_text = generate_text_openai_compat(hashtags_prompt, temperature=0.6)
    hashtags_text = hashtags_text.strip()
    hashtags_text = re.sub(r"^```(?:json)?\s*\n?", "", hashtags_text, flags=re.MULTILINE)
    hashtags_text = re.sub(r"\n?\s*```\s*$", "", hashtags_text, flags=re.MULTILINE)
    hashtags = json.loads(hashtags_text)
    total = len(hashtags.get('arabic', [])) + len(hashtags.get('english', [])) + len(hashtags.get('buying', []))
    print(f"  ✅ {total} هاشتاق: {len(hashtags.get('arabic', []))} عربي + {len(hashtags.get('english', []))} إنجليزي + {len(hashtags.get('buying', []))} شرائي")
    hashtags_file = OUTPUT_DIR / "hashtags.json"
    hashtags_file.write_text(json.dumps(hashtags, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 محفوظ: hashtags.json")
except Exception as e:
    print(f"  ❌ خطأ: {e}")
    hashtags = {}

# 4. السيناريو
print("\n  ⏳ توليد سيناريو الفيديو...")
SYSTEM_SCENARIO = """أنت كاتب سيناريو إبداعي محترف لتيك توك والريلز. أسلوبك: سينمائي، مثير، يبدأ بهوك صادم في أول 3 ثوانٍ."""

scenario_prompt = f"""اكتب سيناريو فيديو 7 ثوانٍ لعطر "{info['product_name']}" من "{info['brand']}"
نوع المشهد: مهووس مع العطر | المكان: متجر فاخر | الزي: بدلة سوداء
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

أجب بـ JSON صرف فقط:
{{
  "title": "عنوان السيناريو",
  "hook": "الهوك الصادم في أول 3 ثوانٍ",
  "scenes": [
    {{"time": "0-3s", "action": "وصف الحركة بالتفصيل", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}},
    {{"time": "3-5s", "action": "وصف الحركة بالتفصيل", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}},
    {{"time": "5-7s", "action": "وصف الحركة بالتفصيل", "camera": "نوع اللقطة", "audio": "الصوت/الموسيقى"}}
  ],
  "cta": "دعوة للشراء غير مباشرة",
  "video_prompt_vertical": "برومت Luma Dream Machine للفيديو العمودي 9:16 بالإنجليزية (7 ثوانٍ) — مفصل وسينمائي",
  "video_prompt_horizontal": "برومت Luma Dream Machine للفيديو الأفقي 16:9 بالإنجليزية (10 ثوانٍ) — مفصل وسينمائي"
}}"""

try:
    scenario_text = generate_text_openai_compat(scenario_prompt, SYSTEM_SCENARIO, temperature=0.85)
    scenario_text = scenario_text.strip()
    scenario_text = re.sub(r"^```(?:json)?\s*\n?", "", scenario_text, flags=re.MULTILINE)
    scenario_text = re.sub(r"\n?\s*```\s*$", "", scenario_text, flags=re.MULTILINE)
    scenario = json.loads(scenario_text)
    print(f"  ✅ العنوان: {scenario.get('title', '')}")
    print(f"  ✅ الهوك: {scenario.get('hook', '')[:80]}...")
    print(f"  ✅ عدد المشاهد: {len(scenario.get('scenes', []))}")
    scenario_file = OUTPUT_DIR / "scenario.json"
    scenario_file.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 محفوظ: scenario.json")
except Exception as e:
    print(f"  ❌ خطأ: {e}")
    scenario = {}

# ─── إنشاء تقرير HTML شامل ──────────────────────────────────────────────────
print("\n" + "─" * 50)
print("📄 إنشاء تقرير HTML شامل")
print("─" * 50)

ig_caption = captions.get("instagram_post", {}).get("caption", "—") if captions else "—"
ig_hashtags = " ".join(captions.get("instagram_post", {}).get("hashtags", [])) if captions else "—"
story_caption = captions.get("instagram_story", {}).get("caption", "—") if captions else "—"
story_hashtags = " ".join(captions.get("instagram_story", {}).get("hashtags", [])) if captions else "—"
tw_caption = captions.get("twitter", {}).get("caption", "—") if captions else "—"
desc_short = descriptions.get("short", "—") if descriptions else "—"
desc_medium = descriptions.get("medium", "—") if descriptions else "—"
desc_ad = descriptions.get("ad", "—") if descriptions else "—"
scenario_title = scenario.get("title", "—") if scenario else "—"
scenario_hook = scenario.get("hook", "—") if scenario else "—"
scenario_cta = scenario.get("cta", "—") if scenario else "—"
vp_vertical = scenario.get("video_prompt_vertical", video_prompts["vertical_9x16"]["prompt"][:300] + "...") if scenario else video_prompts["vertical_9x16"]["prompt"][:300] + "..."
vp_horizontal = scenario.get("video_prompt_horizontal", video_prompts["horizontal_16x9"]["prompt"][:300] + "...") if scenario else video_prompts["horizontal_16x9"]["prompt"][:300] + "..."

all_hashtags = []
if hashtags:
    all_hashtags = hashtags.get("arabic", []) + hashtags.get("english", []) + hashtags.get("buying", [])

html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تقرير المحتوى — {info['product_name']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background: #0a0a0a; color: #f0e6d0; direction: rtl; }}
  .header {{ background: linear-gradient(135deg, #1a0a00, #2d1500); padding: 40px; text-align: center; border-bottom: 2px solid #c9a227; }}
  .header h1 {{ font-size: 2.5em; color: #c9a227; margin-bottom: 10px; }}
  .header p {{ color: #a0896e; font-size: 1.1em; }}
  .badge {{ display: inline-block; background: #c9a227; color: #0a0a0a; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin: 4px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
  .section {{ background: #1a1008; border: 1px solid #3d2a10; border-radius: 12px; padding: 25px; margin-bottom: 25px; }}
  .section-title {{ font-size: 1.4em; color: #c9a227; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #3d2a10; }}
  .platform-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
  .platform-card {{ background: #120a00; border: 1px solid #4a3520; border-radius: 10px; padding: 20px; }}
  .platform-label {{ font-size: 1.1em; color: #c9a227; margin-bottom: 5px; font-weight: bold; }}
  .platform-size {{ font-size: 0.85em; color: #8a7560; margin-bottom: 15px; }}
  .caption-text {{ line-height: 1.8; color: #e8d5b0; white-space: pre-wrap; font-size: 0.95em; }}
  .hashtags {{ margin-top: 15px; }}
  .hashtag {{ display: inline-block; background: #2d1a00; color: #c9a227; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin: 2px; }}
  .prompt-box {{ background: #0d0800; border: 1px solid #2d1a00; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 0.82em; color: #a0896e; white-space: pre-wrap; line-height: 1.6; max-height: 200px; overflow-y: auto; }}
  .video-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .video-card {{ background: #120a00; border: 1px solid #4a3520; border-radius: 10px; padding: 20px; }}
  .scene {{ background: #0d0800; border-right: 3px solid #c9a227; padding: 12px 15px; margin-bottom: 10px; border-radius: 0 8px 8px 0; }}
  .scene-time {{ color: #c9a227; font-weight: bold; font-size: 0.9em; }}
  .scene-action {{ color: #e8d5b0; margin-top: 5px; font-size: 0.9em; }}
  .scene-camera {{ color: #8a7560; font-size: 0.8em; margin-top: 3px; }}
  .info-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
  .info-item {{ background: #120a00; border: 1px solid #3d2a10; border-radius: 8px; padding: 15px; text-align: center; }}
  .info-label {{ color: #8a7560; font-size: 0.85em; margin-bottom: 5px; }}
  .info-value {{ color: #c9a227; font-weight: bold; }}
  .desc-box {{ background: #0d0800; border-right: 3px solid #c9a227; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px; line-height: 1.8; color: #e8d5b0; }}
  .desc-label {{ color: #c9a227; font-weight: bold; font-size: 0.85em; margin-bottom: 8px; }}
  .footer {{ text-align: center; padding: 30px; color: #5a4a35; border-top: 1px solid #2d1a00; margin-top: 30px; }}
  @media (max-width: 768px) {{
    .platform-grid, .video-grid, .info-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>🎬 استديو مهووس الذكي v13.0</h1>
  <p>تقرير المحتوى الكامل — يوم واحد</p>
  <div style="margin-top: 15px;">
    <span class="badge">📸 3 صور</span>
    <span class="badge">🎬 2 فيديو</span>
    <span class="badge">✍️ نصوص كاملة</span>
    <span class="badge">🔖 هاشتاقات</span>
  </div>
</div>

<div class="container">

  <!-- معلومات العطر -->
  <div class="section">
    <div class="section-title">🌹 معلومات العطر</div>
    <div class="info-grid">
      <div class="info-item"><div class="info-label">اسم العطر</div><div class="info-value">{info['product_name']}</div></div>
      <div class="info-item"><div class="info-label">العلامة التجارية</div><div class="info-value">{info['brand']}</div></div>
      <div class="info-item"><div class="info-label">النوع</div><div class="info-value">{info['type']}</div></div>
      <div class="info-item"><div class="info-label">الجنس</div><div class="info-value">{info['gender']}</div></div>
      <div class="info-item"><div class="info-label">الطابع</div><div class="info-value">{info['style']}</div></div>
      <div class="info-item"><div class="info-label">المزاج</div><div class="info-value">{info['mood']}</div></div>
    </div>
  </div>

  <!-- التعليقات -->
  <div class="section">
    <div class="section-title">✍️ التعليقات (3 منصات)</div>
    <div class="platform-grid">
      <div class="platform-card">
        <div class="platform-label">📸 Instagram Post</div>
        <div class="platform-size">1080×1080 | 1:1</div>
        <div class="caption-text">{ig_caption}</div>
        <div class="hashtags">{"".join(f'<span class="hashtag">{h}</span>' for h in captions.get("instagram_post", {}).get("hashtags", []) if captions)}</div>
      </div>
      <div class="platform-card">
        <div class="platform-label">📱 Instagram Story</div>
        <div class="platform-size">1080×1920 | 9:16</div>
        <div class="caption-text">{story_caption}</div>
        <div class="hashtags">{"".join(f'<span class="hashtag">{h}</span>' for h in captions.get("instagram_story", {}).get("hashtags", []) if captions)}</div>
      </div>
      <div class="platform-card">
        <div class="platform-label">🐦 Twitter/X</div>
        <div class="platform-size">1200×675 | 16:9</div>
        <div class="caption-text">{tw_caption}</div>
      </div>
    </div>
  </div>

  <!-- الأوصاف التسويقية -->
  <div class="section">
    <div class="section-title">📝 الأوصاف التسويقية</div>
    <div class="desc-box"><div class="desc-label">📌 وصف قصير (للقصص والريلز)</div>{desc_short}</div>
    <div class="desc-box"><div class="desc-label">📄 وصف متوسط (للمنشورات)</div>{desc_medium}</div>
    <div class="desc-box"><div class="desc-label">📢 إعلان مكثف</div>{desc_ad}</div>
  </div>

  <!-- برومتات الصور -->
  <div class="section">
    <div class="section-title">🖼️ برومتات الصور (Fal.ai Flux)</div>
    <div class="platform-grid">
      <div class="platform-card">
        <div class="platform-label">📸 Instagram Post (1:1)</div>
        <div class="platform-size">1080×1080 — مهووس مع العطر في المتجر</div>
        <div class="prompt-box">{prompts['instagram_post']['prompt'][:500]}...</div>
      </div>
      <div class="platform-card">
        <div class="platform-label">📱 Instagram Story (9:16)</div>
        <div class="platform-size">1080×1920 — مهووس مع العطر في الاستديو</div>
        <div class="prompt-box">{prompts['instagram_story']['prompt'][:500]}...</div>
      </div>
      <div class="platform-card">
        <div class="platform-label">🐦 Twitter/X (16:9)</div>
        <div class="platform-size">1200×675 — مهووس مع العطر على السطح</div>
        <div class="prompt-box">{prompts['twitter']['prompt'][:500]}...</div>
      </div>
    </div>
  </div>

  <!-- السيناريو -->
  <div class="section">
    <div class="section-title">🎭 سيناريو الفيديو</div>
    <div style="background:#120a00; border-radius:10px; padding:20px; margin-bottom:20px;">
      <div style="color:#c9a227; font-size:1.2em; font-weight:bold; margin-bottom:10px;">🎬 {scenario_title}</div>
      <div style="background:#0d0800; padding:12px; border-radius:8px; color:#e8d5b0; margin-bottom:15px;">
        <strong style="color:#c9a227;">الهوك:</strong> {scenario_hook}
      </div>
      {"".join(f'<div class="scene"><div class="scene-time">⏱ {s.get("time","")}</div><div class="scene-action">🎬 {s.get("action","")}</div><div class="scene-camera">📷 {s.get("camera","")} | 🎵 {s.get("audio","")}</div></div>' for s in scenario.get("scenes", []) if scenario)}
      <div style="background:#0d0800; padding:12px; border-radius:8px; color:#c9a227; margin-top:15px;">
        <strong>CTA:</strong> {scenario_cta}
      </div>
    </div>
  </div>

  <!-- برومتات الفيديو -->
  <div class="section">
    <div class="section-title">🎬 برومتات الفيديو (Luma Dream Machine)</div>
    <div class="video-grid">
      <div class="video-card">
        <div class="platform-label">📱 فيديو عمودي (9:16)</div>
        <div class="platform-size">TikTok / Instagram Reels — 7 ثوانٍ</div>
        <div class="prompt-box">{vp_vertical[:600]}...</div>
      </div>
      <div class="video-card">
        <div class="platform-label">🖥️ فيديو أفقي (16:9)</div>
        <div class="platform-size">YouTube / Twitter — 10 ثوانٍ</div>
        <div class="prompt-box">{vp_horizontal[:600]}...</div>
      </div>
    </div>
  </div>

  <!-- الهاشتاقات -->
  <div class="section">
    <div class="section-title">🔖 الهاشتاقات الكاملة ({len(all_hashtags)} هاشتاق)</div>
    <div>
      {"".join(f'<span class="hashtag">{h}</span>' for h in all_hashtags)}
    </div>
  </div>

</div>

<div class="footer">
  <p>🎬 استديو مهووس الذكي v13.0 | Powered by Gemini + Claude + OpenAI</p>
  <p style="margin-top:8px; font-size:0.85em;">تم التوليد بتاريخ {time.strftime('%Y-%m-%d %H:%M')}</p>
</div>
</body>
</html>"""

report_file = OUTPUT_DIR / "content_report.html"
report_file.write_text(html_content, encoding="utf-8")
print(f"  ✅ تقرير HTML محفوظ: test_output/content_report.html")

# ─── ملخص نهائي ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("📊 ملخص النتائج النهائية")
print("=" * 70)
print(f"✅ برومت Instagram Post (1080×1080 | 1:1): {len(prompts['instagram_post']['prompt'])} حرف")
print(f"✅ برومت Instagram Story (1080×1920 | 9:16): {len(prompts['instagram_story']['prompt'])} حرف")
print(f"✅ برومت Twitter (1200×675 | 16:9): {len(prompts['twitter']['prompt'])} حرف")
print(f"✅ برومت فيديو عمودي (9:16 | TikTok/Reels): {len(video_prompts['vertical_9x16']['prompt'])} حرف")
print(f"✅ برومت فيديو أفقي (16:9 | YouTube): {len(video_prompts['horizontal_16x9']['prompt'])} حرف")
print(f"{'✅' if captions else '❌'} التعليقات (3 منصات): {'نجح' if captions else 'فشل'}")
print(f"{'✅' if descriptions else '❌'} الأوصاف التسويقية: {'نجح' if descriptions else 'فشل'}")
print(f"{'✅' if hashtags else '❌'} الهاشتاقات ({len(all_hashtags)} هاشتاق): {'نجح' if hashtags else 'فشل'}")
print(f"{'✅' if scenario else '❌'} السيناريو: {'نجح' if scenario else 'فشل'}")
print(f"\n📁 الملفات المولّدة في: test_output/")
for f in sorted(OUTPUT_DIR.iterdir()):
    size = f.stat().st_size
    print(f"   - {f.name} ({size:,} bytes)")
print("\n✅ اكتمل توليد المحتوى بنجاح!")
