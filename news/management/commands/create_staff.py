"""
Management command: python manage.py create_staff
Creates a staff user for client with limited permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create a staff user for client'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='editor', help='Username')
        parser.add_argument('--password', default='IndiaNews@2026', help='Password')
        parser.add_argument('--email', default='editor@indianews.in', help='Email')
        parser.add_argument('--name', default='Editor', help='Full name')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email    = options['email']
        name     = options['name']

        # Create or update user
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.email      = email
        user.first_name = name
        user.is_staff   = True
        user.is_superuser = False
        user.save()

        # Give permissions for news management only
        from news.models import (News, Category, ShortNews, EPaper,
                                  Tag, AdSpace, AdBooking, SystemSetting)

        allowed_models = [News, Category, ShortNews, EPaper, Tag, AdSpace, AdBooking]

        for model in allowed_models:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            for perm in perms:
                user.user_permissions.add(perm)

        # View only for SystemSetting
        ct = ContentType.objects.get_for_model(SystemSetting)
        view_perm = Permission.objects.filter(content_type=ct, codename__startswith='view')
        for p in view_perm:
            user.user_permissions.add(p)

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'''
✅ {action} Staff Account:
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Admin URL : https://indianews-581a.onrender.com/admin/
👤 Username  : {username}
🔑 Password  : {password}
📧 Email     : {email}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Permissions  : News, Categories, Short News, E-Paper, Tags, Ads
Cannot       : Delete users, change site settings, access server
'''))
