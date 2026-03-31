from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import login_required_message
from .forms import ProjectForm, CategoryForm
from .models import Category, Project


@login_required_message
def explorer_view(request):
    search = request.GET.get('search', '').strip()
    category_slug = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    sort = request.GET.get('sort', 'latest')
    db_error = None
    projects = Project.objects.none()
    categories = Category.objects.none()
    trending = Project.objects.none()

    try:
        projects = Project.objects.select_related('category', 'created_by')
        if search:
            projects = projects.filter(title__icontains=search)
        if category_slug:
            projects = projects.filter(category__name__iexact=category_slug)
        if status_filter:
            projects = projects.filter(status=status_filter)

        if sort == 'oldest':
            projects = projects.order_by('created_at')
        elif sort == 'alpha':
            projects = projects.order_by('title')
        else:
            projects = projects.order_by('-created_at')

        categories = Category.objects.all()
        trending = Project.objects.filter(status=Project.STATUS_APPROVED).order_by('-created_at')[:3]
    except DatabaseError:
        db_error = 'Database not ready. Please run migrations and verify your database settings.'
        messages.error(request, 'Unable to load projects. Database schema may not be ready.')

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'status_filter': status_filter,
        'sort': sort,
        'trending': trending,
        'db_error': db_error,
    }
    return render(request, 'projects/explorer.html', context)

    if search:
        projects = projects.filter(title__icontains=search)
    if category_slug:
        projects = projects.filter(category__name__iexact=category_slug)
    if status_filter:
        projects = projects.filter(status=status_filter)

    if sort == 'oldest':
        projects = projects.order_by('created_at')
    elif sort == 'alpha':
        projects = projects.order_by('title')
    else:
        projects = projects.order_by('-created_at')

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    trending = Project.objects.filter(status=Project.STATUS_APPROVED).order_by('-created_at')[:3]
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'status_filter': status_filter,
        'sort': sort,
        'trending': trending,
    }
    return render(request, 'projects/explorer.html', context)


@login_required_message
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required_message
def studio_view(request):
    db_error = None
    try:
        categories = Category.objects.all()
        my_projects = Project.objects.filter(created_by=request.user).select_related('category')
        total = my_projects.count()
        approved = my_projects.filter(status=Project.STATUS_APPROVED).count()
        pending = my_projects.filter(status=Project.STATUS_PENDING).count()
        rejected = my_projects.filter(status=Project.STATUS_REJECTED).count()
        stats = {'total': total, 'approved': approved, 'pending': pending, 'rejected': rejected}
    except DatabaseError:
        db_error = 'Workspace unavailable. Please try again after database setup.'
        messages.error(request, 'Unable to load your projects right now.')
        categories = Category.objects.none()
        my_projects = Project.objects.none()
        stats = {'total': 0, 'approved': 0, 'pending': 0, 'rejected': 0}

    return render(
        request,
        'projects/studio.html',
        {
            'my_projects': my_projects,
            'stats': stats,
            'categories': categories,
            'db_error': db_error,
        },
    )


@login_required_message
def project_create(request):
    form = ProjectForm(request.POST or None)
    category_form = CategoryForm(request.POST or None)
    if request.method == 'POST':
        if 'new_category' in request.POST and category_form.is_valid():
            category_form.save()
            messages.success(request, 'New category added.')
            return redirect('studio')
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project created. Pending approval.')
            return redirect('studio')
    return render(request, 'projects/project_form.html', {'form': form, 'category_form': category_form, 'action': 'Create'})


@login_required_message
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if project.status == Project.STATUS_APPROVED:
        messages.warning(request, 'Approved projects cannot be modified.')
        return redirect('studio')
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Project updated successfully.')
        return redirect('studio')
    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'action': 'Edit'})


@login_required_message
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if project.status == Project.STATUS_APPROVED:
        messages.warning(request, 'Approved projects cannot be deleted.')
        return redirect('studio')
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('studio')
    return render(request, 'projects/confirm_delete.html', {'project': project})
