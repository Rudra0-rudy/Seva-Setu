from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from helpboard_main import views
from helpboard import views as helpboard_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Home / Dashboard
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Category → Problems list
    path(
        'category/<int:cat_id>/problems/',
        views.category_problems,
        name='category_problems'
    ),

    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/dashboard/', include('dashboards.urls')),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/<int:problem_id>/solve/', helpboard_views.i_can_solve, name='i_can_solve'),
    path('problem/<int:problem_id>/resolve/', views.mark_problem_solved, name='mark_problem_solved'),
    path('problem/<int:problem_id>/comment/', views.add_comment, name='add_comment'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

