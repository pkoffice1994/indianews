# 🇮🇳 India News — Bilingual News Portal

> **Hindi + English** news website built with Django — deploy-ready on Render.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?style=flat-square&logo=django)
![Deploy](https://img.shields.io/badge/Deploy-Render-purple?style=flat-square)

---

## 📸 Features

| Feature | Details |
|--------|---------|
| 🌐 Bilingual | Hindi + English toggle on every page |
| 📱 Mobile First | Aaj Tak style responsive layout |
| 🔴 Breaking News | Live ticker with auto-scroll |
| 📹 Short Videos | YouTube embed + direct MP4 upload |
| 📰 E-Paper | Upload daily newspaper PDF |
| 💰 Ad System | Google AdSense + Direct client booking |
| 📊 Dashboard | Live stats — views, articles, traffic |
| 🔍 SEO Ready | Meta tags, slugs, Open Graph |
| 🌙 Dark Mode | Toggle light/dark theme |
| 👨‍💼 Admin Panel | Jazzmin-powered beautiful admin |

---

## 🛠️ Tech Stack

- **Backend** — Django 4.2, Python 3.11
- **Database** — SQLite (dev) / PostgreSQL (prod)
- **Admin** — Django Jazzmin
- **Deployment** — Render.com
- **Static files** — WhiteNoise

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/pkoffice1994/indianews.git
cd indianews

# 2. Virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install
pip install -r requirements.txt

# 4. Setup
python manage.py migrate --run-syncdb
python setup_demo.py
python manage.py add_news

# 5. Run
python manage.py runserver
```

Open → **http://127.0.0.1:8000**

---

## 🔐 Default Login

| | |
|--|--|
| URL | `/admin/` |
| Username | `admin` |
| Password | `admin123` |

> ⚠️ Change password immediately in production!

---

## ☁️ Deploy on Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect GitHub repo
4. Set:
   - **Build Command:** `./build.sh`
   - **Start Command:** `bash start.sh`
5. Add env var: `SECRET_KEY` → auto-generate
6. Click Deploy!

---

## 📁 Project Structure

```
indianews/
├── news/               # Main app (models, views, admin)
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── management/commands/add_news.py
├── templates/
│   ├── base.html
│   └── news/
│       ├── home.html
│       ├── detail.html
│       ├── dashboard.html
│       └── advertise.html
├── static/
├── build.sh            # Render build
├── start.sh            # Render start
└── requirements.txt
```

---

## 📋 Admin Panel

| Section | What you can do |
|---------|-----------------|
| News | Add/edit articles (Hindi + English) |
| Short News | Add short news + YouTube/MP4 videos |
| Ad Spaces | Manage live advertisements |
| Ad Bookings | Approve client ad requests |
| E-Paper | Upload daily newspaper |
| Settings | Site name, logo, social links |

---

## 💰 Ad Sizes

| Position | Size | Slot |
|----------|------|------|
| Header | 728×90 | `header` |
| Home Top | 970×90 | `home_top` |
| Sidebar Top | 300×250 | `sidebar_top` |
| Sidebar Bottom | 300×600 | `sidebar_bottom` |
| Article Mid | 336×280 | `in_content` |
| Footer | 728×90 | `footer` |

---

## 🌐 Key URLs

| Page | URL |
|------|-----|
| Homepage | `/` |
| Category | `/category/{slug}/` |
| Videos | `/videos/` |
| E-Paper | `/epaper/` |
| Advertise | `/advertise/` |
| Dashboard | `/dashboard/` |
| Admin | `/admin/` |

---

## 📄 License

MIT License — free to use and modify.

**Live Demo:** [indianews-581a.onrender.com](https://indianews-581a.onrender.com)

---

<div align="center"><strong>⭐ Star this repo if it helped you!</strong></div>
