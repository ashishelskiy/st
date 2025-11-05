from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracking_view, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # path('tracking/', views.tracking_view, name='track_request'),
    path("tracking/", views.track_request_view, name="track_request"),
    path('create/', views.create_request_view, name='create_request'),
    path('requests/', views.my_requests_view, name='my_requests'),
    path('sent/', views.sent_requests_view, name='sent_requests'),
    path('received/', views.received_requests, name='received_requests'),
    path('request_detail/<int:request_id>/', views.request_detail, name='request_detail'),
    path("my-requests/send/", views.sent_requests_view, name="send_selected_requests"),
    path('package/<int:package_id>/', views.package_detail_view, name='package_detail'),
    path('sc/package/<int:package_id>/', views.sc_package_detail, name='sc_package_detail'),
    path('update_request_status/<int:request_id>/', views.update_request_status, name='update_request_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)