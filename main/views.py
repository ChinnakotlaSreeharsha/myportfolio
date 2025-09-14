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


# UPDATED views.py - Fixed to increment global counter for returning visitors too

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import json
import hashlib

from .models import (
    VisitorCount, VisitorSession, DailyVisitorStats,
    PopularPage, VisitorGeolocation
)

def get_client_ip(request):
    """Get the client's IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_session_id(request):
    """Generate a unique session ID based on IP and user agent"""
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    timestamp = str(timezone.now().date())
    
    # Create a hash-based session ID
    session_string = f"{ip}-{user_agent}-{timestamp}"
    session_id = hashlib.md5(session_string.encode()).hexdigest()
    return session_id

def update_daily_stats(date, is_new_visitor=True):
    """Update daily visitor statistics"""
    stats, created = DailyVisitorStats.objects.get_or_create(
        date=date,
        defaults={
            'unique_visitors': 0,
            'total_page_views': 0,
            'new_visitors': 0,
            'returning_visitors': 0
        }
    )
    
    stats.total_page_views += 1
    
    if is_new_visitor:
        stats.unique_visitors += 1
        stats.new_visitors += 1
    else:
        # Count returning visitors in daily stats
        stats.returning_visitors += 1
    
    stats.save()
    return stats

def update_popular_page(request):
    """Track popular pages"""
    page_path = request.path
    page_title = request.META.get('HTTP_REFERER', '')
    
    page, created = PopularPage.objects.get_or_create(
        page_path=page_path,
        defaults={'page_title': page_title, 'visit_count': 0}
    )
    
    page.visit_count += 1
    page.save()
    return page

def get_geolocation_from_ip(ip_address):
    """
    Get country and city from IP address
    Replace with actual geolocation service like ipapi.co
    """
    try:
        import requests
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('country_name'), data.get('city')
    except:
        pass
    
    return None, None

@csrf_exempt
@require_http_methods(["POST"])
def track_visitor(request):
    """API endpoint to track visitor and increment counter - BOTH NEW AND RETURNING INCREMENT GLOBAL COUNT"""
    try:
        # Parse request data
        data = json.loads(request.body.decode('utf-8'))
        
        # Get client information
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        session_id = generate_session_id(request)
        
        # Get geolocation
        country, city = get_geolocation_from_ip(ip_address)
        
        with transaction.atomic():
            # Check if this is a returning visitor (same session today)
            today = timezone.now().date()
            existing_session = VisitorSession.objects.filter(
                session_id=session_id,
                first_visit__date=today
            ).first()
            
            # Get or create global visitor count
            visitor_count, created = VisitorCount.objects.get_or_create(
                pk=1,
                defaults={'count': 0}
            )
            
            # INCREMENT GLOBAL COUNTER FOR BOTH NEW AND RETURNING VISITORS!
            visitor_count.count += 1
            visitor_count.save()
            visitor_number = visitor_count.count
            
            is_new_visitor = existing_session is None
            
            if existing_session:
                # RETURNING VISITOR - Update session
                existing_session.last_visit = timezone.now()
                existing_session.page_views += 1
                existing_session.is_returning = True
                existing_session.save()
                
                # Update daily stats for returning visitor
                update_daily_stats(today, is_new_visitor=False)
                
            else:
                # NEW VISITOR - Create new session
                VisitorSession.objects.create(
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    referrer=referrer,
                    country=country,
                    city=city,
                    is_returning=False
                )
                
                # Update daily stats for new visitor
                update_daily_stats(today, is_new_visitor=True)
                
                # Update geolocation stats only for new visitors
                if country:
                    geo_location, created = VisitorGeolocation.objects.get_or_create(
                        country=country,
                        city=city or '',
                        defaults={'visitor_count': 0}
                    )
                    geo_location.visitor_count += 1
                    geo_location.save()
            
            # Update popular pages
            update_popular_page(request)
            
            # Prepare response - ALL visitors get incremented visitor number!
            response_data = {
                'status': 'success',
                'visitor_count': visitor_number,
                'is_returning': existing_session is not None,
                'session_id': session_id[:8] + '...',
                'message': 'Welcome back!' if existing_session else 'Welcome!'
            }
            
            return JsonResponse(response_data)
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_visitor_stats(request):
    """API endpoint to get visitor statistics"""
    try:
        total_count = VisitorCount.objects.first()
        today_stats = DailyVisitorStats.objects.filter(
            date=timezone.now().date()
        ).first()
        
        stats = {
            'total_visitors': total_count.count if total_count else 0,
            'today_visitors': (today_stats.unique_visitors + today_stats.returning_visitors) if today_stats else 0,
            'today_page_views': today_stats.total_page_views if today_stats else 0,
            'today_new_visitors': today_stats.new_visitors if today_stats else 0,
            'today_returning_visitors': today_stats.returning_visitors if today_stats else 0,
        }
        
        return JsonResponse({'status': 'success', 'stats': stats})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)