from django.shortcuts import render
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Skill

def home(request):
    profile = Profile.objects.first()
    return render(request, 'main/home.html', {'profile': profile})

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
    certs = Certification.objects.all()
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

