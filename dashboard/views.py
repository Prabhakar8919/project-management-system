from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.db import DatabaseError
from django.shortcuts import redirect, render

from accounts.decorators import login_required_message

from dashboard.forms import AdminLoginForm
from projects.models import Project
from django.contrib.auth.models import User


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_panel')
    form = AdminLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password'),
        )
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_panel')
        messages.error(request, 'Invalid admin credentials.')
    return render(request, 'dashboard/admin_login.html', {'form': form})


def staff_required(view_func):
    decorated = user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='/admin-login/')
    return decorated(view_func)


@login_required_message
def dashboard_view(request):
    try:
        projects = Project.objects.filter(created_by=request.user)
        total = projects.count()
        approved = projects.filter(status=Project.STATUS_APPROVED).count()
        pending = projects.filter(status=Project.STATUS_PENDING).count()
        rejected = projects.filter(status=Project.STATUS_REJECTED).count()
        recent = projects.order_by('-created_at')[:6]
        
        # Calculate metrics
        approval_rate = round((approved / total * 100) if total > 0 else 0)
        
        # Category breakdown
        from django.db.models import Count
        category_breakdown = projects.values('category__name').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Calculate max count for percentage calculation
        max_category_count = max([item['count'] for item in category_breakdown]) if category_breakdown else 1
        
        # Add percentage to each category
        for item in category_breakdown:
            item['percentage'] = (item['count'] / max_category_count * 100) if max_category_count > 0 else 0
            item['hue'] = (list(category_breakdown).index(item) + 1) * 60
        
        # Top projects (most recently approved)
        top_projects = projects.filter(status=Project.STATUS_APPROVED).order_by('-created_at')[:3]
        
        # All categories for filter
        all_categories = Project.objects.filter(created_by=request.user).values('category__name').distinct()
        
        # Status distribution
        status_dist = {
            'approved_pct': round((approved / total * 100) if total > 0 else 0),
            'pending_pct': round((pending / total * 100) if total > 0 else 0),
            'rejected_pct': round((rejected / total * 100) if total > 0 else 0),
        }
        
    except DatabaseError:
        messages.error(request, 'Unable to load dashboard data at this time.')
        projects = Project.objects.none()
        total = approved = pending = rejected = 0
        recent = Project.objects.none()
        approval_rate = 0
        category_breakdown = []
        top_projects = []
        all_categories = []
        status_dist = {'approved_pct': 0, 'pending_pct': 0, 'rejected_pct': 0}
        
    return render(
        request,
        'dashboard/dashboard.html',
        {
            'stats': {'total': total, 'approved': approved, 'pending': pending, 'rejected': rejected},
            'recent': recent,
            'approval_rate': approval_rate,
            'category_breakdown': category_breakdown,
            'top_projects': top_projects,
            'all_categories': all_categories,
            'status_dist': status_dist,
        },
    )


@staff_required
def admin_panel(request):
    projects = Project.objects.select_related('created_by', 'category').order_by('-created_at')
    users = User.objects.all().order_by('-date_joined')[:10]
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        action = request.POST.get('action')
        project = Project.objects.filter(pk=project_id).first()
        if project and action in [Project.STATUS_APPROVED, Project.STATUS_REJECTED, Project.STATUS_PENDING]:
            project.status = action
            project.save()
            messages.success(request, f'Project "{project.title}" set to {project.get_status_display()}.')
            return redirect('admin_panel')
    counts = {
        'total_users': User.objects.count(),
        'total_projects': Project.objects.count(),
        'approved': projects.filter(status=Project.STATUS_APPROVED).count(),
        'pending': projects.filter(status=Project.STATUS_PENDING).count(),
        'rejected': projects.filter(status=Project.STATUS_REJECTED).count(),
    }
    return render(request, 'dashboard/admin_panel.html', {'projects': projects, 'users': users, 'counts': counts})
