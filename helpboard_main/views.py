from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from helpboard.models import Category, Problem
from . forms import registrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.contrib import messages  # Add this import for messages
from django.db.models import Count
from django.contrib.auth.models import User
import json


# HOME / DASHBOARD
def home(request):
    categories = Category.objects.all()

    #  Category names and counts for pie chart
    category_names = [cat.name for cat in categories]
    category_counts = [Problem.objects.filter(category=cat).count() for cat in categories]

    #  Pending vs Resolved counts for bar chart
    pending_count = Problem.objects.filter(status=Problem.PENDING).count()
    resolved_count = Problem.objects.filter(status=Problem.RESOLVED).count()
    in_progress_count = Problem.objects.filter(status=Problem.IN_PROGRESS).count()

    # Recent activity (last 5 updated problems with meaningful descriptions)
    recent_activity = Problem.objects.select_related('author').order_by('-updated_at')[:5]
    recent_activity_data = []
    for prob in recent_activity:
        # Determine activity type based on created_at vs updated_at
        if prob.created_at == prob.updated_at:
            # Problem just created
            icon = "!"
            activity_msg = f"{prob.author.username} posted '{prob.title[:20]}...'" if len(prob.title) > 20 else f"{prob.author.username} posted '{prob.title}'"
            activity_type = "Created"
        elif prob.status == Problem.RESOLVED:
            # Problem was solved
            icon = "!"
            activity_msg = f"'{prob.title[:20]}...' has been solved" if len(prob.title) > 20 else f"'{prob.title}' has been solved"
            activity_type = "Resolved"
        elif prob.status == Problem.IN_PROGRESS:
            # Problem status changed to in progress
            icon = "!"
            activity_msg = f"'{prob.title[:20]}...' is being worked on" if len(prob.title) > 20 else f"'{prob.title}' is being worked on"
            activity_type = "In Progress"
        else:
            # Default to problem updated
            icon = "!"
            activity_msg = f"'{prob.title[:20]}...' was updated" if len(prob.title) > 20 else f"'{prob.title}' was updated"
            activity_type = "Updated"
        
        recent_activity_data.append({
            'title': activity_msg,
            'icon': icon,
            'status': prob.get_status_display(),
            'category': prob.category.name,
            'updated_at': prob.updated_at.strftime('%b %d, %H:%M'),
            'author': prob.author.username,
            'type': activity_type
        })

    # Total users count
    total_users = User.objects.count()
    total_problems = Problem.objects.count()
    total_solved = resolved_count

    context = {
        "categories": categories,
        "category_names": json.dumps(category_names),
        "category_counts": json.dumps(category_counts),
        "pending_count": pending_count,
        "resolved_count": resolved_count,
        "in_progress_count": in_progress_count,
        "recent_activity": recent_activity_data,
        "total_users": total_users,
        "total_problems": total_problems,
        "total_solved": total_solved,
        "open_count": pending_count + in_progress_count,
        "solved_count": resolved_count,
    }

    return render(request, "home.html", context)


    
# CATEGORY → ALL PROBLEMS
def category_problems(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)

    # ONLY UNRESOLVED problems for category page
    problems = Problem.objects.filter(
        category=category
    ).exclude(status=2).order_by('-created_at')

    # ONLY UNRESOLVED + FEATURED problems
    featured_posts = Problem.objects.filter(
        category=category,
        is_featured=True
    ).exclude(status=2).order_by('-created_at')

    context = {
        'category': category,
        'problems': problems,
        'featured_posts': featured_posts
    }

    return render(request, 'category_problems.html', context)


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    solvers = problem.solvers.select_related('solver').all()
    can_mark_solved = request.user.is_authenticated and request.user == problem.author and problem.status != Problem.RESOLVED
    comments = problem.comments.select_related('author').order_by('-created_at')

    return render(request, 'problem_detail.html', {
        'problem': problem,
        'solvers': solvers,
        'can_mark_solved': can_mark_solved,
        'comments': comments,
    })


@login_required(login_url='login')
def add_comment(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            from helpboard.models import Comment
            Comment.objects.create(
                problem=problem,
                author=request.user,
                content=content
            )
    return redirect('problem_detail', problem_id=problem.id)



@login_required(login_url='login')
def mark_problem_solved(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.user != problem.author:
        raise PermissionDenied("Only the problem owner can mark this as solved.")

    if request.method != 'POST':
        raise PermissionDenied("Invalid request method.")

    problem.status = Problem.RESOLVED
    problem.save(update_fields=['status'])
    # Notification to solvers + author (optional)
    return redirect('problem_detail', problem_id=problem.id)


# SIGNUP
def signup(request):
    if request.method == 'POST':
        form = registrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Changed to auth_login
            return redirect('dashboard')
    else:
        form = registrationForm()

    context = {
        'form': form
    }
    return render(request, 'registration/signup.html', context)

# LOGIN VIEW
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Changed to auth_login
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html')

# LOGOUT VIEW
def logout(request):
    auth_logout(request)
    return redirect('home')


# ABOUT PAGE
def about(request):
    """About page"""
    context = {
        'app_name': 'Seva Setu',
        'tagline': 'Bridging communities through service and collaboration',
        'mission': 'Empower users to report local problems, connect volunteers, and close community issues together.',
        'vision': 'A safer, cleaner, and more connected neighborhood for every person.',
        'values': [
            'Community first',
            'Transparency and trust',
            'Actionable outcomes',
            'Empathy and inclusion',
        ]
    }
    return render(request, 'about.html', context)