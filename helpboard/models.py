from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# ==================================================
# CATEGORY MODEL
# ==================================================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==================================================
# PROBLEM MODEL
# ==================================================
class Problem(models.Model):

    # ---------- STATUS CONSTANTS ----------
    PENDING = 0
    IN_PROGRESS = 1
    RESOLVED = 2

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (IN_PROGRESS, "In Progress"),
        (RESOLVED, "Resolved"),
    ]

    # ---------- CORE FIELDS ----------
    title = models.CharField(max_length=200)
    short_description = models.TextField(max_length=1000)
    description = models.TextField(max_length=3000)

    image = models.ImageField(
        upload_to="problem_images/%Y/%m/%d",
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="problems"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reported_problems"
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Location where the problem exists"
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=PENDING
    )

    is_featured = models.BooleanField(default=False)

    slug = models.SlugField(unique=True, blank=True)

    # ---------- TIME TRACKING ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    solved_at = models.DateTimeField(blank=True, null=True)

    # ---------- MODEL CONFIG ----------
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
        ]

    # ---------- SAVE OVERRIDE ----------
    def save(self, *args, **kwargs):

        # Set solved time automatically
        if self.status == self.RESOLVED and self.solved_at is None:
            self.solved_at = timezone.now()

        # Generate unique slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Problem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('problem_detail', kwargs={'problem_id': self.id})

    def get_status_class(self):
        return self.get_status_display().lower().replace(' ', '-')

    def __str__(self):
        return self.title


# ==================================================
# PROBLEM SOLVER MODEL
# ==================================================
class ProblemSolver(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="solvers"
    )
    solver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solver_attempts"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("problem", "solver")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.solver.username} → {self.problem.title}"


class Comment(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='problem_comments'
    )
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.problem.title[:30]}"

# ==================================================
# NOTIFICATION MODEL
# ==================================================
class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    helper = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helper_notifications',
        null=True,
        blank=True
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:40]}"


# ==================================================
# USER PROFILE MODEL
# ==================================================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None


# ==================================================
# SIGNALS
# ==================================================
@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    # Created users get a profile (new registration flow)
    # Existing users will also get one on login+save if missing.
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    profile.save()



