from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import login_required_message
from .forms import ProjectForm, CategoryForm
from .models import Category, Project

# setting default empty values for projects, categories, and trending
# so even if database fails, the code will not crash
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

# getting all projects and filtering them based on search, category and status
# sorting projects (latest, oldest or alphabetical) and selecting top 3 approved projects as trending
# handling database errors so the app does not crash and shows a message to the user
    try:
        # Optimization: Use .only() to explicitly fetch required fields over .defer()
        projects = Project.objects.select_related('category', 'created_by').only(
            'id', 'title', 'status', 'category_id', 'created_by_id', 'created_at', 
            'student_name', 'roll_number', 'project_link'
        )
        
        if search:
            # Optimization: Changed icontains to istartswith to allow B-tree Index Range Scanning
            projects = projects.filter(title__istartswith=search)
        if category_slug:
            # Optimization: Changed iexact to direct match to prevent index evasion (UPPER() scanning)
            projects = projects.filter(category__name=category_slug)
        if status_filter:
            projects = projects.filter(status=status_filter)

        if sort == 'oldest':
            projects = projects.order_by('created_at')
        elif sort == 'alpha':
            projects = projects.order_by('title')
        else:
            projects = projects.order_by('-created_at')

        categories = Category.objects.all()
        trending = Project.objects.filter(status='approved').order_by('-created_at')[:3]
    except DatabaseError:
        db_error = 'Database not ready...'
        messages.error(request, 'Unable to load projects. Database schema not ready.')

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

# sending all data to template to display projects, filters, and messages on the page
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

# fetching project using primary key (id) if not found it shows 404 error
# sending project data to template to display details
@login_required_message
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_detail.html', {'project': project})

# fetching logged-in users projects and categories from database
# calculating total, approved, pending and rejected project counts for stats
# handling database error by showing message and keeping data empty
@login_required_message
def studio_view(request):
    db_error = None
    try:
        from django.db.models import Count, Q
        categories = Category.objects.all()
        # Ensure description is excluded using .only() for efficiency 
        my_projects = Project.objects.filter(created_by=request.user).select_related('category').only(
            'id', 'title', 'status', 'category_id', 'created_at', 'student_name', 'project_link', 'roll_number'
        )
        
        # Optimization: replacing N+1 queries with single aggregation
        stats_agg = my_projects.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(status=Project.STATUS_APPROVED)),
            pending=Count('id', filter=Q(status=Project.STATUS_PENDING)),
            rejected=Count('id', filter=Q(status=Project.STATUS_REJECTED)),
        )
        
        stats = {
            'total': stats_agg['total'] or 0,
            'approved': stats_agg['approved'] or 0,
            'pending': stats_agg['pending'] or 0,
            'rejected': stats_agg['rejected'] or 0
        }
    except DatabaseError:
        db_error = 'Your workspace isn`t ready yet. Please wait a moment and try again.'
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

# handling form to create a new project or add a new category
# if category form is submitted, save category, otherwise save project with current user
# showing success message and redirecting to studio page
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

# getting project by id for the logged-in user
# if project is already approved, do not allow editing and show warning
# otherwise update project details and save changes
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

# getting project by id for logged-in user
# if project is approved, do not allow delete and show warning
# if user confirms (POST), delete project and redirect
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
