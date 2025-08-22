from django.contrib import admin
from .models import Profile, Skill, Project, Certification, Experience, ContactMessage

# Other models
admin.site.register(Profile)

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
