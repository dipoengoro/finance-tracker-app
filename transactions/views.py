from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from unicodedata import category

from .models import Transaction, Category, Wallet, Payee
from decimal import Decimal

class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/index.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['wallets'] = Wallet.objects.all()
        context['payees'] = Payee.objects.all()
        return context

def transaction_add(request):
    if request.method == 'POST':
        wallet_id = request.POST.get('wallet')
        payee_name = request.POST.get('payee')
        category_id = request.POST.get('category')
        amount = Decimal(request.POST.get('amount'))
        trans_type = request.POST.get('transaction_type')
        trans_date = request.POST.get('transaction_date')

        wallet = Wallet.objects.get(pk=wallet_id)
        category = Category.objects.get(pk=category_id)
        payee, _ = Payee.objects.get_or_create(name=payee_name)

        Transaction.objects.create(
            wallet=wallet,
            payee=payee,
            category=category,
            amount=amount,
            transaction_type=trans_type,
            transaction_date=trans_date,
        )

        if trans_type == 'PENGELUARAN':
            wallet.balance -= amount
        elif trans_type == 'PEMASUKAN':
            wallet.balance += amount
        wallet.save()

    return redirect(reverse('transactions_list'))