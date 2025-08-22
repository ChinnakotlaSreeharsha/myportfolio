from django.shortcuts import render
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Skill
from .models import Profile, Certification

def home(request):
    profile = Profile.objects.first()
    certifications_count = Certification.objects.count()
    return render(request, 'main/home.html', {
        'profile': profile,
        'certifications_count': certifications_count
    })

def about(request):
    profile = Profile.objects.first()
    return render(request, 'main/about.html', {'profile': profile})

def skills(request):
    category = request.GET.get('category')
    skills = Skill.objects.all()

    if category:
        skills = skills.filter(category=category)

    categories = Skill.objects.values_list('category', flat=True).distinct()

    return render(request, 'main/skills.html', {
        'skills': skills,
        'categories': categories,
        'current_category': category,
    })

def projects(request):
    projects = Project.objects.all()
    return render(request, 'main/projects.html', {'projects': projects})

def experience(request):
    experiences = Experience.objects.all().order_by('-start_date')
    return render(request, 'main/experience.html', {'experiences': experiences})

def certifications(request):
    # Convert month names to numbers for proper sorting
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    certs = list(Certification.objects.all())

    # Add numeric month to each cert for sorting
    for cert in certs:
        cert.issue_month_num = month_order.get(cert.issue_date_month, 0)
        cert.expiration_month_num = month_order.get(cert.expiration_date_month, 0)

    # Sort: newest issued first
    certs.sort(key=lambda c: (
        int(c.issue_date_year) if c.issue_date_year else 0,
        c.issue_month_num
    ), reverse=True)

    return render(request, 'main/certifications.html', {'certs': certs})

def resume(request):
    profile = Profile.objects.first()
    resume_url = request.build_absolute_uri(profile.resume.url) if profile and profile.resume else None
    return render(request, 'main/resume.html', {
        'resume': profile.resume,
        'resume_url': resume_url
    })

def contact(request):
    profile = Profile.objects.first()
    form = ContactForm()
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # Auto-reply to user
            send_mail(
                subject="Thanks for contacting me!",
                message=f"Hi {contact.name},\n\nThank you for your message. I will get back to you soon.\n\nBest,\n{profile.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact.email],
                fail_silently=False,
            )

            # (Optional) Notify you
            send_mail(
                subject=f"New Contact Message from {contact.name}",
                message=f"Subject: {contact.subject}\n\n{contact.message}\n\nEmail: {contact.email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.email],  # You receive a copy
                fail_silently=False,
            )

            success = True
            form = ContactForm()  # Clear form

    return render(request, 'main/contact.html', {
        'form': form,
        'profile': profile,
        'success': success
    })


