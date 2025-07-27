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
    wallet = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    payee = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_date', 'transaction_type',
            'wallet', 'category', 'payee', 'amount', 'admin_fee', 'notes'
        ]