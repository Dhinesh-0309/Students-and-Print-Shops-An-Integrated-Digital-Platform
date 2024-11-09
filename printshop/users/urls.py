# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('student/signup/', views.student_signup, name='student_signup'),
    path('owner/signup/', views.owner_signup, name='owner_signup'),
    path('login/', views.user_login, name='login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('upload_file/<int:shop_id>/', views.upload_file, name='upload_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
