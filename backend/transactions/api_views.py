from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, Wallet, Payee, Transaction, Budget, FinancialGoal, Debt, Transfer
from .serializers import (
    CategorySerializer, WalletSerializer, PayeeSerializer, TransactionSerializer,
    BudgetSerializer, FinancialGoalSerializer, DebtSerializer, TransferSerializer, UserSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whoami(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class BaseUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

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

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        wallet = transaction.wallet
        total_expense = transaction.amount + transaction.admin_fee
        if transaction.transaction_type == 'PENGELUARAN':
            wallet.balance -= total_expense
        elif transaction.transaction_type == 'PEMASUKAN':
            wallet.balance += transaction.amount
        wallet.save()

    def perform_update(self, serializer):
        old_transaction = self.get_object()
        old_wallet = old_transaction.wallet
        if old_transaction.transaction_type == 'PENGELUARAN':
            old_wallet.balance += (old_transaction.amount + old_transaction.admin_fee)
        elif old_transaction.transaction_type == 'PEMASUKAN':
            old_wallet.balance -= old_transaction.amount
        old_wallet.save()

        new_transaction = serializer.save()
        new_wallet = new_transaction.wallet
        if new_transaction.transaction_type == 'PENGELUARAN':
            new_wallet.balance -= (new_transaction.amount + new_transaction.admin_fee)
        elif new_transaction.transaction_type == 'PEMASUKAN':
            new_wallet.balance += new_transaction.amount
        new_wallet.save()


    def perform_destroy(self, instance):
        wallet = instance.wallet
        if instance.transaction_type == 'PENGELUARAN':
            wallet.balance += (instance.amount + instance.admin_fee)
        elif instance.transaction_type == 'PEMASUKAN':
            wallet.balance -= instance.amount
        wallet.save()
        instance.delete()

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

    def perform_create(self, serializer):
        from_wallet = serializer.validated_data['from_wallet']
        to_wallet = serializer.validated_data['to_wallet']
        amount = serializer.validated_data['amount']
        admin_fee = serializer.validated_data.get('admin_fee', Decimal(0))

        if from_wallet == to_wallet:
            raise serializers.ValidationError("Dompet asal dan tujuan tidak boleh sama.")
        if from_wallet.balance < (amount + admin_fee):
            raise serializers.ValidationError(f"Saldo di {from_wallet.name} tidak mencukupi.")

        from_wallet.balance -= (amount + admin_fee)
        to_wallet.balance += amount
        from_wallet.save()
        to_wallet.save()

        serializer.save(user=self.request.user)