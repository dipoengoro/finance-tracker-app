from django.urls import path
from . import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('add/', views.transaction_add, name='transaction_add'),
    path('delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
]