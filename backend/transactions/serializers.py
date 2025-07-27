from rest_framework import serializers
from .models import Category, Wallet, Payee, Transaction, Budget, FinancialGoal, Debt, Transfer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'wallet_type', 'balance']

class PayeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payee
        fields = ['id', 'name']

class TransactionSerializer(serializers.ModelSerializer):
    wallet = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    payee = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class FinancialGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialGoal
        fields = '__all__'

class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = '__all__'

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'