from django.contrib import admin
from .models import Profile, Skill, Project, Certification, Experience, ContactMessage



admin.site.register(Profile)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Project)
admin.site.register(Certification)
admin.site.register(Experience)
admin.site.register(ContactMessage)