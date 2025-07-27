from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'categories', api_views.CategoryViewSet, basename='category')
router.register(r'wallets', api_views.WalletViewSet, basename='wallet')
router.register(r'payees', api_views.PayeeViewSet, basename='payee')
router.register(r'transactions', api_views.TransactionViewSet, basename='transaction')
router.register(r'budgets', api_views.BudgetViewSet, basename='budget')
router.register(r'goals', api_views.FinancialGoalViewSet, basename='goal')
router.register(r'debts', api_views.DebtViewSet, basename='debt')
router.register(r'transfers', api_views.TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]