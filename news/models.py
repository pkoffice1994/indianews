from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid


class Category(models.Model):
    name        = models.CharField("नाम (Hindi)", max_length=100)
    name_en     = models.CharField("Name (English)", max_length=100, blank=True)
    slug        = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, blank=True)
    color       = models.CharField(max_length=10, default="#e60026")
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    show_in_nav = models.BooleanField("Nav में दिखाएं", default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category  = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name      = models.CharField(max_length=100)
    name_en   = models.CharField(max_length=100, blank=True)
    slug      = models.SlugField(unique=True, max_length=120)
    order     = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SubCategory"
        verbose_name_plural = "SubCategories"
        ordering = ['order', 'name']

    def __str__(self): return f"{self.category.name} › {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name  = models.CharField(max_length=80, unique=True)
    slug  = models.SlugField(unique=True, max_length=100)
    color = models.CharField(max_length=10, default="#555555")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class News(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('pending',   'Pending Review'),
        ('published', 'Published'),
        ('rejected',  'Rejected'),
    ]
    uuid        = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug        = models.SlugField(unique=True, max_length=250)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='news')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='news')
    tags        = models.ManyToManyField(Tag, blank=True, related_name='news')

    title_hi    = models.CharField("शीर्षक (Hindi)*", max_length=500)
    summary_hi  = models.TextField("सारांश (Hindi)", blank=True)
    content_hi  = models.TextField("सामग्री (Hindi)*")
    title_en    = models.CharField("Title (English)", max_length=500, blank=True)
    summary_en  = models.TextField("Summary (English)", blank=True)
    content_en  = models.TextField("Content (English)", blank=True)

    featured_image     = models.ImageField("तस्वीर", upload_to='news/%Y/%m/', blank=True, null=True)
    featured_image_url = models.URLField("तस्वीर URL", blank=True)
    image_caption      = models.CharField(max_length=300, blank=True)
    video_url          = models.URLField("Video URL", blank=True)
    is_video_news      = models.BooleanField("Video News?", default=False)

    meta_title       = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    author       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='news')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_breaking  = models.BooleanField("Breaking News?", default=False)
    is_featured  = models.BooleanField("Featured?", default=False)
    is_top_story = models.BooleanField("Top Story?", default=False)
    allow_comments = models.BooleanField(default=True)
    views        = models.PositiveIntegerField(default=0)
    read_time    = models.PositiveIntegerField(default=1)
    location     = models.CharField(max_length=100, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-published_at', '-created_at']

    def __str__(self): return self.title_hi[:80]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_hi[:80])
            self.slug = base or str(self.uuid)[:8]
            # ensure uniqueness
            orig = self.slug
            n = 1
            while News.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{orig}-{n}"
                n += 1
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        self.read_time = max(1, len(self.content_hi.split()) // 200)
        super().save(*args, **kwargs)

    def get_image(self):
        if self.featured_image:
            return self.featured_image.url
        return self.featured_image_url or 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80'


class ShortNews(models.Model):
    title      = models.CharField("शीर्षक", max_length=300)
    content    = models.TextField(blank=True)
    image_url  = models.URLField(blank=True)
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Short News"
        verbose_name_plural = "Short News"
        ordering = ['-created_at']

    def __str__(self): return self.title[:60]


class EPaper(models.Model):
    title        = models.CharField(max_length=200)
    edition      = models.CharField(max_length=100, blank=True)
    pdf_file     = models.FileField(upload_to='epaper/%Y/%m/', blank=True, null=True)
    pdf_url      = models.URLField(blank=True)
    thumbnail    = models.ImageField(upload_to='epaper/thumb/', blank=True, null=True)
    publish_date = models.DateField()
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ePaper"
        verbose_name_plural = "ePaper"
        ordering = ['-publish_date']

    def __str__(self): return f"{self.title} — {self.publish_date}"


class FeaturedSection(models.Model):
    TYPES = [
        ('top_stories', 'Top Stories'), ('editors_pick', "Editor's Pick"),
        ('trending', 'Trending'), ('must_read', 'Must Read'),
        ('video', 'Video'), ('custom', 'Custom'),
    ]
    name         = models.CharField(max_length=100)
    section_type = models.CharField(max_length=30, choices=TYPES, default='custom')
    news         = models.ManyToManyField(News, related_name='featured_in', blank=True)
    order        = models.PositiveIntegerField(default=0)
    is_active    = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Featured Section"
        verbose_name_plural = "Featured Sections"
        ordering = ['order']

    def __str__(self): return self.name


class AdSpace(models.Model):
    POSITIONS = [
        ('header', 'Header'), ('footer', 'Footer'),
        ('sidebar_top', 'Sidebar Top'), ('sidebar_bottom', 'Sidebar Bottom'),
        ('in_content', 'In-Content'), ('home_top', 'Home Top'),
        ('between_news', 'Between News'),
    ]
    name       = models.CharField(max_length=100)
    position   = models.CharField(max_length=30, choices=POSITIONS)
    image      = models.ImageField(upload_to='ads/', blank=True, null=True)
    image_url  = models.URLField(blank=True)
    link_url   = models.URLField(blank=True)
    html_code  = models.TextField("AdSense/HTML Code", blank=True)
    is_active  = models.BooleanField(default=True)
    starts_at  = models.DateTimeField("Start Date (optional)", null=True, blank=True)
    ends_at    = models.DateTimeField("End Date (optional)", null=True, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks     = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ad Space"
        verbose_name_plural = "Ad Spaces"

    def __str__(self): return f"{self.name} ({self.get_position_display()})"


class SiteUser(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone       = models.CharField(max_length=15, blank=True)
    bio         = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Site User"
        verbose_name_plural = "Site Users"

    def __str__(self): return self.user.username


class Comment(models.Model):
    news       = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name       = models.CharField(max_length=100, blank=True)
    email      = models.EmailField(blank=True)
    content    = models.TextField()
    is_approved = models.BooleanField(default=False)
    parent     = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_at']

    def __str__(self): return f"{self.name}: {self.content[:50]}"


class CommentFlag(models.Model):
    REASONS = [('spam','Spam'), ('offensive','Offensive'), ('fake','Fake News'), ('other','Other')]
    comment    = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='flags')
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason     = models.CharField(max_length=20, choices=REASONS, default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment Flag"
        verbose_name_plural = "Comment Flags"

    def __str__(self): return f"Flag #{self.comment_id}"


class Page(models.Model):
    title          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True, max_length=200)
    content        = models.TextField("Content (HTML supported)")
    meta_description = models.CharField(max_length=500, blank=True)
    is_active      = models.BooleanField(default=True)
    show_in_footer = models.BooleanField("Footer में दिखाएं", default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self): return self.title


class Role(models.Model):
    name             = models.CharField(max_length=100, unique=True)
    can_create       = models.BooleanField(default=True)
    can_edit         = models.BooleanField(default=True)
    can_delete       = models.BooleanField(default=False)
    can_publish      = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self): return self.name


class StaffMember(models.Model):
    STATUS = [('active', 'Active'), ('inactive', 'Inactive')]
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role         = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    display_name = models.CharField(max_length=100, blank=True)
    phone        = models.CharField(max_length=15, blank=True)
    avatar       = models.ImageField(upload_to='staff/', blank=True, null=True)
    bio          = models.TextField(blank=True)
    status       = models.CharField(max_length=10, choices=STATUS, default='active')
    joined_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Management"

    def __str__(self): return self.display_name or self.user.username


class SystemSetting(models.Model):
    # Branding
    site_name     = models.CharField(max_length=100, default="India News")
    site_name_hi  = models.CharField("Site Name Hindi", max_length=100, default="इंडिया न्यूज़")
    site_tagline  = models.CharField(max_length=200, default="सच की खबर, सबसे पहले")
    site_tagline_en = models.CharField(max_length=200, default="Truth First, Always")
    site_url      = models.URLField(default="https://indianews.in")
    logo          = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon       = models.ImageField(upload_to='site/', blank=True, null=True)

    # Contact
    email         = models.EmailField(blank=True)
    phone         = models.CharField(max_length=20, blank=True)
    address       = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)

    # Social
    facebook_url  = models.URLField(blank=True)
    twitter_url   = models.URLField(blank=True)
    youtube_url   = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    telegram_url  = models.URLField(blank=True)

    # API Keys
    weather_city    = models.CharField(max_length=100, default="New Delhi,IN")
    openweather_key = models.CharField(max_length=100, blank=True, help_text="openweathermap.org — Free key")
    gemini_api_key  = models.CharField(max_length=200, blank=True, help_text="Google AI Studio — Free key")

    # Scripts
    google_analytics = models.TextField(blank=True)
    header_scripts   = models.TextField(blank=True)
    footer_scripts   = models.TextField(blank=True)

    # Features
    enable_dark_mode   = models.BooleanField(default=True)
    enable_comments    = models.BooleanField(default=True)
    items_per_page     = models.PositiveIntegerField(default=12)
    breaking_news_text = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "⚙ System Settings"

    def __str__(self): return "India News — System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
