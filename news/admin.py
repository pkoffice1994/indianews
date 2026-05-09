from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Category, SubCategory, Tag, News, ShortNews, EPaper,
    FeaturedSection, AdSpace, SiteUser, Comment, CommentFlag,
    Page, Role, StaffMember, SystemSetting, AdBooking
)

admin.site.site_header  = "India News — Admin Panel"
admin.site.site_title   = "India News"
admin.site.index_title  = "Content Management · India News"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('dot', 'name', 'name_en', 'slug', 'news_count', 'show_in_nav', 'is_active', 'order')
    list_editable = ('order', 'is_active', 'show_in_nav')
    prepopulated_fields = {'slug': ('name_en',)}
    search_fields = ('name', 'name_en')
    ordering = ('order',)

    def dot(self, obj):
        return format_html('<span style="display:inline-block;width:13px;height:13px;border-radius:50%;background:{};vertical-align:middle"></span>', obj.color)
    dot.short_description = ''

    def news_count(self, obj):
        return format_html('<b>{}</b>', obj.news.filter(status='published').count())
    news_count.short_description = 'Published'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'news_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def news_count(self, obj):
        count = obj.news.filter(status='published').count()
        return format_html('<span style="color:#e60026;font-weight:600">{}</span> articles', count)
    news_count.short_description = 'Published Articles'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display   = ('thumb', 'title_short', 'category', 'status_badge', 'author',
                      'is_breaking', 'is_featured', 'views_fmt', 'published_at')
    list_display_links = ('thumb', 'title_short')
    list_filter    = ('status', 'category', 'is_breaking', 'is_featured',
                      ('published_at', admin.DateFieldListFilter))
    search_fields  = ('title_hi', 'title_en', 'content_hi')
    list_editable  = ('is_breaking', 'is_featured')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    readonly_fields = ('views', 'read_time', 'uuid', 'created_at', 'updated_at', 'slug_preview')
    actions = ['action_publish', 'action_reject', 'action_breaking_on', 'action_breaking_off']
    list_per_page = 25

    fieldsets = (
        ('Hindi Content', {
            'fields': ('title_hi', 'summary_hi', 'content_hi'),
        }),
        ('English Content', {
            'fields': ('title_en', 'summary_en', 'content_en'),
            'classes': ('collapse',),
        }),
        ('Classification', {
            'fields': ('category', 'subcategory', 'tags', 'slug', 'slug_preview', 'location'),
            'description': 'Slug is auto-generated from Title (Hindi). You can edit it manually if needed.'
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_url', 'image_caption', 'video_url', 'is_video_news'),
        }),
        ('Publishing', {
            'fields': ('author', 'status', 'is_breaking', 'is_featured', 'is_top_story', 'allow_comments', 'published_at'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Info', {
            'fields': ('uuid', 'views', 'read_time', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = ('admin/js/news_autoslug.js',)

    def slug_preview(self, obj):
        if obj.slug:
            return format_html(
                '<span style="color:#888;font-size:12px;font-family:monospace">'
                'URL: /{}/ &nbsp; <a href="/{}" target="_blank" style="color:#e60026">Preview ↗</a>'
                '</span>', obj.slug, obj.slug)
        return format_html('<span style="color:#aaa;font-size:12px">Will be auto-generated from Title (Hindi)</span>')
    slug_preview.short_description = 'URL Preview'

    def thumb(self, obj):
        url = obj.get_image()
        if url:
            return format_html('<img src="{}" style="width:64px;height:48px;object-fit:cover;border-radius:4px">', url)
        return '—'
    thumb.short_description = ''

    def title_short(self, obj):
        b = ' 🔴' if obj.is_breaking else ''
        f = ' ⭐' if obj.is_featured else ''
        return format_html('<b>{}</b>{}{}', obj.title_hi[:65], b, f)
    title_short.short_description = 'Headline'

    def status_badge(self, obj):
        colors = {'published':'#28a745','draft':'#6c757d','pending':'#ffc107','rejected':'#dc3545'}
        c = colors.get(obj.status, '#aaa')
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700">{}</span>', c, obj.status.upper())
    status_badge.short_description = 'Status'

    def views_fmt(self, obj):
        return format_html('<span style="color:#888">{}</span>', f'{obj.views:,}')
    views_fmt.short_description = 'Views'

    def action_publish(self, request, queryset):
        n = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'✅ {n} articles published!')
    action_publish.short_description = '✅ Publish selected'

    def action_reject(self, request, queryset):
        n = queryset.update(status='rejected')
        self.message_user(request, f'🚫 {n} articles rejected.')
    action_reject.short_description = '🚫 Reject selected'

    def action_breaking_on(self, request, queryset):
        queryset.update(is_breaking=True)
        self.message_user(request, '🔴 Breaking tag added.')
    action_breaking_on.short_description = '🔴 Mark as Breaking'

    def action_breaking_off(self, request, queryset):
        queryset.update(is_breaking=False)
        self.message_user(request, 'Breaking tag removed.')
    action_breaking_off.short_description = 'Remove Breaking tag'

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ShortNews)
class ShortNewsAdmin(admin.ModelAdmin):
    list_display  = ('title', 'news_type', 'has_video_display', 'category', 'views', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter   = ('news_type', 'is_active', 'category')
    search_fields = ('title', 'content')
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'news_type', 'category', 'is_active', 'order')
        }),
        ('Thumbnail Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload a thumbnail image OR provide an image URL.'
        }),
        ('Video', {
            'fields': ('video_file', 'video_url'),
            'description': 'Upload an MP4 video file OR paste a YouTube / direct video URL. YouTube thumbnails are auto-fetched.'
        }),
    )

    def has_video_display(self, obj):
        if obj.has_video:
            if obj.is_youtube:
                return format_html('<span style="color:red;font-weight:600">▶ YouTube</span>')
            elif obj.video_file:
                return format_html('<span style="color:green;font-weight:600">▶ Uploaded</span>')
            else:
                return format_html('<span style="color:blue;font-weight:600">▶ URL</span>')
        return format_html('<span style="color:#aaa">— Text</span>')
    has_video_display.short_description = 'Video'


@admin.register(EPaper)
class EPaperAdmin(admin.ModelAdmin):
    list_display  = ('title', 'edition', 'publish_date', 'is_active')
    list_editable = ('is_active',)
    date_hierarchy = 'publish_date'


@admin.register(FeaturedSection)
class FeaturedSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'section_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    filter_horizontal = ('news',)


@admin.register(AdSpace)
class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'impressions', 'clicks')
    list_editable = ('is_active',)
    readonly_fields = ('impressions', 'clicks')


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'news', 'short_content', 'is_approved', 'flags_count', 'created_at')
    list_editable = ('is_approved',)
    list_filter   = ('is_approved',)
    actions       = ['approve', 'reject']

    def short_content(self, obj): return obj.content[:60]
    short_content.short_description = 'Comment'

    def flags_count(self, obj):
        n = obj.flags.count()
        return format_html('<span style="color:red;font-weight:700">⚑ {}</span>', n) if n else '0'
    flags_count.short_description = 'Flags'

    def approve(self, req, qs): qs.update(is_approved=True)
    approve.short_description = '✅ Approve'

    def reject(self, req, qs): qs.update(is_approved=False)
    reject.short_description = '🚫 Reject'


@admin.register(CommentFlag)
class CommentFlagAdmin(admin.ModelAdmin):
    list_display = ('comment', 'reason', 'user', 'created_at')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'slug', 'is_active', 'show_in_footer')
    list_editable = ('is_active', 'show_in_footer')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'can_create', 'can_edit', 'can_delete', 'can_publish', 'can_manage_staff')
    list_editable = ('can_create', 'can_edit', 'can_delete', 'can_publish', 'can_manage_staff')


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display  = ('display_name', 'user', 'role', 'status', 'joined_at')
    list_editable = ('status',)
    list_filter   = ('role', 'status')


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Branding', {
            'fields': ('site_name', 'site_name_hi', 'site_tagline', 'site_tagline_en', 'site_url', 'logo', 'favicon'),
        }),
        ('Contact Info', {
            'fields': ('email', 'phone', 'address', 'whatsapp_number'),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'youtube_url', 'instagram_url', 'telegram_url'),
        }),
        ('API Keys', {
            'fields': ('weather_city', 'openweather_key', 'gemini_api_key'),
            'description': 'Get free keys from openweathermap.org and aistudio.google.com',
        }),
        ('Analytics & Scripts', {
            'fields': ('google_analytics', 'header_scripts', 'footer_scripts'),
            'classes': ('collapse',),
        }),
        ('Features', {
            'fields': ('enable_dark_mode', 'enable_comments', 'items_per_page', 'breaking_news_text'),
        }),
    )

    def has_add_permission(self, request):
        return not SystemSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AdBooking)
class AdBookingAdmin(admin.ModelAdmin):
    list_display  = ('client_name','client_phone','company_name','position','duration_days','total_price','status','created_at')
    list_filter   = ('status','position')
    search_fields = ('client_name','client_email','client_phone','company_name')
    list_editable = ('status',)
    readonly_fields = ('created_at','updated_at','impressions_count')
    fieldsets = (
        ('Client Info', {'fields': ('client_name','client_email','client_phone','company_name')}),
        ('Ad Details',  {'fields': ('position','duration_days','banner_image','banner_url','website_url','ad_title','message','total_price')}),
        ('Status',      {'fields': ('status','admin_note','start_date','end_date')}),
        ('Timestamps',  {'fields': ('created_at','updated_at')}),
    )
    actions = ['approve_and_activate', 'reject_booking']

    def impressions_count(self, obj): return '—'
    impressions_count.short_description = 'Impressions'

    def approve_and_activate(self, request, queryset):
        from django.utils import timezone
        import datetime
        for booking in queryset:
            # Create actual AdSpace when approved
            from .models import AdSpace
            AdSpace.objects.create(
                name=f"{booking.client_name} — {booking.get_position_display()}",
                position=booking.position,
                image_url=booking.banner_url,
                link_url=booking.website_url,
                is_active=True,
                starts_at=timezone.now(),
                ends_at=timezone.now() + datetime.timedelta(days=booking.duration_days),
            )
            booking.status = 'active'
            booking.save()
        self.message_user(request, f'{queryset.count()} bookings approved and ads activated!')
    approve_and_activate.short_description = '✅ Approve & Activate Ad'

    def reject_booking(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} bookings rejected.')
    reject_booking.short_description = '❌ Reject Booking'
