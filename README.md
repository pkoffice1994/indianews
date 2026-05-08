India News-Django News Portal

Professional news portal with AI-powered article generation, multilingual support (Hindi/English), and admin panel.

## Features
- 📰 AI News Fetching (Gemini/Claude API)
- 🔤 Bilingual Content (Hindi + English)
- 👥 Staff Management with Roles
- 📄 E-Paper Support
- 🏷️ Categories, Tags, Short News
- 💬 Comments & User Engagement
- 📊 Analytics Dashboard
- ☁️ Weather Integration
- 🌓 Dark/Light Theme

## Setup

### Requirements
- Python 3.10+
- Django 4.2+
- PostgreSQL/MySQL (recommended) or SQLite

### Installation

1. Clone repo:
```bash
git clone https://github.com/yourusername/deshdharti-news.git
cd deshdharti-news
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup database:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Set environment variables (.env):
6. Open browser: `http://localhost:8000`
   Admin: `http://localhost:8000/django-admin/`
   Portal: `http://localhost:8000/portal/login/`

## API Keys

- **Gemini**: [aistudio.google.com](https://aistudio.google.com)
- **Claude/Anthropic**: [console.anthropic.com](https://console.anthropic.com)
- **Weather**: [openweathermap.org](https://openweathermap.org)

## Deployment

Deploy on Render, Railway, PythonAnywhere, AWS, या अपने server पर।

## License
MIT License
