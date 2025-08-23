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

from django.shortcuts import render
from datetime import datetime
from .models import Certification

def certifications(request):
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    certs = Certification.objects.all()

    # Distinct years for dropdown
    years = Certification.objects.values_list('issue_date_year', flat=True).distinct().order_by('-issue_date_year')

    cert_list = []
    now = datetime.now()

    for cert in certs:
        # Numeric month conversion
        issue_month_num = month_order.get(cert.issue_date_month, 0)
        exp_month_num = month_order.get(cert.expiration_date_month, 0)

        # Issue date
        issue_date = None
        if cert.issue_date_year and cert.issue_date_month:
            try:
                issue_date = datetime(int(cert.issue_date_year), issue_month_num, 1)
            except:
                pass

        # Expiration date
        exp_date = None
        if cert.expiration_date_year and cert.expiration_date_month:
            try:
                exp_date = datetime(int(cert.expiration_date_year), exp_month_num, 1)
            except:
                pass

        # Badges
        expired = exp_date < now if exp_date else False
        new_cert = issue_date and (now - issue_date).days <= 90
        expiring_soon = exp_date and 0 <= (exp_date - now).days <= 60

        cert_list.append({
            'cert': cert,
            'expired': expired,
            'new_cert': new_cert,
            'expiring_soon': expiring_soon,
            'issue_date': issue_date,
            'exp_date': exp_date,
            'issue_month_num': issue_month_num
        })

    # Sort newest issued first
    cert_list.sort(key=lambda x: (int(x['cert'].issue_date_year or 0), x['issue_month_num']), reverse=True)

    return render(request, 'main/certifications.html', {
        'cert_list': cert_list,
        'years': years
    })


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

from django.shortcuts import render
from .models import Profile

def about(request):
    profile = Profile.objects.first()  # or filter for your profile
    context = {
        "profile": profile,
        "education_list": profile.education_list.all()  # now it works
    }
    return render(request, "main/about.html", context)


