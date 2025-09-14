# main/models.py
from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='profile/')
    resume = models.FileField(upload_to='resume/')
    email = models.EmailField()
    github = models.URLField()
    linkedin = models.URLField()
    credly = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="education_list")
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(default=2025)
    grade = models.CharField(max_length=20, blank=True, null=True)  # new field for GPA/percentage
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Python', 'Data'),
        ('SQL', 'Data'),
        ('Pandas', 'Data'),
        ('NumPy', 'Data'),
        ('ML Integration', 'Data'),
        ('Data Wrangling', 'Data'),
        ('Automation Scripts', 'Backend'),
        ('Django', 'Backend'),
        ('Git', 'DevOps'),
        ('UX for Data', 'Frontend'),
        ('Dashboard Design', 'Frontend'),
        ('Problem Solving', 'Other'),
        ('Communication', 'Other'),
    ]

    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=100)
    proficiency = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Other')

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    github_link = models.URLField(blank=True)
    demo_link = models.URLField(blank=True)

    def __str__(self):
        return self.title

class Experience(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    skills_used = models.ManyToManyField(Skill, blank=True)


    def __str__(self):
        return self.title

class Certification(models.Model):
    MONTH_CHOICES = [
        ("January","January"),("February","February"),("March","March"),
        ("April","April"),("May","May"),("June","June"),
        ("July","July"),("August","August"),("September","September"),
        ("October","October"),("November","November"),("December","December")
    ]

    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True, null=True)
    issue_date_month = models.CharField(max_length=20, choices=MONTH_CHOICES, blank=True, null=True)
    issue_date_year = models.PositiveIntegerField(blank=True, null=True)
    expiration_date_month = models.CharField(max_length=20, choices=MONTH_CHOICES, blank=True, null=True)
    expiration_date_year = models.PositiveIntegerField(blank=True, null=True)
    credential_id = models.CharField(max_length=255, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)
    issuer_logo = models.ImageField(upload_to="cert_logos/", blank=True, null=True)

    class Meta:
        ordering = ['-issue_date_year', '-issue_date_month']

    def __str__(self):
        return f"{self.name} ({self.issuer})" if self.issuer else self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


# Add to your existing main/models.py

from django.db import models
from django.utils import timezone

class VisitorCount(models.Model):
    """Global visitor counter"""
    count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Total Visitor Count"
        verbose_name_plural = "Total Visitor Count"
    
    def __str__(self):
        return f"Total Visitors: {self.count:,}"

class VisitorSession(models.Model):
    """Individual visitor session tracking"""
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    first_visit = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    page_views = models.PositiveIntegerField(default=1)
    is_returning = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-first_visit']
        verbose_name = "Visitor Session"
        verbose_name_plural = "Visitor Sessions"
    
    def __str__(self):
        return f"Visitor {self.session_id[:8]}... - {self.first_visit.strftime('%Y-%m-%d %H:%M')}"

class DailyVisitorStats(models.Model):
    """Daily visitor statistics"""
    date = models.DateField(unique=True, db_index=True)
    unique_visitors = models.PositiveIntegerField(default=0)
    total_page_views = models.PositiveIntegerField(default=0)
    new_visitors = models.PositiveIntegerField(default=0)
    returning_visitors = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Daily Visitor Stats"
        verbose_name_plural = "Daily Visitor Stats"
    
    def __str__(self):
        return f"{self.date} - {self.unique_visitors} visitors"

class PopularPage(models.Model):
    """Track popular pages"""
    page_path = models.CharField(max_length=500, unique=True)
    page_title = models.CharField(max_length=200, blank=True)
    visit_count = models.PositiveIntegerField(default=0)
    last_visited = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_count']
        verbose_name = "Popular Page"
        verbose_name_plural = "Popular Pages"
    
    def __str__(self):
        return f"{self.page_path} ({self.visit_count} visits)"

class VisitorGeolocation(models.Model):
    """Visitor location statistics"""
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    visitor_count = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['country', 'city']
        ordering = ['-visitor_count']
        verbose_name = "Visitor Location"
        verbose_name_plural = "Visitor Locations"
    
    def __str__(self):
        return f"{self.city}, {self.country} ({self.visitor_count} visitors)"