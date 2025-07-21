from http.client import responses

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
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
        category_name = request.POST.get('category')
        amount = Decimal(request.POST.get('amount'))
        trans_type = request.POST.get('transaction_type')
        trans_date = request.POST.get('transaction_date')

        wallet = Wallet.objects.get(pk=wallet_id)
        category, _ = Category.objects.get_or_create(name=category_name)
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

    return redirect(reverse('transaction_list'))

def transaction_delete(request, pk):
    if request.method == 'POST':
        transaction = Transaction.objects.get(pk=pk)
        wallet = transaction.wallet
        amount = transaction.amount

        if transaction.transaction_type == 'PENGELUARAN':
            wallet.balance += amount
        elif transaction.transaction_type == 'PEMASUKAN':
            wallet.balance -= amount
        wallet.save()

        transaction.delete()

    return redirect(reverse('transaction_list'))

class TransactionUpdateView(UpdateView):
    model = Transaction
    fields = ['transaction_date', 'wallet', 'category', 'payee', 'amount', 'transaction_type', 'notes']
    template_name = 'transactions/transaction_form.html'

    def get_success_url(self):
        return reverse_lazy('transaction_list')

    def form_valid(self, form):
        old_transaction = Transaction.objects.get(pk=self.object.pk)
        old_wallet = old_transaction.wallet
        old_amount = old_transaction.amount

        if old_transaction.transaction_type == 'PENGELUARAN':
            old_wallet.balance += old_amount
        elif old_transaction.transaction_type == 'PEMASUKAN':
            old_wallet.balance -= old_amount
        old_wallet.save()

        response = super().form_valid(form)

        new_transaction = self.object
        new_wallet = new_transaction.wallet
        new_amount = new_transaction.amount

        if new_transaction.transaction_type == 'PENGELUARAN':
            new_wallet.balance -= new_amount
        elif new_transaction.transaction_type == 'PEMASUKAN':
            new_wallet.balance += new_amount
        new_wallet.save()

        return response