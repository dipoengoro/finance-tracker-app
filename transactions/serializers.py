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
    class Meta:
        model = Transaction
        fields = '__all__'