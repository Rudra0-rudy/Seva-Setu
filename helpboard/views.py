from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .models import Problem, ProblemSolver, Notification


# ============================
# I CAN SOLVE View part
# ============================
@login_required(login_url='login')
def i_can_solve(request, problem_id):
    """
    Allows a user to mark themselves as a solver for a problem.
    - Problem author cannot solve their own problem
    - Same user cannot be added twice
    - Problem auto-resolves after 3 solvers
    """

    problem = get_object_or_404(Problem, id=problem_id)

    if problem.author == request.user:
        return redirect('dashboard')

    solver_obj, created = ProblemSolver.objects.get_or_create(
        problem=problem,
        solver=request.user
    )

    if not created:
        # duplicate helper ignored
        return redirect('dashboard')

    # Update issue status
    if problem.status != Problem.RESOLVED:
        if problem.solvers.count() >= 3:
            problem.status = Problem.RESOLVED
        else:
            problem.status = Problem.IN_PROGRESS
        problem.save(update_fields=['status'])

    # Create in-app notification for problem owner
    Notification.objects.create(
        user=problem.author,
        helper=request.user,
        problem=problem,
        message=f"{request.user.username} wants to help your issue '{problem.title}'",
        is_read=False
    )

    # Send email alert to problem owner
    if problem.author.email:
        issue_url = request.build_absolute_uri(reverse('problem_detail', kwargs={'problem_id': problem.id}))
        subject = f"{request.user.username} can help with your issue"
        body = (
            f"Hi {problem.author.username},\n\n"
            f"{request.user.username} has clicked 'I Can Help' for your issue: '{problem.title}'.\n"
            f"You can view the issue here: {issue_url}\n\n"
            "Thanks,\nThe Helpboard Team"
        )
        send_mail(
            subject,
            body,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@helpboard.local'),
            [problem.author.email],
            fail_silently=True,
        )

    return redirect('dashboard')
