from django.urls import path
from . import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('add/', views.transaction_add, name='transaction_add'),
    path('delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    path('update/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/add/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('goals/', views.FinancialGoalListView.as_view(), name='goal_list'),
    path('goals/add/', views.FinancialGoalCreateView.as_view(), name='goal_create'),
]