from rest_framework import viewsets
from .models import Category, Wallet, Payee, Transaction, Budget, FinancialGoal, Debt, Transfer
from .serializers import (
    CategorySerializer, WalletSerializer, PayeeSerializer, TransactionSerializer,
    BudgetSerializer, FinancialGoalSerializer, DebtSerializer, TransferSerializer
)

class BaseUserViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(BaseUserViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class WalletViewSet(BaseUserViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class PayeeViewSet(BaseUserViewSet):
    queryset = Payee.objects.all()
    serializer_class = PayeeSerializer

class TransactionViewSet(BaseUserViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class BudgetViewSet(BaseUserViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class FinancialGoalViewSet(BaseUserViewSet):
    queryset = FinancialGoal.objects.all()
    serializer_class = FinancialGoalSerializer

class DebtViewSet(BaseUserViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

class TransferViewSet(BaseUserViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer