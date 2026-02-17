from django.urls import path
from . import views

urlpatterns = [
    path('', views.TicketListCreate.as_view(), name='ticket-list'),
    path('<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),
    path('classify/', views.classify_ticket, name='classify'),
    path('stats/', views.ticket_stats, name='stats'),
]