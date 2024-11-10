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
    path('cost_estimation/<int:shop_id>/', views.cost_estimation, name='cost_estimation'),
    path('owner/settings/', views.configure_print_cost, name='owner_settings'),
    path('payment/<int:shop_id>/', views.payment_gateway, name='payment_gateway'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
