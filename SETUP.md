# India News — Setup Guide

## ⚡ Quick Start

### Windows
1. Install **Python 3.10+** from python.org
2. Double-click **`START.bat`**
3. Open browser → http://127.0.0.1:8000

### Mac / Linux
```bash
chmod +x START.sh
./START.sh
```

---

## 🔐 Create Admin Account

After the server starts, open a **new terminal** in the same folder:

```bash
# Windows
venv\Scripts\activate
python manage.py createsuperuser

# Mac/Linux
source venv/bin/activate
python manage.py createsuperuser
```

Enter username, email, password → then go to **http://127.0.0.1:8000/admin**

---

## ⚙️ Settings (Admin Panel)

Go to **Admin → System Settings** and fill:

| Setting | Where to get |
|---------|-------------|
| Site Name | Your choice |
| Weather API Key | openweathermap.org (free) |
| Gemini API Key | aistudio.google.com (free) — for AI news |
| Google Analytics | analytics.google.com |

---

## 📰 Adding News

1. Go to **Admin → News → Add News**
2. Fill **Title (Hindi)** — this shows on website
3. Fill **Title (English)** — used for URL slug
4. Set **Status = Published**
5. Choose **Category**
6. Save!

---

## 🗂️ Pages

- **Home** → http://127.0.0.1:8000
- **Admin** → http://127.0.0.1:8000/admin
- **Search** → http://127.0.0.1:8000/search/
- **E-Paper** → http://127.0.0.1:8000/epaper/
- **Videos** → http://127.0.0.1:8000/videos/

---

## 🚀 Production (Render.com — Free Hosting)

1. Push code to GitHub
2. Create account at render.com
3. New Web Service → connect GitHub repo
4. Build Command: `./build.sh`
5. Start Command: `gunicorn indianews.wsgi`
6. Add environment variable: `DEBUG=False`

