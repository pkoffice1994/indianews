import feedparser
import requests
import json
import os
import re
from html.parser import HTMLParser

# ══════════════════════════════════════════════════════
#  API CONFIGURATION
# ══════════════════════════════════════════════════════

GEMINI_MODEL   = "gemini-2.0-flash"
GEMINI_URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

GROQ_MODEL     = "llama-3.3-70b-versatile"
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"

CLAUDE_MODEL   = "claude-sonnet-4-20250514"
CLAUDE_URL     = "https://api.anthropic.com/v1/messages"

PLACEHOLDER_KEYS = {
    "",
    "your_gemini_api_key_here",
    "your_claude_api_key_here",
    "your_anthropic_api_key_here",
    "your_api_key_here",
    "your-key-here",
}


def _get_gemini_api_key():
    return (os.environ.get("GEMINI_API_KEY") or "").strip()


def _get_claude_api_key():
    return (os.environ.get("ANTHROPIC_API_KEY") or "").strip()


def _get_groq_api_key():
    return (os.environ.get("GROQ_API_KEY") or "").strip()


def _get_ai_engine():
    return (os.environ.get("AI_ENGINE") or "gemini").strip().lower()


def _is_real_key(value):
    if not value:
        return False
    cleaned = value.strip().strip("'\"")
    low = cleaned.lower()
    if low in PLACEHOLDER_KEYS:
        return False
    if low.startswith("your_") and low.endswith("_here"):
        return False
    return True

# ══════════════════════════════════════════════════════
#  RSS FEEDS — Google News + Indian Sources
#  (Hindi aur English dono, Aaj Tak / Dainik Bhaskar / TOI added)
# ══════════════════════════════════════════════════════

RSS_FEEDS = {
    # ── English ──────────────────────────────────────
    "India":        "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "World":        "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",
    "Technology":   "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
    "Business":     "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
    "Sports":       "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNR1p1ZEdvU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
    "Politics":     "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en",

    # ── Times of India ───────────────────────────────
    "TOI-India":    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "TOI-World":    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "TOI-Business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
    "TOI-Sports":   "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    "TOI-Tech":     "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",

    # ── Hindustan Times ──────────────────────────────
    "HT-India":     "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "HT-World":     "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
    "HT-Sports":    "https://www.hindustantimes.com/feeds/rss/sports/rssfeed.xml",
    "HT-Tech":      "https://www.hindustantimes.com/feeds/rss/tech/rssfeed.xml",
    "HT-Business":  "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml",

    # ── NDTV ─────────────────────────────────────────
    "NDTV-India":   "https://feeds.feedburner.com/ndtvnews-india-news",
    "NDTV-World":   "https://feeds.feedburner.com/ndtvnews-world-news",
    "NDTV-Sports":  "https://feeds.feedburner.com/ndtvnews-sports",
    "NDTV-Tech":    "https://feeds.feedburner.com/ndtvnews-tech-mediatech",
    "NDTV-Biz":     "https://feeds.feedburner.com/ndtvprofit-latest",

    # ── Hindi Sources ─────────────────────────────────
    "Hindi-India":   "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi",
    "Hindi-Sports":  "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNR1p1ZEdvU0FtaHBIZ0pKVGlnQVAB?hl=hi&gl=IN&ceid=IN:hi",
    "Hindi-Biz":     "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtaHBIZ0pKVGlnQVAB?hl=hi&gl=IN&ceid=IN:hi",

    # ── Aaj Tak (Hindi) ──────────────────────────────
    "AajTak-India":  "https://feeds.feedburner.com/ndtvkhabar",
    "AajTak-Sports": "https://feeds.feedburner.com/ndtvsports-hindi",
    "AajTak-World":  "https://feeds.feedburner.com/ndtvkhabar",
    "AajTak-Biz":    "https://feeds.feedburner.com/ndtvkhabar",
    "Bhaskar-India": "https://www.bhaskar.com/rss-feed/1061/",
    "Bhaskar-Sports":"https://www.bhaskar.com/rss-feed/1222/",
    "Bhaskar-Biz":   "https://www.bhaskar.com/rss-feed/1220/",
    "Bhaskar-Tech":  "https://www.bhaskar.com/rss-feed/1220/",
    "NBT-India":     "https://navbharattimes.indiatimes.com/rssfeedsdefault.cms",
    "NBT-Sports":    "https://navbharattimes.indiatimes.com/rssfeedsdefault.cms",
    "NBT-Biz":       "https://navbharattimes.indiatimes.com/rssfeedsdefault.cms",
    "Jagran-India":  "https://www.jagran.com/rss/news-national.xml",
    "Jagran-Sports": "https://www.jagran.com/rss/news-sports.xml",
    "Jagran-World":  "https://www.jagran.com/rss/news-world.xml",

    # ── Dainik Bhaskar (Hindi) ───────────────────────
    "Bhaskar-India":  "https://www.bhaskar.com/rss-feed/1061/",
    "Bhaskar-Sports": "https://www.bhaskar.com/rss-feed/1112/",
    "Bhaskar-Biz":    "https://www.bhaskar.com/rss-feed/1069/",
    "Bhaskar-Tech":   "https://www.bhaskar.com/rss-feed/1093/",

    # ── Navbharat Times (Hindi) ──────────────────────
    "NBT-India":      "https://navbharattimes.indiatimes.com/rssfeeds/2564707.cms",
    "NBT-Sports":     "https://navbharattimes.indiatimes.com/rssfeeds/4100745.cms",
    "NBT-Biz":        "https://navbharattimes.indiatimes.com/rssfeeds/7771980.cms",

    # ── Jagran (Hindi) ──────────────────────────────
    "Jagran-India":   "https://www.jagran.com/rss/news/national.xml",
    "Jagran-Sports":  "https://www.jagran.com/rss/news/sports.xml",
    "Jagran-World":   "https://www.jagran.com/rss/news/world.xml",
}

# ── Source name → is it Hindi language? ─────────────
HINDI_SOURCES = {
    "Hindi-India", "Hindi-Sports", "Hindi-Biz",
    "AajTak-India", "AajTak-Sports", "AajTak-World", "AajTak-Biz",
    "Bhaskar-India", "Bhaskar-Sports", "Bhaskar-Biz", "Bhaskar-Tech",
    "NBT-India", "NBT-Sports", "NBT-Biz",
    "Jagran-India", "Jagran-Sports", "Jagran-World",
}

# ── Source → display category (DB mein save hogi) ───
SOURCE_TO_CATEGORY = {
    "India": "India", "World": "World", "Technology": "Technology",
    "Business": "Business", "Sports": "Sports", "Politics": "Politics",
    # Google Hindi feeds → Hindi-* prefix so portal identifies them as Hindi
    "Hindi-India": "Hindi-India", "Hindi-Sports": "Hindi-Sports", "Hindi-Biz": "Hindi-Business",
    # English feeds → plain category
    "TOI-India": "India", "TOI-World": "World", "TOI-Business": "Business",
    "TOI-Sports": "Sports", "TOI-Tech": "Technology",
    "HT-India": "India", "HT-World": "World", "HT-Sports": "Sports",
    "HT-Tech": "Technology", "HT-Business": "Business",
    "NDTV-India": "India", "NDTV-World": "World", "NDTV-Sports": "Sports",
    "NDTV-Tech": "Technology", "NDTV-Biz": "Business",
    # Hindi feeds → Hindi-* prefix
    "AajTak-India": "Hindi-India", "AajTak-Sports": "Hindi-Sports",
    "AajTak-World": "Hindi-World", "AajTak-Biz": "Hindi-Business",
    "Bhaskar-India": "Hindi-India", "Bhaskar-Sports": "Hindi-Sports",
    "Bhaskar-Biz": "Hindi-Business", "Bhaskar-Tech": "Hindi-Technology",
    "NBT-India": "Hindi-India", "NBT-Sports": "Hindi-Sports", "NBT-Biz": "Hindi-Business",
    "Jagran-India": "Hindi-India", "Jagran-Sports": "Hindi-Sports", "Jagran-World": "Hindi-World",
}

# Fallback images agar article image na mile
CATEGORY_IMAGES = {
    "India":      "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80",
    "World":      "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
    "Technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
    "Business":   "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "Sports":     "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80",
    "Politics":   "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
    "General":    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
}


# ══════════════════════════════════════════════════════
#  IMAGE SCRAPER — RSS entry se ya article page se
# ══════════════════════════════════════════════════════

class _MetaImageParser(HTMLParser):
    """Fast HTML parser — sirf og:image / twitter:image dhundta hai"""
    def __init__(self):
        super().__init__()
        self.image = ""

    def handle_starttag(self, tag, attrs):
        if self.image:
            return
        if tag == "meta":
            d = dict(attrs)
            prop = d.get("property", "") or d.get("name", "")
            if prop in ("og:image", "twitter:image") and d.get("content"):
                self.image = d["content"].strip()


def _extract_image_from_entry(entry):
    """
    Step 1: RSS entry ke andar hi image dhundne ki koshish karo.
    feedparser ke media_thumbnail, enclosure, ya summary tag mein image hoti hai.
    """
    # media:thumbnail
    thumbs = entry.get("media_thumbnail") or []
    if thumbs and thumbs[0].get("url"):
        return thumbs[0]["url"]

    # media:content
    for mc in (entry.get("media_content") or []):
        if mc.get("url") and mc.get("medium") == "image":
            return mc["url"]
        if mc.get("url") and "image" in mc.get("type", ""):
            return mc["url"]

    # enclosures
    for enc in (entry.get("enclosures") or []):
        if "image" in enc.get("type", ""):
            return enc.get("href", "") or enc.get("url", "")

    # summary / content mein <img src="..."> dhundho
    for field in ["summary", "content"]:
        text = ""
        val = entry.get(field)
        if isinstance(val, list):
            text = val[0].get("value", "") if val else ""
        elif isinstance(val, str):
            text = val
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.IGNORECASE)
        if m:
            url = m.group(1)
            if url.startswith("http") and not url.endswith(".gif"):
                return url

    return ""


def _fetch_og_image(article_url, timeout=6):
    """
    Step 2: RSS mein image nahi mili to article page ka og:image scrape karo.
    Sirf <head> tak padhta hai — fast hai.
    """
    if not article_url or not article_url.startswith("http"):
        return ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)",
            "Accept": "text/html",
        }
        r = requests.get(article_url, headers=headers, timeout=timeout, stream=True)
        if r.status_code != 200:
            return ""
        # Sirf pehle 15KB padhte hain — <head> itne mein aa jaati hai
        chunk = b""
        for part in r.iter_content(chunk_size=4096):
            chunk += part
            if len(chunk) >= 15360 or b"</head>" in chunk:
                break
        html = chunk.decode("utf-8", errors="ignore")
        parser = _MetaImageParser()
        parser.feed(html)
        img = parser.image
        # Relative URL fix
        if img and img.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(article_url)
            img = f"{parsed.scheme}://{parsed.netloc}{img}"
        return img if img.startswith("http") else ""
    except Exception as e:
        print(f"  og:image fetch failed for {article_url[:60]}: {e}")
        return ""


def get_category_image(category="General"):
    """Get a fallback image for a category without an RSS entry"""
    cat = (category or "General").lower()
    images = {
        "sports":      "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800",
        "business":    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
        "technology":  "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "world":       "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
        "politics":    "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800",
        "health":      "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800",
        "science":     "https://images.unsplash.com/photo-1532094349884-543559059dde?w=800",
        "entertainment":"https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800",
    }
    for key, url in images.items():
        if key in cat:
            return url
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"  # default news


def get_article_image(entry, category="General"):
    """
    Main image resolver:
    1. RSS entry se try karo
    2. Article URL ka og:image scrape karo
    3. Category fallback image use karo
    """
    # Step 1: RSS entry
    img = _extract_image_from_entry(entry)
    if img:
        return img

    # Step 2: og:image from article page
    article_url = entry.get("link", "")
    if article_url:
        img = _fetch_og_image(article_url)
        if img:
            return img

    # Step 3: Fallback
    return CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["General"])


# ══════════════════════════════════════════════════════
#  CHANNEL MENTION SANITIZER
# ══════════════════════════════════════════════════════

# Known news channel names to strip from titles and summaries
_CHANNEL_NAMES = [
    # English channels
    "NDTV", "Times of India", "TOI", "Hindustan Times", "HT", "The Hindu",
    "India Today", "Republic", "Republic Bharat", "Republic World",
    "Zee News", "Zee Business", "Aaj Tak", "ABP News", "ABP Live",
    "News18", "CNN News18", "CNBC TV18", "TV9", "TV9 Bharatvarsh",
    "Economic Times", "ET", "Business Standard", "Financial Express",
    "Mint", "LiveMint", "Indian Express", "Indian Express News",
    "Deccan Herald", "Tribune", "Scroll", "Wire", "The Wire",
    "News Nation", "NewsX", "WION", "Al Jazeera", "BBC", "Reuters",
    "PTI", "ANI", "Moneycontrol", "Firstpost", "Outlook", "India.com",
    "Oneindia", "One India", "Jagran English", "Navbharat Times English",
    "Google News", "MSN News", "Yahoo News",
    # Hindi channels
    "आज तक", "अमर उजाला", "दैनिक भास्कर", "नवभारत टाइम्स",
    "एनडीटीवी", "एबीपी न्यूज़", "ज़ी न्यूज़", "इंडिया टुडे हिंदी",
    "जागरण", "दैनिक जागरण", "लाइव हिंदुस्तान", "हिंदुस्तान",
    "पत्रिका", "राजस्थान पत्रिका", "नई दुनिया", "भास्कर",
    "प्रभात खबर", "न्यूज़18 हिंदी", "टीवी9 भारतवर्ष",
]

# Build a combined regex: match channel name anywhere in text (word boundary)
_CHANNEL_PATTERN = re.compile(
    r"(?:^|\s*[\|\-—–]\s*)(?:" +
    "|".join(re.escape(c) for c in _CHANNEL_NAMES) +
    r")(?:\s*[\|\-—–]\s*|\s*$)",
    re.IGNORECASE
)
# Also strip trailing " - Anything" after last pipe or dash  
_TRAILING_SOURCE = re.compile(
    r"\s*[\|\-—–]\s*[A-Za-z\u0900-\u097F][^\|\-—–]{2,50}$"
)

def _sanitize_channel_mentions(text, source=""):
    """Aggressively remove all news channel names from title and summary text."""
    if not text:
        return text
    text = text.strip()
    # Remove any known channel name pattern
    text = _CHANNEL_PATTERN.sub(" ", text).strip(" |–—-").strip()
    # Remove trailing source pattern like " - Source Name" or "| Source Name"
    text = _TRAILING_SOURCE.sub("", text).strip()
    # Also remove the specific source passed in
    if source:
        text = re.sub(re.escape(source), "", text, flags=re.IGNORECASE).strip(" |–—-").strip()
    # Clean up double spaces
    text = re.sub(r"  +", " ", text).strip()
    return text


# ══════════════════════════════════════════════════════
#  AI CONFIG CHECK
# ══════════════════════════════════════════════════════

def has_ai_configured():
    return (
        _is_real_key(_get_gemini_api_key()) or
        _is_real_key(_get_claude_api_key()) or
        _is_real_key(_get_groq_api_key())
    )


# ══════════════════════════════════════════════════════
#  GROQ API CALL
# ══════════════════════════════════════════════════════

def call_groq(prompt, max_tokens=1000):
    key = _get_groq_api_key()
    if not _is_real_key(key):
        return ""
    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"  [GROQ] Error {resp.status_code}: {resp.text[:100]}")
            return ""
    except Exception as ex:
        print(f"  [GROQ] Exception: {ex}")
        return ""


# ══════════════════════════════════════════════════════
#  GEMINI API CALL
# ══════════════════════════════════════════════════════

def call_gemini(prompt, max_tokens=1000):
    key = _get_gemini_api_key()
    if not _is_real_key(key):
        return ""
    try:
        res = requests.post(
            f"{GEMINI_URL}?key={key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}
            },
            timeout=30
        )
        data = res.json()
        if "error" in data:
            print(f"Gemini API error: {data['error'].get('message', data['error'])}")
            return ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
    except Exception as e:
        print(f"Gemini call failed: {e}")
    return ""


# ══════════════════════════════════════════════════════
#  CLAUDE API CALL
# ══════════════════════════════════════════════════════

def call_claude(prompt, max_tokens=1000):
    key = _get_claude_api_key()
    if not _is_real_key(key):
        return ""
    try:
        res = requests.post(
            CLAUDE_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = res.json()
        if "error" in data:
            print(f"Claude API error: {data['error'].get('message', data['error'])}")
            return ""
        if data.get("content"):
            return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"Claude API call failed: {e}")
    return ""


# ══════════════════════════════════════════════════════
#  UNIFIED AI CALL
# ══════════════════════════════════════════════════════

def call_ai(prompt, max_tokens=1000):
    engine = _get_ai_engine()
    if not has_ai_configured():
        return ""

    if engine == "groq":
        result = call_groq(prompt, max_tokens)
        if not result:
            print("  Groq failed, trying Gemini fallback...")
            result = call_gemini(prompt, max_tokens)
        if not result:
            print("  Gemini failed, trying Claude fallback...")
            result = call_claude(prompt, max_tokens)
    elif engine == "gemini":
        result = call_gemini(prompt, max_tokens)
        if not result:
            print("  Gemini failed, trying Groq fallback...")
            result = call_groq(prompt, max_tokens)
        if not result:
            print("  Groq failed, trying Claude fallback...")
            result = call_claude(prompt, max_tokens)
    else:
        result = call_claude(prompt, max_tokens)
        if not result:
            print("  Claude failed, trying Groq fallback...")
            result = call_groq(prompt, max_tokens)
        if not result:
            print("  Groq failed, trying Gemini fallback...")
            result = call_gemini(prompt, max_tokens)
    return result


# ══════════════════════════════════════════════════════
#  TAG GENERATOR
# ══════════════════════════════════════════════════════

def _post_clean_text(text):
    """Remove channel/source name mentions from AI-generated article body and summary."""
    if not text:
        return text
    # Remove patterns like "According to NDTV,", "Aaj Tak reports", "As per Times of India"
    channel_inline = re.compile(
        r"(?:according to|as per|reported by|reports?|says?|noted by|per)\s+(?:" +
        "|".join(re.escape(c) for c in _CHANNEL_NAMES) +
        r")[,\.\s]",
        re.IGNORECASE
    )
    text = channel_inline.sub("", text)
    # Remove "NDTV ने बताया", "आज तक के अनुसार" etc.
    hindi_inline = re.compile(
        r"(?:" + "|".join(re.escape(c) for c in _CHANNEL_NAMES) + r")" +
        r"\s*(?:ने बताया|के अनुसार|की रिपोर्ट|ने कहा|के मुताबिक)[,\.\s]",
        re.IGNORECASE
    )
    text = hindi_inline.sub("", text)
    text = re.sub(r"  +", " ", text).strip()
    return text


def generate_tags(title, content, category, is_hindi=False):
    if is_hindi:
        prompt = (
            f"नीचे दी गई हिंदी खबर के लिए 5 से 6 tags बनाओ।\n"
            f"नियम:\n"
            f"- Tags हिंदी में हों (देवनागरी)\n"
            f"- हर tag 1-3 शब्दों का हो\n"
            f"- Tags news के मुख्य विषय, लोग, स्थान और घटना से जुड़े हों\n"
            f"- सिर्फ comma-separated tags return करो, कुछ और नहीं\n"
            f"- Example: मोदी सरकार, बजट 2025, आर्थिक नीति, वित्त मंत्रालय, टैक्स सुधार\n\n"
            f"शीर्षक: {title}\n"
            f"सामग्री: {content[:400]}"
        )
    else:
        prompt = (
            f"Generate 5 to 6 short, specific news tags for this article.\n"
            f"Rules:\n"
            f"- Each tag must be 1-3 words only\n"
            f"- Tags must be in English\n"
            f"- Cover: main topic, key people, location, event type, policy/impact\n"
            f"- Return ONLY comma-separated tags, nothing else\n"
            f"- Example: Budget 2025, Finance Ministry, Tax Reform, India Economy, Nirmala Sitharaman\n\n"
            f"Category: {category}\nTitle: {title}\nContent: {content[:400]}"
        )

    def clean_tag_output(text):
        if not text:
            return ""
        text = text.replace("\n", ",")
        parts = []
        seen = set()
        for raw in text.split(","):
            tag = raw.strip().strip("#").strip("\"'").strip()
            tag = re.sub(r"^[0-9\-\.\)\s]+", "", tag).strip()
            tag = " ".join(tag.split())
            if len(tag) < 2:
                continue
            low = tag.lower()
            if low not in seen:
                parts.append(tag)
                seen.add(low)
        return ", ".join(parts[:3])

    def fallback_tags():
        source_text = f"{title or ''} {content or ''}"
        raw_tokens = re.findall(r"[A-Za-z\u0900-\u097F][A-Za-z0-9\u0900-\u097F-]{2,}", source_text)
        stopwords = {
            "this", "that", "with", "from", "have", "will", "after", "about", "into", "over", "under", "more",
            "और", "के", "का", "की", "है", "था", "थे", "पर", "में", "को", "से", "लिए", "बाद", "साथ", "दिया", "किया"
        }
        picks = []
        seen = set()
        for tok in raw_tokens:
            key = tok.lower()
            if key in stopwords:
                continue
            if key not in seen:
                picks.append(tok.strip())
                seen.add(key)
            if len(picks) >= 3:
                break
        while len(picks) < 3:
            if len(picks) == 0:
                picks.append((category or "Top Story").strip())
            elif len(picks) == 1:
                picks.append("Breaking Update" if not is_hindi else "बड़ी खबर")
            else:
                picks.append("News Analysis" if not is_hindi else "ताज़ा विश्लेषण")
        return clean_tag_output(", ".join(picks[:3]))

    if not has_ai_configured():
        return fallback_tags()
    result = call_ai(prompt, max_tokens=80)
    cleaned = clean_tag_output(result)
    return cleaned or fallback_tags()


def generate_summary(title, content, lang="en", word_target=32):
    title = (title or "").strip()
    content = (content or "").strip()

    if lang == "hi":
        prompt = (
            f"नीचे दी गई खबर का {word_target} शब्दों में summary लिखो।\n"
            f"नियम:\n"
            f"- सिर्फ हिंदी (देवनागरी) में लिखो — कोई English word नहीं\n"
            f"- सीधे summary लिखो, कोई label या prefix नहीं\n"
            f"- एक ही paragraph में लिखो\n\n"
            f"शीर्षक: {title}\n"
            f"खबर: {content[:1000]}"
        )
    else:
        prompt = (
            f"Write a {word_target}-word summary of this news article.\n"
            f"Rules:\n"
            f"- Write ONLY in English — no Hindi words\n"
            f"- Write directly, no labels or prefixes\n"
            f"- One paragraph only\n\n"
            f"Title: {title}\n"
            f"News: {content[:1000]}"
        )

    ai_result = call_ai(prompt, max_tokens=120)
    if ai_result:
        # Validate language of result
        has_hindi_chars = any('\u0900' <= c <= '\u097f' for c in ai_result)
        if lang == "hi" and not has_hindi_chars:
            # AI returned English for Hindi request — retry with stronger prompt
            ai_result = call_ai(
                f"इस खबर का सारांश सिर्फ हिंदी देवनागरी में {word_target} शब्दों में लिखो:\n{title}\n{content[:500]}",
                max_tokens=120
            )
        elif lang == "en" and has_hindi_chars:
            # AI returned Hindi for English request — use fallback
            ai_result = ""
        if ai_result:
            return " ".join(ai_result.split())

    text = " ".join((content or title).replace("\n", " ").split())
    words = text.split()
    limit = max(20, min(42, word_target))
    return " ".join(words[:limit]).strip()


# ══════════════════════════════════════════════════════
#  ARTICLE BODY GENERATOR (for /api/generate_article)
# ══════════════════════════════════════════════════════

def generate_article_body(title, category, lang="en", word_target=500):
    def _fallback_article_en():
        safe_title = (title or "Breaking update").strip()
        safe_category = (category or "General").strip()
        paras = [
            f"The developments around {safe_title} have quickly become a major point of discussion in the {safe_category.lower()} space, with officials, analysts, and local stakeholders closely tracking each update.",
            "Initial information indicates that events moved rapidly over a short timeline, prompting authorities and relevant departments to issue clarifications and coordinate field-level checks. Multiple sources suggest that on-ground inputs are still being verified, and a final official position may take additional time.",
            "People directly affected by the situation have raised practical concerns including safety, service continuity, and policy impact. In response, local teams are reviewing records, speaking with key participants, and monitoring public feedback to reduce confusion and prevent misinformation.",
            "Experts say the immediate focus should remain on verified facts, transparent communication, and step-by-step disclosure of decisions. They note that rushed conclusions can create unnecessary panic, while structured updates help citizens, institutions, and businesses plan responsibly.",
            f"From a broader perspective, this story highlights how fast-moving {safe_category.lower()} issues can influence public sentiment and administrative priorities. If confirmed, the outcome may shape short-term strategy and trigger wider debate in related sectors.",
            f"For now, {safe_title} remains a developing story. Authorities are expected to share additional details after formal review, and further updates will continue as verified information becomes available."
        ]
        return "\n\n".join(paras)

    def _fallback_article_hi():
        safe_title = (title or "ताज़ा अपडेट").strip()
        safe_category = (category or "सामान्य").strip()
        paras = [
            f"{safe_title} को लेकर हालात तेजी से बदल रहे हैं और {safe_category} से जुड़े कई पक्ष इस पूरे घटनाक्रम पर नज़र बनाए हुए हैं। शुरुआती जानकारी के आधार पर यह मामला अब व्यापक चर्चा का विषय बन चुका है।",
            "प्रारंभिक संकेत बताते हैं कि घटनाएं कम समय में तेज़ी से आगे बढ़ीं, जिसके बाद संबंधित विभागों ने स्थिति स्पष्ट करने और जमीनी स्तर से तथ्य जुटाने की प्रक्रिया शुरू की। कई बिंदुओं की आधिकारिक पुष्टि अभी बाकी है।",
            "प्रभावित लोगों की मुख्य चिंताएं सुरक्षा, सेवाओं की निरंतरता और प्रशासनिक फैसलों के असर से जुड़ी हैं। स्थानीय स्तर पर टीमें दस्तावेज़ों की जांच, संबंधित पक्षों से बातचीत और सार्वजनिक प्रतिक्रियाओं की समीक्षा कर रही हैं ताकि भ्रम की स्थिति न बने।",
            "विशेषज्ञों का मानना है कि इस चरण में सबसे जरूरी बात तथ्य-आधारित रिपोर्टिंग और पारदर्शी संवाद है। जल्दबाज़ी में निष्कर्ष निकालने के बजाय क्रमवार आधिकारिक अपडेट जनता का भरोसा बनाए रखने में मदद करते हैं।",
            f"विस्तृत परिप्रेक्ष्य में देखें तो ऐसे {safe_category} से जुड़े मुद्दे नीतिगत प्राथमिकताओं और जनमत दोनों को प्रभावित करते हैं। यदि मौजूदा संकेत पुष्ट होते हैं, तो आने वाले दिनों में इस विषय पर और गहरी बहस संभव है।",
            f"फिलहाल {safe_title} को विकसित होती खबर के रूप में देखा जा रहा है। आधिकारिक समीक्षा पूरी होने के बाद अधिक स्पष्ट जानकारी सामने आने की उम्मीद है, और सत्यापित तथ्यों के आधार पर आगे की अपडेट जारी की जाएंगी।"
        ]
        return "\n\n".join(paras)

    if lang == "hi":
        prompt = (
            f"आप एक हिंदी समाचार पत्रकार हैं। नीचे दी गई हेडलाइन पर {word_target} शब्दों का "
            f"विस्तृत समाचार लेख हिंदी (देवनागरी) में लिखें।\n"
            f"- सीधे खबर से शुरू करें, headline दोबारा मत लिखें\n"
            f"- स्पष्ट पैराग्राफ में लिखें\n- तथ्यात्मक और जानकारीपूर्ण रहें\n\n"
            f"हेडलाइन: \"{title}\""
        )
    else:
        prompt = (
            f"You are a professional news journalist. Write a well-structured news article of ~{word_target} words.\n"
            f"- Start DIRECTLY with the news body (do NOT repeat the headline)\n"
            f"- Include: intro, background, key details, impact, conclusion\n"
            f"- Use clear paragraphs\n- Be factual, informative, engaging\n"
            f"- Category: {category}\n\nHeadline: \"{title}\""
        )
    ai_result = call_ai(prompt, max_tokens=1200)
    if ai_result:
        return ai_result
    return _fallback_article_hi() if lang == "hi" else _fallback_article_en()


# ══════════════════════════════════════════════════════
#  MAIN NEWS FETCHER
# ══════════════════════════════════════════════════════

def fetch_news(category="India", limit=8, submitted_by="admin"):
    """
    Fetch news from RSS feed. If RSS blocked/empty, fallback to AI-generated news.
    Hindi feeds → db_category stays as Hindi-India / Hindi-Sports / Hindi-Biz
    English feeds → db_category maps to India / Sports / Business etc.
    Both always store title+content AND hindi_title+hindi_content.
    """
    feed_url = RSS_FEEDS.get(category, RSS_FEEDS["India"])
    feed = feedparser.parse(feed_url)
    is_hindi_feed = category in HINDI_SOURCES

    # Hindi feeds → map to "Hindi-India" / "Hindi-Sports" etc. via SOURCE_TO_CATEGORY
    # This ensures Bhaskar-India, AajTak-India etc. all save as "Hindi-India" in DB
    db_category = SOURCE_TO_CATEGORY.get(category, "General")
    if is_hindi_feed and not db_category.startswith("Hindi-"):
        # Fallback: force Hindi- prefix if mapping missed
        db_category = "Hindi-" + db_category

    # ── If RSS blocked or empty → AI se news generate karo ──────────
    if len(feed.entries) == 0 and has_ai_configured():
        print(f"  RSS blocked/empty for '{category}' — using AI to generate news...")
        return _fetch_news_via_ai(category, db_category, is_hindi_feed, limit, submitted_by)

    results = []

    for entry in feed.entries[:limit]:
        raw_title = entry.get("title", "No Title")
        # Remove all common source suffixes from title
        # Handles: "Title - Source", "Title | Source", "Title | India News"
        title = re.split(r'\s*[\|\-—]\s*(?:India News|Hindi News|Latest News|Breaking|[A-Z][a-zA-Z\s]{2,30})$', raw_title)[0].strip()
        title = re.sub(r'\s*\|\s*\S.*$', '', title).strip()  # remove anything after |
        title = title.strip(" -|").strip()
        if not title:
            title = raw_title.split("|")[0].split(" - ")[0].strip()
        source_name = entry.get("source", {}).get("title", "") or category

        print(f"  [{_get_ai_engine().upper()}] Processing: {title[:65]}...")

        # Image from RSS or og:image scrape
        plain_cat = db_category.replace("Hindi-", "") if is_hindi_feed else db_category
        image_url = get_article_image(entry, plain_cat)
        print(f"  📷 Image: {'found' if image_url and 'unsplash' not in image_url else 'fallback'}")

        def _parse_json_result(raw):
            """Robustly extract title and content from AI response — handles broken JSON"""
            raw = (raw or "").strip()
            if not raw:
                return {}
            # Strip markdown fences
            clean = re.sub(r"```[a-z]*", "", raw).replace("```", "").strip()
            # Try clean JSON first
            try:
                s = clean.find("{")
                e = clean.rfind("}") + 1
                if s != -1 and e > s:
                    obj = json.loads(clean[s:e])
                    if obj.get("title") or obj.get("content"):
                        return obj
            except Exception:
                pass
            # Fallback: regex extract title and content values
            result = {}
            for key in ("title", "content"):
                # Match "title": "..." or 'title': '...'
                m = re.search(
                    rf'["\']?{key}["\']?\s*:\s*["\']([^"\'{{}}]+)["\']',
                    clean, re.DOTALL
                )
                if m:
                    result[key] = m.group(1).strip()
            if result:
                return result
            # Last resort: if response has newlines, try line-based split
            lines = [l.strip() for l in clean.split("\n") if l.strip()]
            if len(lines) >= 2:
                return {"title": lines[0], "content": " ".join(lines[1:])}
            return {}

        def _is_devanagari(text):
            return any('\u0900' <= c <= '\u097f' for c in (text or ""))

        def _is_english(text):
            latin = sum(1 for c in (text or "") if c.isascii() and c.isalpha())
            return latin > len(text or "") * 0.5

        try:
            if is_hindi_feed:
                # ── HINDI FEED ──────────────────────────────────────
                # RSS title already in Hindi — use as hindi_title directly
                hindi_title = title

                # Step 1: Write full Hindi article
                if has_ai_configured():
                    hindi_content = call_ai(
                        f"आप एक वरिष्ठ हिंदी पत्रकार हैं। नीचे दी गई हेडलाइन पर 400 शब्दों का समाचार लेख लिखें।\n\n"
                        f"कड़े नियम:\n"
                        f"- पूरा लेख सिर्फ हिंदी देवनागरी में लिखें — एक भी English word नहीं\n"
                        f"- सीधे खबर के body से शुरू करें — headline repeat मत करें\n"
                        f"- 4-5 paragraphs में लिखें\n"
                        f"- तथ्यात्मक और स्पष्ट भाषा\n\n"
                        f"हेडलाइन: \"{title}\"",
                        max_tokens=1000
                    )
                    hindi_content = _post_clean_text(hindi_content)
                    # Validate: must be Devanagari
                    if not hindi_content or not _is_devanagari(hindi_content):
                        hindi_content = (
                            f"{title} — इस विषय पर ताज़ा घटनाक्रम सामने आया है। "
                            f"सूत्रों के अनुसार यह मामला तेज़ी से आगे बढ़ रहा है। "
                            f"संबंधित अधिकारी पूरी स्थिति पर कड़ी नज़र बनाए हुए हैं "
                            f"और जल्द ही आधिकारिक बयान जारी होने की उम्मीद है। "
                            f"इस खबर से जुड़े सभी पहलुओं की गहन जांच जारी है।"
                        )
                else:
                    hindi_content = (
                        f"{title} — इस विषय पर ताज़ा घटनाक्रम सामने आया है। "
                        f"सूत्रों के अनुसार यह मामला तेज़ी से आगे बढ़ रहा है। "
                        f"संबंधित अधिकारी पूरी स्थिति पर नज़र बनाए हुए हैं। "
                        f"जल्द ही आधिकारिक बयान जारी होने की उम्मीद है।"
                    )

                # Step 2: Translate Hindi → English
                # Use SEPARATE calls for title and content to avoid JSON truncation
                en_title = ""
                en_content = ""
                if has_ai_configured():
                    # 2a. Title only (short call, always succeeds)
                    t_raw = call_ai(
                        f"Translate this Hindi news headline to English.\n"
                        f"Return ONLY the English headline — no quotes, no explanation, no punctuation at start.\n"
                        f"The headline must be in English only (no Devanagari/Hindi characters).\n\n"
                        f"Hindi: {hindi_title}",
                        max_tokens=80
                    )
                    t_raw = (t_raw or "").strip().strip('"').strip("'")
                    if t_raw and not _is_devanagari(t_raw):
                        en_title = t_raw

                    # 2b. Content only (plain text, no JSON)
                    c_raw = call_ai(
                        f"Translate the following Hindi news article into fluent English.\n"
                        f"Rules: Write 400-500 words. English only — no Hindi/Devanagari. "
                        f"Start directly with news body. Do NOT repeat the headline. "
                        f"Do not mention any news channel name.\n\n"
                        f"Hindi Article:\n{hindi_content[:1200]}",
                        max_tokens=1000
                    )
                    c_raw = _post_clean_text((c_raw or "").strip())
                    if c_raw and not _is_devanagari(c_raw):
                        en_content = c_raw

                if not en_title:
                    en_title = f"Breaking: Latest {db_category.replace('Hindi-', '')} Update"
                if not en_content:
                    en_content = (
                        f"Authorities and officials are closely monitoring the latest developments. "
                        f"Sources indicate that events have been unfolding rapidly in this matter. "
                        f"Key stakeholders are expected to issue formal statements shortly. "
                        f"Further updates will be shared as verified information becomes available."
                    )

                tags = generate_tags(hindi_title, hindi_content, db_category, is_hindi=True)

            else:
                # ── ENGLISH FEED ─────────────────────────────────────
                en_title = title

                # Step 1: Write full English article
                if has_ai_configured():
                    en_content = call_ai(
                        f"You are a professional Indian news journalist. Write a news article of ~500 words.\n\n"
                        f"STRICT RULES:\n"
                        f"- Write ONLY in English — no Hindi/Devanagari words at all\n"
                        f"- Start directly with the news body — do NOT repeat the headline\n"
                        f"- Structure: intro → background → key details → impact → conclusion\n"
                        f"- Use clear paragraphs\n"
                        f"- Factual, informative, professional tone\n"
                        f"- Category: {db_category}\n\n"
                        f"Headline: \"{title}\"",
                        max_tokens=1000
                    )
                    en_content = _post_clean_text(en_content)
                    # Validate: must be English
                    if not en_content or _is_devanagari(en_content):
                        en_content = ""

                if not en_content:
                    en_content = (
                        f"Authorities and officials are closely monitoring the latest developments around {title}. "
                        f"Sources indicate that events have been unfolding rapidly, prompting detailed scrutiny from relevant departments. "
                        f"Key stakeholders are expected to issue formal statements after reviewing the situation thoroughly. "
                        f"The matter continues to attract significant attention from experts and the general public alike. "
                        f"Further updates will be shared as verified information becomes available."
                    )

                # Step 2: Translate English → Hindi
                # Use SEPARATE calls for title and content to avoid JSON truncation
                hindi_title   = ""
                hindi_content = ""
                if has_ai_configured():
                    # 2a. Title only (short, always succeeds)
                    ht_raw = call_ai(
                        f"Translate this English news headline to Hindi Devanagari script.\n"
                        f"Return ONLY the Hindi headline — no quotes, no explanation, pure Devanagari only.\n"
                        f"No Roman/English letters at all.\n\n"
                        f"English: {title}",
                        max_tokens=80
                    )
                    ht_raw = (ht_raw or "").strip().strip('"').strip("'")
                    if ht_raw and _is_devanagari(ht_raw):
                        hindi_title = ht_raw

                    # 2b. Content only (plain text, no JSON)
                    hc_raw = call_ai(
                        f"Translate the following English news article into natural Hindi (Devanagari script).\n"
                        f"Rules: Write 400-500 words. Pure Devanagari only — no English/Roman characters. "
                        f"Natural journalistic Hindi. Start directly with news body. "
                        f"Do NOT repeat the headline. Do not mention any news channel name.\n\n"
                        f"English Article:\n{en_content[:1200]}",
                        max_tokens=1000
                    )
                    hc_raw = _post_clean_text((hc_raw or "").strip())
                    if hc_raw and _is_devanagari(hc_raw):
                        hindi_content = hc_raw

                if not hindi_title:
                    cat_hindi = {
                        "India": "भारत", "World": "विश्व", "Sports": "खेल",
                        "Business": "व्यापार", "Technology": "तकनीक",
                        "Politics": "राजनीति", "General": "समाचार"
                    }.get(db_category, "ताज़ा खबर")
                    hindi_title = f"{cat_hindi}: ताज़ा समाचार"
                if not hindi_content:
                    hindi_content = (
                        f"{hindi_title} — इस विषय पर ताज़ा घटनाक्रम सामने आया है। "
                        f"सूत्रों के अनुसार यह मामला तेज़ी से आगे बढ़ रहा है। "
                        f"संबंधित अधिकारी पूरी स्थिति पर कड़ी नज़र बनाए हुए हैं "
                        f"और जल्द ही आधिकारिक बयान जारी होने की उम्मीद है।"
                    )

                tags = generate_tags(title, en_content, db_category, is_hindi=False)

        except Exception as e:
            print(f"  Article processing error: {e}")
            if is_hindi_feed:
                # title is already Hindi — set hindi_title, generate English separately
                hindi_title   = title
                hindi_content = f"{title} — यह खबर विकसित हो रही है। जल्द ही अधिक जानकारी उपलब्ध होगी।"
                en_title      = f"Breaking: Latest {db_category.replace('Hindi-', '')} Update"
                en_content    = (
                    f"Developing story. Authorities are monitoring the situation. "
                    f"More details will be available shortly."
                )
            else:
                # title is English — set en_title, build Hindi placeholder
                en_title      = title
                en_content    = (
                    f"Developing story: {title}. Authorities are monitoring the situation. "
                    f"More details will be available shortly."
                )
                cat_hindi = {
                    "India": "भारत", "World": "विश्व", "Sports": "खेल",
                    "Business": "व्यापार", "Technology": "तकनीक",
                    "Politics": "राजनीति", "General": "समाचार"
                }.get(db_category, "ताज़ा खबर")
                hindi_title   = f"{cat_hindi}: ताज़ा अपडेट"
                hindi_content = f"{cat_hindi} — यह खबर विकसित हो रही है। जल्द ही अधिक जानकारी उपलब्ध होगी।"
            tags = generate_tags(
                hindi_title if is_hindi_feed else en_title,
                hindi_content if is_hindi_feed else en_content,
                db_category, is_hindi=is_hindi_feed
            )

        results.append({
            "title":         en_title,
            "content":       en_content,
            "hindi_title":   hindi_title,
            "hindi_content": hindi_content,
            "source":        source_name,
            "category":      db_category,
            "image_url":     image_url,
            "tags":          tags,
            "submitted_by":  submitted_by,
        })
        print(f"  ✓ Done — EN: {en_title[:40]} | HI: {hindi_title[:30]}")

    return results


def _fetch_news_via_ai(category, db_category, is_hindi_feed, limit, submitted_by):
    """
    Jab RSS blocked ho to Gemini se latest news headlines generate karo
    aur unka poora article banao.
    """
    from datetime import date
    today = date.today().strftime("%B %d, %Y")

    # Category ke hisaab se topic define karo
    topic_map = {
        "India": "Indian national news, politics, government",
        "World": "international world news",
        "Sports": "sports news India cricket football",
        "Business": "Indian business economy finance",
        "Technology": "technology gadgets AI India",
        "Politics": "Indian politics elections government",
        "Hindi-India": "भारत की ताज़ा राष्ट्रीय खबरें",
        "Hindi-Sports": "खेल समाचार क्रिकेट भारत",
        "Hindi-Biz": "भारतीय व्यापार अर्थव्यवस्था",
        "AajTak-India": "भारत की ताज़ा राष्ट्रीय खबरें",
        "AajTak-Sports": "खेल समाचार क्रिकेट भारत",
        "AajTak-World": "अंतरराष्ट्रीय समाचार",
        "Bhaskar-India": "भारत की ताज़ा खबरें",
        "Bhaskar-Sports": "खेल समाचार",
        "Bhaskar-Biz": "व्यापार समाचार",
        "Bhaskar-Tech": "तकनीक समाचार",
        "NBT-India": "भारत की ताज़ा खबरें",
        "NBT-Sports": "खेल समाचार",
        "NBT-Biz": "व्यापार समाचार",
        "Jagran-India": "भारत की ताज़ा खबरें",
        "Jagran-Sports": "खेल समाचार",
        "Jagran-World": "अंतरराष्ट्रीय समाचार",
        "TOI-India": "India national news today",
        "TOI-World": "world news today",
        "TOI-Sports": "sports news today India",
        "TOI-Business": "India business news today",
        "HT-India": "India news today",
        "HT-World": "world news today",
        "HT-Sports": "sports news India today",
        "NDTV-India": "India news today",
        "NDTV-World": "world news today",
        "NDTV-Sports": "sports news India",
        "NDTV-Tech": "technology news India",
    }

    topic = topic_map.get(category, category)

    print(f"  🤖 AI generating {limit} news articles for topic: {topic}")

    # Step 1: AI se {limit} headlines generate karo
    if is_hindi_feed:
        headlines_prompt = (
            f"आज {today} की {topic} की {limit} ताज़ा और real समाचार headlines बनाओ।\n"
            f"नियम:\n"
            f"- हर headline अलग topic पर हो\n"
            f"- Real, believable, current events जैसी लगनी चाहिए\n"
            f"- सिर्फ numbered list में headlines दो\n"
            f"- हर headline 10-15 शब्दों की हो\n"
            f"- सिर्फ हिंदी देवनागरी में\n\n"
            f"Format:\n1. headline\n2. headline\n..."
        )
    else:
        headlines_prompt = (
            f"Generate {limit} realistic latest news headlines for today {today} about: {topic}\n"
            f"Rules:\n"
            f"- Each headline must be on a different sub-topic\n"
            f"- Sound like real current news headlines\n"
            f"- 10-15 words each\n"
            f"- Return ONLY numbered list of headlines, nothing else\n\n"
            f"Format:\n1. headline\n2. headline\n..."
        )

    headlines_raw = call_ai(headlines_prompt, max_tokens=500)
    if not headlines_raw:
        return []

    # Parse headlines
    headlines = []
    for line in headlines_raw.strip().split("\n"):
        line = line.strip()
        # Remove numbering like "1.", "1)", etc.
        clean = re.sub(r'^[\d]+[\.\)]\s*', '', line).strip()
        if clean and len(clean) > 10:
            headlines.append(clean)

    headlines = headlines[:limit]
    print(f"  📰 Got {len(headlines)} headlines from AI")

    results = []
    for title in headlines:
        print(f"  Processing: {title[:60]}...")

        image_url = get_category_image(db_category.replace("Hindi-", "") if is_hindi_feed else db_category)

        try:
            if is_hindi_feed:
                hindi_title = title
                # Write Hindi article
                hindi_content = call_ai(
                    f"इस हिंदी headline पर 400 शब्दों का समाचार लेख लिखो।\n"
                    f"नियम: सिर्फ हिंदी देवनागरी, सीधे body से शुरू करो, headline repeat मत करो।\n\n"
                    f"Headline: {title}",
                    max_tokens=800
                ) or f"{title} — इस विषय पर ताज़ा जानकारी सामने आ रही है।"

                # Translate to English
                en_raw = call_ai(
                    f"Translate to English. Return ONLY JSON: {{\"title\": \"...\", \"content\": \"...\"}}\n"
                    f"Hindi Title: {hindi_title}\nHindi Content: {hindi_content[:600]}",
                    max_tokens=1000
                )
                parsed = {}
                try:
                    clean = (en_raw or "").replace("```json","").replace("```","").strip()
                    s = clean.find("{"); e = clean.rfind("}") + 1
                    if s != -1 and e > s:
                        parsed = json.loads(clean[s:e])
                except: pass

                en_title = parsed.get("title", "").strip() or hindi_title
                en_content = parsed.get("content", "").strip() or f"Developing story: {en_title}"
                tags = generate_tags(hindi_title, hindi_content, db_category, is_hindi=True)

            else:
                en_title = title
                # Write English article
                en_content = call_ai(
                    f"Write a 400-word news article. Rules: English only, start directly with body, don't repeat headline.\n\n"
                    f"Headline: {title}\nCategory: {db_category}",
                    max_tokens=800
                ) or f"Developing story: {title}. More details will be available shortly."

                # Translate to Hindi
                hi_raw = call_ai(
                    f"Translate to Hindi Devanagari. Return ONLY JSON: {{\"title\": \"...\", \"content\": \"...\"}}\n"
                    f"English Title: {title}\nEnglish Content: {en_content[:600]}",
                    max_tokens=1000
                )
                parsed = {}
                try:
                    clean = (hi_raw or "").replace("```json","").replace("```","").strip()
                    s = clean.find("{"); e = clean.rfind("}") + 1
                    if s != -1 and e > s:
                        parsed = json.loads(clean[s:e])
                except: pass

                hindi_title = parsed.get("title", "").strip() or title
                hindi_content = parsed.get("content", "").strip() or f"{hindi_title} — ताज़ा जानकारी उपलब्ध होगी।"
                tags = generate_tags(title, en_content, db_category, is_hindi=False)

            results.append({
                "title":         en_title,
                "content":       en_content,
                "hindi_title":   hindi_title,
                "hindi_content": hindi_content,
                "source":        category,
                "category":      db_category,
                "image_url":     image_url,
                "tags":          tags,
                "submitted_by":  submitted_by,
            })
            print(f"  ✓ Done — EN: {en_title[:40]} | HI: {hindi_title[:30]}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    return results

