from django.contrib import admin
from .models import Profile, Skill, Project, Certification, Experience, ContactMessage, Education

# Other models
# admin.site.register(Profile)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Project)
admin.site.register(Experience)
admin.site.register(ContactMessage)

# Certification Admin
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'issuer',
        'issue_date_month',
        'issue_date_year',
        'expiration_date_month',
        'expiration_date_year',
        'credential_id',
        'credential_url',
    )
    search_fields = ('name', 'issuer')
    list_filter = ('issuer', 'issue_date_year', 'expiration_date_year')


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1  # Show one empty form by default

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [EducationInline]
    list_display = ['name', 'title', 'email']



# FIXED admin.py - Replace your existing admin code

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from datetime import timedelta
from .models import (
    VisitorCount, VisitorSession, DailyVisitorStats, 
    PopularPage, VisitorGeolocation
)

@admin.register(VisitorCount)
class VisitorCountAdmin(admin.ModelAdmin):
    list_display = ['count', 'last_updated', 'formatted_count']
    readonly_fields = ['count', 'last_updated']
    
    def formatted_count(self, obj):
        # FIXED: Remove the comma from the format string
        return format_html(
            '<strong style="color: #0066cc; font-size: 16px;">{}</strong>',
            f"{obj.count:,}"
        )
    formatted_count.short_description = 'Total Visitors'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_display', 'ip_address', 'location_display', 
        'page_views', 'is_returning', 'first_visit', 'duration'
    ]
    list_filter = [
        'is_returning', 'first_visit', 'country', 'city'
    ]
    search_fields = ['ip_address', 'session_id', 'user_agent', 'country', 'city']
    readonly_fields = [
        'session_id', 'ip_address', 'user_agent', 'referrer',
        'first_visit', 'last_visit'
    ]
    
    def session_display(self, obj):
        return f"{obj.session_id[:12]}..."
    session_display.short_description = 'Session ID'
    
    def location_display(self, obj):
        if obj.city and obj.country:
            return f"{obj.city}, {obj.country}"
        elif obj.country:
            return obj.country
        return "Unknown"
    location_display.short_description = 'Location'
    
    def duration(self, obj):
        if obj.first_visit and obj.last_visit:
            delta = obj.last_visit - obj.first_visit
            if delta.total_seconds() < 60:
                return f"{int(delta.total_seconds())}s"
            elif delta.total_seconds() < 3600:
                return f"{int(delta.total_seconds() / 60)}m"
            else:
                return f"{delta.total_seconds() / 3600:.1f}h"
        return "0s"
    duration.short_description = 'Session Duration'

@admin.register(DailyVisitorStats)
class DailyVisitorStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'unique_visitors', 'total_page_views', 
        'new_visitors', 'returning_visitors', 'growth_rate'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def growth_rate(self, obj):
        try:
            previous_day = DailyVisitorStats.objects.filter(
                date=obj.date - timedelta(days=1)
            ).first()
            if previous_day and previous_day.unique_visitors > 0:
                rate = ((obj.unique_visitors - previous_day.unique_visitors) / previous_day.unique_visitors) * 100
                color = "green" if rate >= 0 else "red"
                return format_html(
                    '<span style="color: {};">{:+.1f}%</span>',
                    color, rate
                )
        except:
            pass
        return "-"
    growth_rate.short_description = 'Growth Rate'

@admin.register(PopularPage)
class PopularPageAdmin(admin.ModelAdmin):
    list_display = ['page_path', 'page_title', 'visit_count', 'percentage', 'last_visited']
    search_fields = ['page_path', 'page_title']
    ordering = ['-visit_count']
    readonly_fields = ['last_visited']
    
    def percentage(self, obj):
        total_visits = PopularPage.objects.aggregate(
            total=Sum('visit_count')
        )['total'] or 0
        if total_visits > 0:
            percent = (obj.visit_count / total_visits) * 100
            return f"{percent:.1f}%"
        return "0%"
    percentage.short_description = 'Share'

@admin.register(VisitorGeolocation)
class VisitorGeolocationAdmin(admin.ModelAdmin):
    list_display = ['location_display', 'visitor_count', 'percentage', 'last_visit']
    list_filter = ['country', 'last_visit']
    search_fields = ['country', 'city']
    ordering = ['-visitor_count']
    
    def location_display(self, obj):
        if obj.city:
            return f"{obj.city}, {obj.country}"
        return obj.country
    location_display.short_description = 'Location'
    
    def percentage(self, obj):
        total_visitors = VisitorGeolocation.objects.aggregate(
            total=Sum('visitor_count')
        )['total'] or 0
        if total_visitors > 0:
            percent = (obj.visitor_count / total_visitors) * 100
            return f"{percent:.1f}%"
        return "0%"
    percentage.short_description = 'Share'

# Customize admin site header
admin.site.site_header = "Portfolio Admin Dashboard"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Welcome to Portfolio Administration"