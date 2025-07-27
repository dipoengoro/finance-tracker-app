from django.urls import path

from . import views

urlpatterns = [path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('add/', views.transaction_add, name='transaction_add'),
    path('delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    path('update/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/add/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('goals/', views.FinancialGoalListView.as_view(), name='goal_list'),
    path('goals/add/', views.FinancialGoalCreateView.as_view(), name='goal_create'),
    path('goals/<int:pk>/add_savings', views.add_saving_to_goal, name='goal_add_savings'),
    path('debts/', views.DebtListView.as_view(), name='debt_list'),
    path('debts/add/', views.DebtCreateView.as_view(), name='debt_create'),
    path('debts/<int:pk>/pay/', views.pay_debt, name='pay_debt'),
    path('transfers/', views.TransferListView.as_view(), name='transfer_list'),
    path('transfers/add/', views.TransferCreateView.as_view(), name='transfer_create'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('export/', views.export_transactions, name='transaction_export'),
    path('wallets/', views.WalletListView.as_view(), name='wallet_list'),
    path('wallets/add/', views.WalletCreateView.as_view(), name='wallet_create'),
    path('wallets/update/<int:pk>/', views.WalletUpdateView.as_view(), name='wallet_update'),
    path('wallets/delete/<int:pk>/', views.WalletDeleteView.as_view(), name='wallet_delete'), ]
