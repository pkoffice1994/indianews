import os
import uuid
import html
import base64
from urllib.parse import quote, urlencode
from dotenv import load_dotenv
load_dotenv()

import requests as req
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from db import (
    add_comment,
    create_staff,
    delete_comment,
    delete_news,
    delete_staff,
    get_all_news,
    get_all_staff,
    get_approved_news,
    get_category_stats,
    get_city_stats,
    get_comments,
    get_country_stats,
    get_news_by_id,
    get_staff,
    get_stats,
    get_top_picks,
    get_module_config,
    get_module_items,
    increment_views,
    init_db,
    insert_news,
    create_module_item,
    delete_module_item,
    set_top_pick,
    count_top_picks,
    toggle_module_item_status,
    update_comment_status,
    update_news,
    update_staff,
    update_status,
)
def _load_local_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


_load_local_env()

from news_agent import (
    _sanitize_channel_mentions,
    fetch_news,
    generate_article_body,
    generate_summary,
    generate_tags,
    has_ai_configured,
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "india-news-dev-secret")
app.jinja_env.globals["urlencode"] = urlencode
init_db()

ADMIN_USER = "admin"
ADMIN_PASS = "1234"
UPLOAD_DIR = "static/uploads"
DAY_NIGHT_OPTIONS = {"day", "night"}
ENGLISH_CATEGORIES = ["India", "World", "Politics", "Business", "Sports", "Technology", "General"]
HINDI_CATEGORIES = ["Hindi-India", "Hindi-Sports", "Hindi-Biz"]
DEFAULT_CATEGORY_IMAGES = {
    "India": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200&q=80",
    "World": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80",
    "Technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
    "Business": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
    "Sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80",
    "Politics": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=80",
    "General": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80",
    "Hindi-India": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200&q=80",
    "Hindi-Sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80",
    "Hindi-Biz": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
}
MODULE_LABELS = {
    "category": "Category",
    "subcategory": "Subcategory",
    "tag": "Tag",
    "news": "News",
    "short": "Short",
    "featured_section": "Featured Section",
    "ad_spaces": "Ad Spaces",
    "user": "User",
    "comment_flag": "Comment Flag",
    "send_notification": "Send Notification",
    "pages": "Pages",
    "roles": "Roles",
    "system_setting": "System Setting",
}


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(file):
    if not file or not file.filename:
        return ""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "bin"
    filename = f"{uuid.uuid4().hex}.{ext}"
    ensure_upload_dir()
    file.save(os.path.join(UPLOAD_DIR, filename))
    return f"/static/uploads/{filename}"


def get_location(ip):
    try:
        if ip in ("127.0.0.1", "::1", "localhost"):
            return "Local", "Local"
        r = req.get(f"http://ip-api.com/json/{ip}?fields=country,city", timeout=3)
        data = r.json()
        return data.get("country", "Unknown"), data.get("city", "Unknown")
    except Exception:
        return "Unknown", "Unknown"


def is_logged_in():
    return session.get("logged_in") or session.get("staff_logged_in")


def get_role():
    return session.get("role", "admin")


def get_uname():
    return session.get("username", "admin")


def is_admin():
    return get_role() == "admin"


def can_access_news_item(item):
    return bool(item) and (is_admin() or item.get("submitted_by") == get_uname())


def require_admin_dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Access denied. Admin only.", "warning")
        return redirect(url_for("dashboard"))
    return None


def normalize_tags(raw_tags):
    if not raw_tags:
        return []
    clean = []
    seen = set()
    normalized = raw_tags.replace("\n", ",")
    for tag in normalized.split(","):
        value = tag.strip().strip("#").strip("\"'").strip()
        value = value.lstrip("0123456789.-) ").strip()
        if not value:
            continue
        value = " ".join(value.split())
        key = value.lower()
        if key not in seen:
            clean.append(value)
            seen.add(key)
    return clean[:3]


def looks_hindi(text):
    return any("\u0900" <= ch <= "\u097f" for ch in (text or ""))


def is_hindi_category(category):
    return (category or "").startswith("Hindi-")


def get_display_title(article, lang):
    """
    Hindi portal (lang=hi): show hindi_title first, fallback to title.
    English portal (lang=en): show title first, fallback to hindi_title.
    Hindi articles (Hindi-* category): always prefer hindi_title for hi, en title for en.
    """
    source = article.get("source", "")
    category = article.get("category", "")
    hi = _sanitize_channel_mentions((article.get("hindi_title") or "").strip(), source)
    en = _sanitize_channel_mentions((article.get("title") or "").strip(), source)
    # If English title has Hindi chars it is bad data — discard it
    if en and looks_hindi(en):
        en = ""
    # If Hindi title has no Hindi chars it is bad data — discard it
    if hi and not looks_hindi(hi):
        hi = ""
    if lang == "hi":
        # For Hindi portal: prefer Hindi title; for English articles without Hindi title, show English
        return hi or en
    else:
        # For English portal: prefer English title; for Hindi articles without English title, show Hindi
        return en or hi


def get_display_content(article, lang):
    """
    Hindi portal (lang=hi): show hindi_content first, fallback to content.
    English portal (lang=en): show content first, fallback to hindi_content.
    """
    source = article.get("source", "")
    hi = _sanitize_channel_mentions((article.get("hindi_content") or "").strip(), source)
    en = _sanitize_channel_mentions((article.get("content") or "").strip(), source)
    if en and looks_hindi(en):
        en = ""
    if hi and not looks_hindi(hi):
        hi = ""
    if lang == "hi":
        return hi or en
    else:
        return en or hi


def _compact_text(text):
    return " ".join((text or "").replace("\n", " ").split())


def _fallback_summary(text, max_words=30):
    words = _compact_text(text).split()
    if not words:
        return ""
    return " ".join(words[:max_words]).strip()


def get_display_summary(article, lang, max_words=30):
    content = get_display_content(article, lang)
    if not content:
        return ""
    return _fallback_summary(content, max_words=max_words)


def decorate_article(article, lang="hi"):
    article = dict(article)
    article["tag_list"] = normalize_tags(article.get("tags", ""))
    article["display_title"] = get_display_title(article, lang)
    article["display_content"] = get_display_content(article, lang)
    article["display_summary"] = get_display_summary(article, lang, max_words=30)
    article["detail_url"] = url_for("news_detail", id=article["id"], lang=lang)
    article["share_url"] = request.url_root.rstrip("/") + url_for("news_detail", id=article["id"], lang=lang)
    encoded_title = quote(article["display_title"] or article.get("title", ""))
    encoded_url = quote(article["share_url"])
    article["share_links"] = {
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "whatsapp": f"https://wa.me/?text={encoded_title}%20{encoded_url}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}",
    }
    return article


def get_theme():
    theme = request.args.get("theme", "").strip().lower()
    if theme in DAY_NIGHT_OPTIONS:
        return theme
    return "day"


def build_ai_image_url(title, category, mood="day"):
    title = (title or "Breaking News").strip()
    category = (category or "General").strip()

    if mood == "night":
        bg1, bg2, fg, accent = "#0a0e1a", "#1a2744", "#f0f4ff", "#e11d48"
    else:
        bg1, bg2, fg, accent = "#1a2744", "#c8381a", "#ffffff", "#ffffff"

    # Word-wrap title into lines of max 30 chars
    words = title[:140].split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) <= 30:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:4]

    cat_safe = html.escape(category.upper()[:22])
    cat_w = max(120, len(cat_safe) * 14 + 24)

    # Build text lines
    line_h = 66
    total_h = len(lines) * line_h
    start_y = 340 - total_h // 2
    txt = ""
    for i, ln in enumerate(lines):
        txt += f"<text x='60' y='{start_y + i*line_h}' fill='{fg}' font-size='54' font-family='Georgia,serif' font-weight='700'>{html.escape(ln)}</text>\n  "

    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='675'>"
        f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
        f"<stop offset='0%' stop-color='{bg1}'/><stop offset='100%' stop-color='{bg2}'/>"
        f"</linearGradient></defs>"
        f"<rect width='1200' height='675' fill='url(#g)'/>"
        f"<rect x='0' y='0' width='6' height='675' fill='{accent}'/>"
        f"<rect x='0' y='590' width='1200' height='3' fill='{accent}' opacity='0.4'/>"
        f"<rect x='48' y='48' rx='6' ry='6' width='{cat_w}' height='38' fill='{accent}'/>"
        f"<text x='60' y='74' fill='#fff' font-size='19' font-family='Arial,sans-serif' font-weight='800' letter-spacing='2'>{cat_safe}</text>"
        f"{txt}"
        f"<text x='60' y='645' fill='rgba(255,255,255,0.45)' font-size='17' font-family='Arial,sans-serif'>NewsDesk · Auto Generated</text>"
        f"</svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def get_display_image(article):
    image_url = (article.get("image_url") or "").strip()
    if image_url:
        return image_url
    title = article.get("display_title") or article.get("title") or article.get("hindi_title") or "India News update"
    mood = "day"
    try:
        mood = get_theme()
    except Exception:
        mood = "day"
    return build_ai_image_url(title, article.get("category", "General"), mood=mood)


def get_dashboard_summary(article):
    if is_hindi_category(article.get("category", "")):
        return _fallback_summary(article.get("hindi_content", ""), max_words=24)
    return _fallback_summary(article.get("content", ""), max_words=24)


app.jinja_env.globals["get_dashboard_summary"] = get_dashboard_summary


def normalize_category_selection(language, category):
    language = (language or "en").strip().lower()
    category = (category or "General").strip()
    if language == "hi":
        if category in HINDI_CATEGORIES:
            return category
        hindi_map = {
            "India": "Hindi-India",
            "Sports": "Hindi-Sports",
            "Business": "Hindi-Biz",
            "Politics": "Hindi-India",
            "World": "Hindi-India",
            "Technology": "Hindi-Biz",
            "General": "Hindi-India",
        }
        return hindi_map.get(category, "Hindi-India")
    if category in ENGLISH_CATEGORIES:
        return category
    english_map = {
        "Hindi-India": "India",
        "Hindi-Sports": "Sports",
        "Hindi-Biz": "Business",
    }
    return english_map.get(category, "General")


def normalize_article_by_category(title, content, hindi_title, hindi_content, category):
    """
    Store whatever the user filled in.
    Hindi category: store in hindi fields (English fields stay empty unless provided).
    English category: store in English fields (Hindi fields stay empty unless provided).
    get_display_title/content will do the right fallback when showing.
    """
    if is_hindi_category(category):
        # Hindi article — keep hindi fields, clear english if empty
        return (
            title.strip(),          # keep if provided
            content.strip(),        # keep if provided
            hindi_title.strip(),
            hindi_content.strip(),
        )
    return (
        title.strip(),
        content.strip(),
        hindi_title.strip(),        # keep if provided
        hindi_content.strip(),      # keep if provided
    )


def build_dashboard_payload(role, username):
    news = get_all_news(role=role, username=username)
    stats = get_stats() if role == "admin" else get_stats(news)
    cat_stats = get_category_stats(role=role, username=username)
    country_stats = get_country_stats() if role == "admin" else []
    city_stats = get_city_stats() if role == "admin" else []
    comments = get_comments() if role == "admin" else []
    return news, stats, cat_stats, country_stats, city_stats, comments


@app.route("/", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["logged_in"] = True
            session["role"] = "admin"
            session["username"] = "admin"
            return redirect(url_for("dashboard"))
        staff = get_staff(u, p)
        if staff and staff["status"] == "active":
            session["staff_logged_in"] = True
            session["role"] = staff["role"]
            session["username"] = staff["username"]
            return redirect(url_for("dashboard"))
        error = "Invalid credentials. Try again."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    role = get_role()
    uname = get_uname()
    news, stats, cat_stats, country_stats, city_stats, comments = build_dashboard_payload(role, uname)
    f = request.args.get("filter", "all")
    if f != "all":
        news = [n for n in news if n["status"] == f]
    return render_template(
        "dashboard.html",
        news=news,
        stats=stats,
        cat_stats=cat_stats,
        country_stats=country_stats,
        city_stats=city_stats,
        comments=comments,
        filter=f,
        role=role,
        username=uname,
        top_pick_count=count_top_picks(),
    )


@app.route("/manage/<module>", methods=["GET", "POST"])
def manage_module(module):
    guard = require_admin_dashboard()
    if guard:
        return guard
    cfg = get_module_config(module)
    if not cfg:
        flash("⚠️ Unknown module.", "warning")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        payload = {}
        for field in cfg["fields"]:
            payload[field] = request.form.get(field, "").strip()
        # For ad_spaces: if image file uploaded, use that over URL
        if module == "ad_spaces":
            file = request.files.get("ad_image_file")
            upload_url = save_upload(file)
            if upload_url:
                payload["image_url"] = upload_url
        status_field = cfg.get("status_field") or ""
        if status_field:
            payload[status_field] = request.form.get(status_field, "active").strip() or "active"
        if create_module_item(module, payload):
            flash(f"✅ {MODULE_LABELS.get(module, module)} added.", "success")
        else:
            flash(f"⚠️ Could not add {MODULE_LABELS.get(module, module)}. Duplicate or invalid data.", "warning")
        return redirect(url_for("manage_module", module=module))
    items = get_module_items(module)
    return render_template(
        "module_manage.html",
        module=module,
        module_label=MODULE_LABELS.get(module, module),
        fields=cfg["fields"],
        status_field=cfg.get("status_field", ""),
        items=items,
        role=get_role(),
        username=get_uname(),
    )


@app.route("/manage/<module>/delete/<int:item_id>")
def manage_module_delete(module, item_id):
    guard = require_admin_dashboard()
    if guard:
        return guard
    if delete_module_item(module, item_id):
        flash("🗑️ Item deleted.", "info")
    else:
        flash("⚠️ Delete failed.", "warning")
    return redirect(url_for("manage_module", module=module))


@app.route("/manage/<module>/toggle/<int:item_id>")
def manage_module_toggle(module, item_id):
    guard = require_admin_dashboard()
    if guard:
        return guard
    if toggle_module_item_status(module, item_id):
        flash("✅ Status updated.", "success")
    else:
        flash("⚠️ Status update not available for this module.", "warning")
    return redirect(url_for("manage_module", module=module))


@app.route("/generate")
def generate():
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can fetch AI news.", "warning")
        return redirect(url_for("dashboard"))
    category = request.args.get("category", "India")
    uname = get_uname()
    items = fetch_news(category=category, limit=8, submitted_by=uname)
    for n in items:
        insert_news(
            n["title"],
            n["content"],
            n["hindi_title"],
            n["hindi_content"],
            n["source"],
            n["category"],
            n.get("image_url", ""),
            n.get("tags", ""),
            uname,
        )
    if has_ai_configured():
        flash(f"✅ {len(items)} articles fetched from '{category}' with rewritten content, auto summary, and 3 strong tags.", "success")
    else:
        flash(
            f"⚠️ {len(items)} articles fetched from '{category}' in fallback mode with basic summary + tags.",
            "warning",
        )
    return redirect(url_for("dashboard"))


@app.route("/approve/<int:id>")
def approve(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can approve articles.", "warning")
        return redirect(url_for("dashboard"))
    update_status(id, "approved")
    flash("✅ Article approved & published!", "success")
    return redirect(url_for("dashboard"))


@app.route("/reject/<int:id>")
def reject(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can reject articles.", "warning")
        return redirect(url_for("dashboard"))
    update_status(id, "rejected")
    flash("🚫 Article rejected.", "warning")
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:id>")
def delete(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    item = get_news_by_id(id)
    if not can_access_news_item(item):
        flash("⚠️ Access denied.", "warning")
        return redirect(url_for("dashboard"))
    if not is_admin() and item.get("status") == "approved":
        flash("⚠️ Staff cannot delete published articles.", "warning")
        return redirect(url_for("dashboard"))
    delete_news(id)
    flash("🗑️ Article deleted.", "info")
    return redirect(url_for("dashboard"))


@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    item = get_news_by_id(id)
    if not can_access_news_item(item):
        flash("⚠️ Access denied.", "warning")
        return redirect(url_for("dashboard"))
    if not is_admin() and item.get("status") == "approved":
        flash("⚠️ Only admins can edit published articles.", "warning")
        return redirect(url_for("dashboard"))
    category = item.get("category", "General")
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    hindi_title = request.form.get("hindi_title", "").strip()
    hindi_content = request.form.get("hindi_content", "").strip()
    title, content, hindi_title, hindi_content = normalize_article_by_category(
        title, content, hindi_title, hindi_content, category
    )
    image_url = request.form.get("image_url", "").strip()
    tags = request.form.get("tags", "").strip()
    file = request.files.get("image_file")
    upload_url = save_upload(file)
    if upload_url:
        image_url = upload_url
    update_news(id, title, content, hindi_title, hindi_content, image_url, tags)
    flash("✏️ Article updated successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/api/generate_tags", methods=["POST"])
def api_generate_tags():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    data = request.json or {}
    title = data.get("title", "")
    content = data.get("content", "")
    category = data.get("category", "General")
    is_hindi = data.get("is_hindi", False)
    tags = generate_tags(title, content, category, is_hindi=is_hindi)
    return jsonify({"tags": tags})


@app.route("/api/generate_summary", methods=["POST"])
def api_generate_summary():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    data = request.json or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    lang = (data.get("lang") or "en").strip().lower()
    if not title and not content:
        return jsonify({"error": "title_or_content_required"}), 400
    summary = generate_summary(title, content, lang=lang, word_target=32)
    return jsonify({"summary": summary})


@app.route("/api/generate_article", methods=["POST"])
def api_generate_article():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    if not is_admin():
        return jsonify({"error": "forbidden"}), 403
    data = request.json or {}
    title = (data.get("title") or "").strip()
    category = data.get("category", "General")
    lang = data.get("lang", "en")
    if not title:
        return jsonify({"error": "title_required"}), 400
    article = generate_article_body(title, category, lang=lang, word_target=500)
    return jsonify({"content": article, "provider": "ai_or_fallback"})


@app.route("/api/translate", methods=["POST"])
def api_translate():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    data = request.json or {}
    title   = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    target  = (data.get("target") or "en").strip().lower()  # "hi" or "en"

    if not title:
        return jsonify({"error": "title_required"}), 400

    from news_agent import call_ai

    def is_dev(t):
        return any('ऀ' <= c <= 'ॿ' for c in (t or ""))

    if target == "hi":
        # Translate English → Hindi
        t_raw = call_ai(
            f"Translate this English news headline to Hindi Devanagari script.\n"
            f"Return ONLY the Hindi headline — pure Devanagari, no Roman letters, no explanation.\n\n"
            f"English: {title}",
            max_tokens=80
        )
        t_out = (t_raw or "").strip().strip('"').strip("'")
        if not is_dev(t_out):
            t_out = ""

        c_out = ""
        if content:
            c_raw = call_ai(
                f"Translate this English news article into natural Hindi (Devanagari script).\n"
                f"Rules: 400-500 words. Pure Devanagari only. Natural journalistic Hindi. "
                f"Start directly with news body. Do NOT repeat the headline.\n\n"
                f"English Article:\n{content[:1200]}",
                max_tokens=1000
            )
            c_out = (c_raw or "").strip()
            if not is_dev(c_out):
                c_out = ""

        return jsonify({"title": t_out, "content": c_out, "target": "hi"})

    else:
        # Translate Hindi → English
        t_raw = call_ai(
            f"Translate this Hindi news headline to English.\n"
            f"Return ONLY the English headline — no quotes, no explanation, no Devanagari.\n\n"
            f"Hindi: {title}",
            max_tokens=80
        )
        t_out = (t_raw or "").strip().strip('"').strip("'")
        if is_dev(t_out):
            t_out = ""

        c_out = ""
        if content:
            c_raw = call_ai(
                f"Translate this Hindi news article into fluent English.\n"
                f"Rules: 400-500 words. English only — no Hindi/Devanagari. "
                f"Start directly with news body. Do NOT repeat the headline.\n\n"
                f"Hindi Article:\n{content[:1200]}",
                max_tokens=1000
            )
            c_out = (c_raw or "").strip()
            if is_dev(c_out):
                c_out = ""

        return jsonify({"title": t_out, "content": c_out, "target": "en"})


@app.route("/api/generate_image", methods=["POST"])
def api_generate_image():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    if not is_admin():
        return jsonify({"error": "forbidden"}), 403
    data = request.json or {}
    title = (data.get("title") or "").strip()
    category = normalize_category_selection(data.get("language", "en"), data.get("category", "General"))
    mood = (data.get("mood") or "day").strip().lower()
    if mood not in DAY_NIGHT_OPTIONS:
        mood = "day"
    if not title:
        return jsonify({"error": "title_required"}), 400
    return jsonify({"image_url": build_ai_image_url(title, category, mood=mood), "provider": "local_generated"})


@app.route("/top-pick/<int:id>")
def toggle_top_pick(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can manage top 5 news.", "warning")
        return redirect(url_for("dashboard"))
    item = get_news_by_id(id)
    if not item:
        flash("⚠️ Article not found.", "warning")
        return redirect(url_for("dashboard"))
    if item.get("status") != "approved":
        flash("⚠️ Only approved articles can be added to Top 5.", "warning")
        return redirect(url_for("dashboard"))
    enable = not bool(item.get("top_pick"))
    if enable and count_top_picks() >= 5:
        flash("⚠️ Top 5 list is full. Please remove an existing item first.", "warning")
        return redirect(url_for("dashboard"))
    set_top_pick(id, enable)
    flash("⭐ Top 5 updated." if enable else "⭐ News removed from Top 5.", "success")
    return redirect(url_for("dashboard"))


@app.route("/upload_image", methods=["POST"])
def upload_image():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "no file"}), 400
    url = save_upload(file)
    return jsonify({"url": url})


@app.route("/staff")
def staff_list():
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Access denied.", "warning")
        return redirect(url_for("dashboard"))
    staff = get_all_staff()
    return render_template("staff.html", staff=staff, role=get_role(), username=get_uname())


@app.route("/staff/create", methods=["POST"])
def staff_create():
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can create staff.", "warning")
        return redirect(url_for("staff_list"))
    u = request.form.get("username", "").strip()
    p = request.form.get("password", "").strip()
    r = request.form.get("role", "writer")
    if not u or not p:
        flash("❌ Username and password required.", "warning")
    elif create_staff(u, p, r):
        flash(f"✅ Staff '{u}' created as {r}.", "success")
    else:
        flash(f"❌ Username '{u}' already exists.", "warning")
    return redirect(url_for("staff_list"))


@app.route("/staff/edit/<int:id>", methods=["POST"])
def staff_edit(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can edit staff.", "warning")
        return redirect(url_for("staff_list"))
    u = request.form.get("username", "").strip()
    p = request.form.get("password", "").strip()
    r = request.form.get("role", "writer")
    s = request.form.get("status", "active")
    update_staff(id, u, p if p else None, r, s)
    flash(f"✅ Staff '{u}' updated.", "success")
    return redirect(url_for("staff_list"))


@app.route("/staff/delete/<int:id>")
def staff_delete(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can delete staff.", "warning")
        return redirect(url_for("staff_list"))
    delete_staff(id)
    flash("🗑️ Staff member removed.", "info")
    return redirect(url_for("staff_list"))


@app.route("/submit", methods=["GET", "POST"])
def submit_news():
    if not is_logged_in():
        return redirect(url_for("login"))
    if request.method == "POST":
        language = request.form.get("language", "en").strip().lower()
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        hindi_title = request.form.get("hindi_title", "").strip()
        hindi_content = request.form.get("hindi_content", "").strip()
        category = normalize_category_selection(language, request.form.get("category", "General"))
        title, content, hindi_title, hindi_content = normalize_article_by_category(
            title, content, hindi_title, hindi_content, category
        )
        tags = request.form.get("tags", "").strip()
        image_url = request.form.get("image_url", "").strip()
        file = request.files.get("image_file")
        upload_url = save_upload(file)
        if upload_url:
            image_url = upload_url
        insert_news(title, content, hindi_title, hindi_content, "Manual", category, image_url, tags, get_uname())
        flash("✅ Article submitted for review!", "success")
        return redirect(url_for("dashboard"))
    return render_template(
        "submit_news.html",
        role=get_role(),
        username=get_uname(),
        english_categories=ENGLISH_CATEGORIES,
        hindi_categories=HINDI_CATEGORIES,
    )


@app.route("/news")
def news_site():
    lang = request.args.get("lang", "en")
    category = request.args.get("category", "all")
    theme = get_theme()
    news = get_approved_news()

    # ── Language filter: Hindi lang → sirf Hindi-* categories dikhao
    #                    English lang → sirf non-Hindi categories dikhao
    if lang == "hi":
        news = [n for n in news if is_hindi_category(n.get("category", ""))]
    else:
        news = [n for n in news if not is_hindi_category(n.get("category", ""))]

    # ── Category filter (after language filter)
    if category != "all":
        # Hindi categories: "Hindi-India", "Hindi-Sports" etc. — match by suffix
        if lang == "hi":
            news = [n for n in news if n["category"].replace("Hindi-", "").lower() == category.lower()]
        else:
            news = [n for n in news if n["category"].lower() == category.lower()]

    decorated_news = [decorate_article(item, lang) for item in news]
    decorated_news = [item for item in decorated_news if item["display_title"] and item["display_content"]]
    for item in decorated_news:
        item["display_image_url"] = get_display_image(item)
    top_news = [decorate_article(item, lang) for item in get_top_picks(limit=5)]
    top_news = [item for item in top_news if item["display_title"] and item["display_content"]]
    for item in top_news:
        item["display_image_url"] = get_display_image(item)
    if not top_news:
        top_news = decorated_news[:5]
    # ── Categories list: language-filtered, clean names for display
    all_approved = get_approved_news()
    if lang == "hi":
        lang_news = [n for n in all_approved if is_hindi_category(n.get("category", ""))]
        categories = list(dict.fromkeys(
            n["category"].replace("Hindi-", "") for n in lang_news
        ))
    else:
        lang_news = [n for n in all_approved if not is_hindi_category(n.get("category", ""))]
        categories = list(dict.fromkeys(n["category"] for n in lang_news))
    return render_template(
        "news_site.html",
        news=decorated_news,
        top_news=top_news,
        lang=lang,
        category=category,
        categories=categories,
        theme=theme,
    )


@app.route("/e-paper")
def epaper_page():
    return redirect(url_for("news_site", lang=request.args.get("lang", "en"), theme=get_theme()))


@app.route("/about-us")
def about_page():
    lang = request.args.get("lang", "en")
    theme = get_theme()
    return render_template("info_page.html", page_type="about", lang=lang, theme=theme)


@app.route("/contact-us")
def contact_page():
    lang = request.args.get("lang", "en")
    theme = get_theme()
    return render_template("info_page.html", page_type="contact", lang=lang, theme=theme)


@app.route("/news/<int:id>")
def news_detail(id):
    lang = request.args.get("lang", "en")
    theme = get_theme()
    all_news = get_approved_news()
    article = next((n for n in all_news if n["id"] == id), None)
    if not article:
        return redirect(url_for("news_site"))
    # No redirect — get_display_title/content now fallback across languages
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    country, city = get_location(ip)
    increment_views(id, country, city, ip)
    article = decorate_article(article, lang)
    article["display_image_url"] = get_display_image(article)
    related = [decorate_article(n, lang) for n in all_news if n["category"] == article["category"] and n["id"] != id]
    related = [item for item in related if item["display_title"]][:3]
    for item in related:
        item["display_image_url"] = get_display_image(item)
    comments = get_comments(news_id=id, status="approved")
    return render_template("news_detail.html", article=article, lang=lang, related=related, comments=comments, theme=theme)


@app.route("/news/<int:id>/comment", methods=["POST"])
def submit_comment(id):
    article = get_news_by_id(id)
    if not article or article.get("status") != "approved":
        return redirect(url_for("news_site"))
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    lang = request.form.get("lang", "hi")
    if not name or not message:
        flash("⚠️ Please enter your name and comment.", "warning")
    else:
        add_comment(id, name[:80], message[:1000])
        flash("✅ Comment posted successfully.", "success")
    return redirect(url_for("news_detail", id=id, lang=lang))


@app.route("/comments/approve/<int:id>")
def approve_comment(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can manage comments.", "warning")
        return redirect(url_for("dashboard"))
    update_comment_status(id, "approved")
    flash("✅ Comment approved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/comments/delete/<int:id>")
def remove_comment(id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if not is_admin():
        flash("⚠️ Only admin can manage comments.", "warning")
        return redirect(url_for("dashboard"))
    delete_comment(id)
    flash("🗑️ Comment deleted.", "info")
    return redirect(url_for("dashboard"))


@app.route("/api/news")
def api_news():
    lang = request.args.get("lang", "en")
    news = get_approved_news()
    category = request.args.get("category", "all")
    if category != "all":
        news = [n for n in news if n["category"].lower() == category.lower()]
    decorated = [decorate_article(n, lang) for n in news[:20]]
    decorated = [item for item in decorated if item["display_title"] and item["display_content"]]
    return jsonify(decorated)


if __name__ == "__main__":
    debug_mode = (os.environ.get("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes", "on"})
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=debug_mode,
        use_reloader=debug_mode,
    )
