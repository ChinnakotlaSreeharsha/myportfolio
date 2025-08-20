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
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    badge_image = models.ImageField(upload_to='certifications/', blank=True, null=True)
    badge_url = models.URLField()

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

