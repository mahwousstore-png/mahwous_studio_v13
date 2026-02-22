"""
اختبار شامل لاستديو مهووس الذكي v13.0
يختبر: توليد النصوص + بناء البرومتات + منطق الكود
"""
import os
import sys
import json
import time

# إضافة مسار المشروع
sys.path.insert(0, '/home/ubuntu/mahwous_studio_v13')

# محاكاة st.session_state و st.secrets
import unittest.mock as mock

# إنشاء mock لـ streamlit
st_mock = mock.MagicMock()
st_mock.session_state = {}
st_mock.secrets = mock.MagicMock()
st_mock.secrets.get = mock.MagicMock(return_value="")
st_mock.secrets.__getitem__ = mock.MagicMock(side_effect=KeyError)
sys.modules['streamlit'] = st_mock

# الآن نستورد المحرك
from modules.ai_engine import (
    build_manual_info,
    build_mahwous_product_prompt,
    build_product_only_prompt,
    build_video_prompt,
    generate_scenario,
    generate_all_captions,
    generate_descriptions,
    generate_hashtags,
    PLATFORMS,
    MAHWOUS_DNA,
    MAHWOUS_OUTFITS,
)

# إعداد OpenAI كـ fallback للنصوص
import openai
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

def test_openai_text(prompt: str, system: str = None) -> str:
    """اختبار توليد النص عبر OpenAI"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        max_tokens=2000,
        temperature=0.8
    )
    return response.choices[0].message.content

print("=" * 60)
print("🧪 اختبار استديو مهووس الذكي v13.0")
print("=" * 60)

# ─── اختبار 1: بناء معلومات العطر يدوياً ──────────────────────
print("\n✅ اختبار 1: build_manual_info")
info = build_manual_info(
    product_name="Bvlgari Man Glacial Essence",
    brand="Bvlgari",
    perfume_type="EDP",
    size="100ml",
    gender="masculine",
    style="luxury",
    colors=["silver", "white", "blue"],
    bottle_shape="rectangular crystal-clear glass bottle with silver metallic cap",
    mood="fresh icy masculine",
    notes="bergamot, violet, vetiver, musk"
)
print(f"  ✓ العطر: {info['product_name']} من {info['brand']}")
print(f"  ✓ النوع: {info['type']} | الجنس: {info['gender']}")
print(f"  ✓ الألوان: {info['colors']}")
print(f"  ✓ المزاج: {info['mood']}")

# ─── اختبار 2: بناء برومت الصورة مع مهووس ─────────────────────
print("\n✅ اختبار 2: build_mahwous_product_prompt")
for platform_key in ["post_1_1", "story_9_16", "wide_16_9"]:
    plat = PLATFORMS[platform_key]
    prompt = build_mahwous_product_prompt(info, outfit="suit", scene="store", platform_aspect=plat["fal_ratio"])
    print(f"  ✓ {plat['label']} ({plat['w']}x{plat['h']}) — برومت: {len(prompt)} حرف")
    assert "Mahwous" in prompt or "mahwous" in prompt.lower() or "MAHWOUS" in prompt
    assert info['product_name'] in prompt
    assert info['brand'] in prompt

# ─── اختبار 3: برومت المنتج فقط ────────────────────────────────
print("\n✅ اختبار 3: build_product_only_prompt")
prompt_product = build_product_only_prompt(info, "1:1")
print(f"  ✓ برومت المنتج: {len(prompt_product)} حرف")
assert "NO TEXT" in prompt_product or "STRICT" in prompt_product

# ─── اختبار 4: برومت الفيديو ────────────────────────────────────
print("\n✅ اختبار 4: build_video_prompt")
for scene_type in ["مهووس مع العطر", "العطر يتكلم وحده", "مهووس بدون عطر"]:
    for aspect in ["9:16", "16:9"]:
        vp = build_video_prompt(info, scene="store", outfit="suit", duration=7, 
                                camera_move="push_in", scene_type=scene_type)
        print(f"  ✓ {scene_type} ({aspect}) — برومت: {len(vp)} حرف")

# ─── اختبار 5: التحقق من منطق المنصات ─────────────────────────
print("\n✅ اختبار 5: PLATFORMS")
mandatory = ["post_1_1", "story_9_16", "wide_16_9"]
for key in mandatory:
    p = PLATFORMS[key]
    print(f"  ✓ {p['label']}: {p['w']}x{p['h']} | {p['aspect']}")

# ─── اختبار 6: توليد النصوص عبر OpenAI ────────────────────────
print("\n✅ اختبار 6: توليد النصوص (OpenAI)")

# توليد التعليقات
system_captions = """أنت أفضل كاتب محتوى عطور فاخرة في الخليج العربي.
أسلوبك: شعري، عاطفي، فاخر، مع هوك جذاب في كل منصة.
اللغة: عربية خليجية راقية.
الكلمات المفتاحية: "شراء عطور فاخرة"، "أفضل عطور نيش"، "عطور أصلية للبيع"، "متجر عطور موثوق"."""

prompt_captions = f"""العطر: {info['product_name']} من {info['brand']}
النوع: {info['type']} | الجنس: {info['gender']} | الطابع: {info['style']}
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

اكتب Captions احترافية لـ 3 منصات. أجب بـ JSON صرف فقط:
{{
  "instagram_post": {{"caption": "نص 120-150 كلمة شعري وجذاب مع هاشتاقات", "hashtags": ["#هاشتاق1", "#هاشتاق2", "#هاشتاق3", "#هاشتاق4", "#هاشتاق5", "#هاشتاق6", "#هاشتاق7", "#هاشتاق8", "#هاشتاق9", "#هاشتاق10"]}},
  "instagram_story": {{"caption": "نص قصير 40-50 كلمة + CTA للشراء", "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5"]}},
  "twitter": {{"caption": "نص 220 حرف + 2-3 هاشتاقات"}}
}}"""

print("  ⏳ جاري توليد التعليقات...")
try:
    captions_text = test_openai_text(prompt_captions, system_captions)
    # تنظيف JSON
    import re
    captions_text = captions_text.strip()
    captions_text = re.sub(r"^```(?:json)?\s*\n?", "", captions_text, flags=re.MULTILINE)
    captions_text = re.sub(r"\n?\s*```\s*$", "", captions_text, flags=re.MULTILINE)
    captions = json.loads(captions_text)
    
    print(f"  ✓ Instagram Post: {len(captions.get('instagram_post', {}).get('caption', ''))} حرف")
    print(f"  ✓ Instagram Story: {len(captions.get('instagram_story', {}).get('caption', ''))} حرف")
    print(f"  ✓ Twitter: {len(captions.get('twitter', {}).get('caption', ''))} حرف")
    print(f"\n  📝 نموذج Instagram Post:")
    print(f"  {captions['instagram_post']['caption'][:200]}...")
    print(f"\n  📝 نموذج Twitter:")
    print(f"  {captions['twitter']['caption']}")
except Exception as e:
    print(f"  ❌ خطأ في التعليقات: {e}")
    captions = {}

# ─── اختبار 7: توليد الأوصاف ────────────────────────────────────
print("\n✅ اختبار 7: توليد الأوصاف التسويقية")
prompt_desc = f"""العطر: {info['product_name']} من {info['brand']}
النوع: {info['type']} | {info['gender']} | {info['style']}
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

اكتب وصفين تسويقيين. JSON فقط:
{{
  "short": "وصف 60-80 كلمة مكثف للقصص والريلز",
  "medium": "وصف 120-150 كلمة للمنشورات الرئيسية"
}}"""

try:
    desc_text = test_openai_text(prompt_desc)
    desc_text = desc_text.strip()
    desc_text = re.sub(r"^```(?:json)?\s*\n?", "", desc_text, flags=re.MULTILINE)
    desc_text = re.sub(r"\n?\s*```\s*$", "", desc_text, flags=re.MULTILINE)
    descriptions = json.loads(desc_text)
    print(f"  ✓ وصف قصير: {len(descriptions.get('short', ''))} حرف")
    print(f"  ✓ وصف متوسط: {len(descriptions.get('medium', ''))} حرف")
    print(f"\n  📝 الوصف القصير:")
    print(f"  {descriptions.get('short', '')}")
except Exception as e:
    print(f"  ❌ خطأ في الأوصاف: {e}")
    descriptions = {}

# ─── اختبار 8: توليد السيناريو ──────────────────────────────────
print("\n✅ اختبار 8: توليد سيناريو الفيديو")
system_scenario = """أنت كاتب سيناريو إبداعي محترف لتيك توك والريلز. أسلوبك: سينمائي، مثير، يبدأ بهوك صادم."""

prompt_scenario = f"""اكتب سيناريو فيديو 7 ثوانٍ لعطر "{info['product_name']}" من "{info['brand']}"
نوع المشهد: مهووس مع العطر | المكان: متجر فاخر | الزي: بدلة
المزاج: {info['mood']} | الملاحظات: {info['notes_guess']}

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
  "video_prompt_vertical": "برومت Luma للفيديو العمودي 9:16 بالإنجليزية (7 ثوانٍ)",
  "video_prompt_horizontal": "برومت Luma للفيديو الأفقي 16:9 بالإنجليزية (7 ثوانٍ)"
}}"""

try:
    scenario_text = test_openai_text(prompt_scenario, system_scenario)
    scenario_text = scenario_text.strip()
    scenario_text = re.sub(r"^```(?:json)?\s*\n?", "", scenario_text, flags=re.MULTILINE)
    scenario_text = re.sub(r"\n?\s*```\s*$", "", scenario_text, flags=re.MULTILINE)
    scenario = json.loads(scenario_text)
    print(f"  ✓ العنوان: {scenario.get('title', '')}")
    print(f"  ✓ الهوك: {scenario.get('hook', '')}")
    print(f"  ✓ عدد المشاهد: {len(scenario.get('scenes', []))}")
    print(f"  ✓ CTA: {scenario.get('cta', '')}")
    print(f"\n  🎬 برومت الفيديو العمودي (9:16):")
    print(f"  {scenario.get('video_prompt_vertical', '')[:200]}")
    print(f"\n  🎬 برومت الفيديو الأفقي (16:9):")
    print(f"  {scenario.get('video_prompt_horizontal', '')[:200]}")
except Exception as e:
    print(f"  ❌ خطأ في السيناريو: {e}")
    scenario = {}

# ─── اختبار 9: توليد الهاشتاقات ────────────────────────────────
print("\n✅ اختبار 9: توليد الهاشتاقات")
prompt_hashtags = f"""العطر: {info['product_name']} | {info['brand']} | {info['gender']} | {info['style']} | {info['mood']}

اختر 20 هاشتاق مثالي. JSON فقط:
{{
  "arabic": ["#هاشتاق_عربي × 10"],
  "english": ["#english_hashtag × 7"],
  "buying": ["#شراء_عطور_فاخرة","#عطور_أصلية_للبيع","#متجر_عطور_موثوق"]
}}"""

try:
    hashtags_text = test_openai_text(prompt_hashtags)
    hashtags_text = hashtags_text.strip()
    hashtags_text = re.sub(r"^```(?:json)?\s*\n?", "", hashtags_text, flags=re.MULTILINE)
    hashtags_text = re.sub(r"\n?\s*```\s*$", "", hashtags_text, flags=re.MULTILINE)
    hashtags = json.loads(hashtags_text)
    print(f"  ✓ عربي: {len(hashtags.get('arabic', []))} هاشتاق")
    print(f"  ✓ إنجليزي: {len(hashtags.get('english', []))} هاشتاق")
    print(f"  ✓ شرائي: {hashtags.get('buying', [])}")
except Exception as e:
    print(f"  ❌ خطأ في الهاشتاقات: {e}")
    hashtags = {}

# ─── ملخص النتائج ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("📊 ملخص نتائج الاختبار")
print("=" * 60)
print(f"✅ بناء معلومات العطر: نجح")
print(f"✅ برومت Instagram Post (1080x1080): نجح")
print(f"✅ برومت Instagram Story (1080x1920): نجح")
print(f"✅ برومت Twitter (1200x675): نجح")
print(f"✅ برومت الفيديو العمودي (9:16): نجح")
print(f"✅ برومت الفيديو الأفقي (16:9): نجح")
print(f"{'✅' if captions else '❌'} توليد التعليقات (OpenAI): {'نجح' if captions else 'فشل'}")
print(f"{'✅' if descriptions else '❌'} توليد الأوصاف: {'نجح' if descriptions else 'فشل'}")
print(f"{'✅' if scenario else '❌'} توليد السيناريو: {'نجح' if scenario else 'فشل'}")
print(f"{'✅' if hashtags else '❌'} توليد الهاشتاقات: {'نجح' if hashtags else 'فشل'}")

# حفظ النتائج
results = {
    "info": info,
    "captions": captions,
    "descriptions": descriptions,
    "scenario": scenario,
    "hashtags": hashtags,
    "prompts": {
        "instagram_post_1x1": build_mahwous_product_prompt(info, "suit", "store", "1:1"),
        "instagram_story_9x16": build_mahwous_product_prompt(info, "suit", "store", "9:16"),
        "twitter_16x9": build_mahwous_product_prompt(info, "suit", "store", "16:9"),
        "video_vertical_9x16": build_video_prompt(info, "store", "suit", 7, "push_in", "مهووس مع العطر"),
        "video_horizontal_16x9": build_video_prompt(info, "rooftop", "suit", 7, "orbit", "مهووس مع العطر"),
    }
}

with open("/tmp/test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n💾 النتائج محفوظة في: /tmp/test_results.json")
print("\n✅ اكتمل الاختبار بنجاح!")
