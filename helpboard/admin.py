from django.contrib import admin
from .models import Category, Problem, ProblemSolver, Notification, Comment


# ============================
# CATEGORY ADMIN
# ============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


# ============================
# PROBLEM ADMIN
# ============================
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "is_featured",
        "author",
        "category",
        "created_at",
    )

    list_filter = ("status", "category", "created_at", "is_featured")
    search_fields = ("title", "short_description", "description", "id")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("status", "is_featured")
    ordering = ("-created_at",)


# ============================
# PROBLEM SOLVER ADMIN
# ============================
@admin.register(ProblemSolver)
class ProblemSolverAdmin(admin.ModelAdmin):
    list_display = ("problem", "solver", "joined_at")
    search_fields = ("problem__title", "solver__username")
    ordering = ("-joined_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "helper", "problem", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "helper__username", "problem__title", "message")
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("problem", "author", "created_at")
    search_fields = ("problem__title", "author__username", "content")
    ordering = ("-created_at",)
