from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracking_view, name='home'),
    path('tracking/', views.tracking_view, name='tracking'),
    path('create/', views.create_request_view, name='create_request'),
    path('requests/', views.my_requests_view, name='my_requests'),
    path('sent/', views.sent_requests_view, name='sent_requests'),
    path('received/', views.received_view, name='received'),
    path('request_detail/<int:request_id>/', views.request_detail, name='request_detail'),
]