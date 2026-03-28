from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from helpboard.models import Category, Problem, Notification
from .forms import ProblemForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
import json


# ==================================================
# DASHBOARD HOME
# ==================================================
@login_required(login_url='login')
def dashboard(request):
    # Get all statistics
    categories = Category.objects.all()
    category_names = [cat.name for cat in categories]
    category_counts = [Problem.objects.filter(category=cat).count() for cat in categories]
    
    pending_count = Problem.objects.filter(status=Problem.PENDING).count()
    resolved_count = Problem.objects.filter(status=Problem.RESOLVED).count()
    in_progress_count = Problem.objects.filter(status=Problem.IN_PROGRESS).count()
    
    total_users = User.objects.count()
    total_problems = Problem.objects.count()
    total_categories = Category.objects.count()
    
    # Recent activity (last 5 problems with meaningful descriptions)
    recent_activity = Problem.objects.select_related('author').order_by('-updated_at')[:5]
    recent_activity_data = []
    for prob in recent_activity:
        # Determine activity type based on created_at vs updated_at
        if prob.created_at == prob.updated_at:
            # Problem just created
            activity_msg = f"🆕 {prob.author.username} created '{prob.title[:25]}...'" if len(prob.title) > 25 else f"🆕 {prob.author.username} created '{prob.title}'"
        elif prob.status == Problem.RESOLVED:
            # Problem was solved
            activity_msg = f"✅ Problem solved: '{prob.title[:25]}...'" if len(prob.title) > 25 else f"✅ Problem solved: '{prob.title}'"
        elif prob.status == Problem.IN_PROGRESS:
            # Problem status changed to in progress
            activity_msg = f"🔄 {prob.author.username} working on '{prob.title[:25]}...'" if len(prob.title) > 25 else f"🔄 {prob.author.username} working on '{prob.title}'"
        else:
            # Default to problem updated
            activity_msg = f"📝 '{prob.title[:25]}...'" if len(prob.title) > 25 else f"📝 '{prob.title}'"
        
        recent_activity_data.append({
            'title': activity_msg,
            'status': prob.get_status_display(),
            'updated_at': timezone.localtime(prob.updated_at).strftime('%b %d %H:%M'),
            'author': prob.author.username
        })
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'category_counts': total_categories,
        'problem_counts': total_problems,
        'solved_issues': resolved_count,
        'pending_issues': pending_count,
        'in_progress_issues': in_progress_count,
        'total_users': total_users,
        'category_names': json.dumps(category_names),
        'category_stats': json.dumps(category_counts),
        'recent_activity': recent_activity_data,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'dashboard/dashboard.html', context)


# ==================================================
# NOTIFICATIONS 
# ==================================================
@login_required(login_url='login')
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect('dashboard')


@login_required(login_url='login')
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    problem = notification.problem
    if problem and problem.status == Problem.PENDING:
        problem.status = Problem.IN_PROGRESS
        problem.save(update_fields=['status'])

    helper = notification.helper

    return render(request, 'dashboard/notification_detail.html', {
        'notification': notification,
        'problem': problem,
        'helper': helper,
    })


@login_required(login_url='login')
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('dashboard')


@login_required(login_url='login')
def notifications_json(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [
        {
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': timezone.localtime(n.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            'problem_id': n.problem.id if n.problem else None,
            'problem_title': n.problem.title if n.problem else '',
            'url': n.problem.get_absolute_url() if n.problem else ''
        }
        for n in notifications
    ]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread_count})


# ==================================================
# MY PROBLEMS (User-specific)
# ==================================================
@login_required(login_url='login')
def myproblems(request):
    user_problems = Problem.objects.filter(author=request.user)

    context = {
        'user_problems': user_problems,
        'category_counts': Category.objects.count(),
        'problem_counts': user_problems.count(),
        'solved_issues': user_problems.filter(status=Problem.RESOLVED).count(),
    }
    return render(request, 'dashboard/myproblems.html', context)


# ==================================================
# ADD NEW PROBLEM
# ==================================================
@login_required(login_url='login')
def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.author = request.user
            problem.save()
            return redirect('myproblems')
    else:
        form = ProblemForm()

    return render(request, 'dashboard/add_problem.html', {
        'form': form
    })


# ==================================================
# DELETE PROBLEM
# ==================================================
@login_required(login_url='login')
def delete_problem(request, problem_id):
    problem = get_object_or_404(
        Problem,
        id=problem_id,
        author=request.user
    )

    if request.method == 'POST':
        problem.delete()
        return redirect('myproblems')

    return render(request, 'dashboard/delete_problem.html', {
        'problem': problem
    })


# ==================================================
# SOLVED ISSUES (GLOBAL)
# ==================================================
@login_required(login_url='login')
def solved_issues(request):
    solved_issues = Problem.objects.filter(
        status=2   # Resolved only
    ).order_by('-updated_at')

    return render(request, 'dashboard/solved_issues.html', {
        'solved_issues': solved_issues
    })
