"""
India News — Demo Data Setup
Run: python setup_demo.py
Creates superuser, categories, sample news, and system settings.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'indianews.settings')
django.setup()

from django.contrib.auth.models import User
from news.models import Category, Tag, News, SystemSetting, Page, Role

print("\n🇮🇳  India News — Setup Starting...\n")

# ── SUPERUSER ──────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@indianews.in', 'admin123')
    print("✅ Superuser created: admin / admin123")
else:
    print("ℹ️  Superuser 'admin' already exists")

# ── SYSTEM SETTINGS ────────────────────────────────────────────────────────
s = SystemSetting.get_settings()
s.site_name       = "India News"
s.site_name_hi    = "इंडिया न्यूज़"
s.site_tagline    = "सच की खबर, सबसे पहले"
s.site_tagline_en = "Truth First, Always"
s.weather_city    = "New Delhi,IN"
s.enable_dark_mode = True
s.enable_comments  = True
s.items_per_page   = 12
s.breaking_news_text = "India News पर आपका स्वागत है — देश की सबसे तेज़ खबरें"
s.save()
print("✅ System settings saved")

# ── CATEGORIES ─────────────────────────────────────────────────────────────
CATS = [
    ("देश",      "desh",      "#e60026", True),
    ("राजनीति",  "rajneeti",  "#c0392b", True),
    ("विश्व",    "vishwa",    "#2980b9", True),
    ("खेल",      "khel",      "#27ae60", True),
    ("व्यापार",  "vyapaar",   "#f39c12", True),
    ("तकनीक",    "takneek",   "#8e44ad", True),
    ("मनोरंजन",  "manoranjan","#e67e22", True),
    ("शिक्षा",   "shiksha",   "#16a085", True),
    ("स्वास्थ्य","swasthya",  "#e74c3c", True),
    ("अपराध",    "apradh",    "#2c3e50", False),
]
for name, slug, color, nav in CATS:
    obj, created = Category.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'name_en': slug, 'color': color, 'show_in_nav': nav, 'order': CATS.index((name,slug,color,nav))}
    )
    if created:
        print(f"  📂 Category: {name}")
print("✅ Categories ready")

# ── TAGS ───────────────────────────────────────────────────────────────────
TAGS = ["मोदी", "संसद", "चुनाव", "क्रिकेट", "बॉलीवुड", "शेयर बाज़ार",
        "AI", "सुप्रीम कोर्ट", "रेलवे", "मौसम"]
for t in TAGS:
    from django.utils.text import slugify
    Tag.objects.get_or_create(name=t, defaults={'slug': slugify(t) or t[:20].replace(' ','-')})
print("✅ Tags ready")

# ── SAMPLE NEWS ────────────────────────────────────────────────────────────
admin_user = User.objects.get(username='admin')
desh_cat   = Category.objects.get(slug='desh')
khel_cat   = Category.objects.get(slug='khel')
tech_cat   = Category.objects.get(slug='takneek')

SAMPLE = [
    {
        "title_hi": "नई दिल्ली में G20 समिट की तैयारियां पूरी, विश्व नेता होंगे शामिल",
        "title_en": "G20 Summit preparations complete in New Delhi, world leaders to attend",
        "summary_hi": "भारत की अध्यक्षता में G20 शिखर सम्मेलन नई दिल्ली में आयोजित होगा।",
        "content_hi": """नई दिल्ली में G20 शिखर सम्मेलन की सभी तैयारियां पूरी हो गई हैं। इस बार भारत की अध्यक्षता में यह महत्वपूर्ण आयोजन होने जा रहा है।

विश्व के 20 प्रमुख देशों के नेता इस सम्मेलन में भाग लेंगे। अमेरिका, रूस, चीन, ब्रिटेन सहित कई देशों के राष्ट्राध्यक्ष भारत आएंगे।

प्रधानमंत्री ने कहा कि यह भारत के लिए गर्व का अवसर है। देश की राजधानी को विशेष रूप से सजाया गया है।

सुरक्षा के कड़े इंतजाम किए गए हैं। हजारों पुलिसकर्मी और सुरक्षाकर्मी तैनात हैं।

इस सम्मेलन में जलवायु परिवर्तन, आर्थिक विकास और वैश्विक शांति जैसे महत्वपूर्ण विषयों पर चर्चा होगी।""",
        "category": desh_cat, "is_breaking": True, "is_featured": True, "is_top_story": True,
        "featured_image_url": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=80",
    },
    {
        "title_hi": "भारत ने ऑस्ट्रेलिया को हराकर टेस्ट सीरीज़ जीती, विराट ने शतक लगाया",
        "title_en": "India beats Australia to win Test series, Virat hits century",
        "summary_hi": "भारतीय क्रिकेट टीम ने शानदार प्रदर्शन करते हुए ऑस्ट्रेलिया को हराया।",
        "content_hi": """भारतीय क्रिकेट टीम ने ऐतिहासिक जीत दर्ज की है। ऑस्ट्रेलिया के खिलाफ टेस्ट सीरीज़ में भारत ने 3-1 से जीत हासिल की।

विराट कोहली ने अंतिम टेस्ट मैच में शानदार शतक लगाया। उन्होंने 108 रन की पारी खेली।

रोहित शर्मा की कप्तानी में टीम ने बेहतरीन प्रदर्शन किया। गेंदबाज़ी में जसप्रीत बुमराह ने 15 विकेट लिए।

यह जीत भारतीय क्रिकेट के लिए बेहद महत्वपूर्ण है। ICC रैंकिंग में भारत शीर्ष स्थान पर पहुंच गया है।

करोड़ों भारतीय प्रशंसकों ने इस जीत का जश्न मनाया।""",
        "category": khel_cat, "is_breaking": False, "is_featured": True,
        "featured_image_url": "https://images.unsplash.com/photo-1540747913346-19212a4cf528?w=1200&q=80",
    },
    {
        "title_hi": "AI तकनीक से बदल रहा है भारत का शिक्षा क्षेत्र, लाखों छात्रों को फायदा",
        "title_en": "AI technology transforming India's education sector, millions of students benefit",
        "summary_hi": "आर्टिफिशियल इंटेलिजेंस की मदद से भारत में शिक्षा का नया युग शुरू हो रहा है।",
        "content_hi": """भारत में आर्टिफिशियल इंटेलिजेंस तकनीक शिक्षा के क्षेत्र में क्रांति ला रही है। देश भर के लाखों छात्र इस नई तकनीक का लाभ उठा रहे हैं।

सरकार ने 'AI for Education' कार्यक्रम शुरू किया है। इसके तहत सरकारी स्कूलों में भी AI आधारित शिक्षण सामग्री उपलब्ध कराई जाएगी।

IIT और IIM जैसे प्रतिष्ठित संस्थानों में पहले से ही AI का उपयोग हो रहा है। अब इसे प्राथमिक और माध्यमिक शिक्षा में भी लागू किया जा रहा है।

ग्रामीण क्षेत्रों में भी इस तकनीक को पहुंचाने की योजना है। मोबाइल आधारित AI एप्लिकेशन के माध्यम से दूरदराज़ के छात्रों को शिक्षा मिलेगी।

विशेषज्ञों का मानना है कि यह पहल भारत को शिक्षा के क्षेत्र में विश्व में अग्रणी बनाएगी।""",
        "category": tech_cat, "is_breaking": False, "is_featured": True,
        "featured_image_url": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200&q=80",
    },
    {
        "title_hi": "संसद में बजट पेश, मध्यम वर्ग को मिली बड़ी राहत",
        "title_en": "Budget presented in Parliament, major relief for middle class",
        "summary_hi": "वित्त मंत्री ने संसद में आम बजट पेश किया। मध्यम वर्ग के लिए कर में छूट की घोषणा।",
        "content_hi": """वित्त मंत्री ने आज संसद में आम बजट 2024-25 पेश किया। इस बजट में मध्यम वर्ग को बड़ी राहत दी गई है।

आयकर की सीमा बढ़ाकर 7 लाख रुपये कर दी गई है। इससे करोड़ों करदाताओं को सीधा फायदा होगा।

कृषि क्षेत्र के लिए विशेष पैकेज की घोषणा की गई है। किसानों को सस्ती ऋण सुविधा मिलेगी।

स्वास्थ्य और शिक्षा पर खर्च बढ़ाया गया है। बुनियादी ढांचे के विकास के लिए बड़ा आवंटन किया गया।

विपक्ष ने बजट को चुनावी बजट बताया है। सरकार ने इसे विकास का बजट कहा है।""",
        "category": desh_cat, "is_breaking": True,
        "featured_image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
    },
    {
        "title_hi": "चंद्रयान-4 मिशन की घोषणा, ISRO ने रखी अंतरिक्ष की नई योजनाएं",
        "title_en": "Chandrayaan-4 mission announced, ISRO unveils new space plans",
        "summary_hi": "भारतीय अंतरिक्ष एजेंसी ISRO ने चंद्रयान-4 समेत कई महत्वाकांक्षी योजनाएं घोषित कीं।",
        "content_hi": """भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने चंद्रयान-4 मिशन की आधिकारिक घोषणा की है।

इस मिशन में चंद्रमा की सतह से नमूने लाए जाएंगे। यह भारत का पहला sample return mission होगा।

ISRO प्रमुख ने बताया कि 2025 तक यह मिशन लॉन्च होगा। इसमें नई तकनीक का उपयोग किया जाएगा।

चंद्रयान-3 की सफलता के बाद भारत अंतरिक्ष में नई ऊंचाइयां छू रहा है। मंगलयान-2 की भी तैयारी चल रही है।

अंतर्राष्ट्रीय समुदाय ने भारत के इस कदम की सराहना की है।""",
        "category": tech_cat,
        "featured_image_url": "https://images.unsplash.com/photo-1517976487492-5750f3195933?w=1200&q=80",
    },
    {
        "title_hi": "नए साल में शेयर बाज़ार ने लगाई छलांग, सेंसेक्स 75000 के पार",
        "title_en": "Stock market surges in new year, Sensex crosses 75000",
        "summary_hi": "भारतीय शेयर बाज़ार में जबरदस्त उछाल, सेंसेक्स ने नई ऊंचाई छुई।",
        "content_hi": """भारतीय शेयर बाज़ार में जबरदस्त तेज़ी आई है। BSE सेंसेक्स पहली बार 75,000 अंकों के पार पहुंचा।

निफ्टी 50 भी 22,500 के स्तर को पार कर गया। आईटी, बैंकिंग और फार्मा शेयरों में सबसे ज़्यादा तेज़ी रही।

विदेशी निवेशकों ने भारतीय बाज़ार में भारी निवेश किया। FII ने एक दिन में 8000 करोड़ रुपये से ज़्यादा की खरीदारी की।

आर्थिक विशेषज्ञों का मानना है कि भारतीय अर्थव्यवस्था मज़बूत दिशा में आगे बढ़ रही है।

छोटे निवेशकों को सतर्क रहने की सलाह दी गई है।""",
        "category": Category.objects.get(slug='vyapaar'),
        "featured_image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
    },
]

for i, item in enumerate(SAMPLE):
    from django.utils.text import slugify
    slug = slugify(item['title_en'][:80]) or f"news-{i+1}"
    if not News.objects.filter(slug=slug).exists():
        n = News.objects.create(
            title_hi=item['title_hi'],
            title_en=item['title_en'],
            summary_hi=item['summary_hi'],
            content_hi=item['content_hi'],
            category=item['category'],
            author=admin_user,
            status='published',
            is_breaking=item.get('is_breaking', False),
            is_featured=item.get('is_featured', False),
            is_top_story=item.get('is_top_story', False),
            featured_image_url=item.get('featured_image_url', ''),
            slug=slug,
        )
        print(f"  📰 News: {item['title_hi'][:50]}...")
print("✅ Sample news created")

# ── PAGES ──────────────────────────────────────────────────────────────────
PAGES = [
    ("About Us", "about-us", "<h2>India News के बारे में</h2><p>India News भारत का एक प्रमुख डिजिटल समाचार पोर्टल है। हम सच्ची और निष्पक्ष खबरें देने के लिए प्रतिबद्ध हैं।</p><p>हमारी टीम अनुभवी पत्रकारों से मिलकर बनी है जो 24/7 आपको देश-दुनिया की खबरें पहुंचाते हैं।</p>"),
    ("Contact Us", "contact-us", "<h2>संपर्क करें</h2><p>Email: contact@indianews.in</p><p>Phone: +91-XXXXXXXXXX</p><p>Address: नई दिल्ली, भारत</p>"),
    ("Privacy Policy", "privacy-policy", "<h2>Privacy Policy</h2><p>India News आपकी निजी जानकारी की सुरक्षा को सर्वोच्च प्राथमिकता देता है।</p>"),
    ("Disclaimer", "disclaimer", "<h2>Disclaimer</h2><p>India News पर प्रकाशित सभी समाचार तथ्यों पर आधारित हैं।</p>"),
]
for title, slug, content in PAGES:
    Page.objects.get_or_create(slug=slug, defaults={'title': title, 'content': content, 'is_active': True, 'show_in_footer': True})
print("✅ Pages created")

# ── ROLES ──────────────────────────────────────────────────────────────────
Role.objects.get_or_create(name="Editor",  defaults={'can_create':True,'can_edit':True,'can_delete':False,'can_publish':True,'can_manage_staff':False})
Role.objects.get_or_create(name="Writer",  defaults={'can_create':True,'can_edit':True,'can_delete':False,'can_publish':False,'can_manage_staff':False})
Role.objects.get_or_create(name="Admin",   defaults={'can_create':True,'can_edit':True,'can_delete':True,'can_publish':True,'can_manage_staff':True})
print("✅ Roles created")

print("""
╔══════════════════════════════════════════════════════╗
║        🇮🇳  INDIA NEWS — SETUP COMPLETE!  🇮🇳          ║
╠══════════════════════════════════════════════════════╣
║  Admin URL  :  http://127.0.0.1:8000/admin/          ║
║  Username   :  admin                                 ║
║  Password   :  admin123                              ║
╠══════════════════════════════════════════════════════╣
║  Website    :  http://127.0.0.1:8000/                ║
╚══════════════════════════════════════════════════════╝
""")
