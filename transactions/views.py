from datetime import datetime
from http.client import responses

from django.db.models import Sum
from django.db.models.fields import return_None
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from unicodedata import category

from .models import Transaction, Category, Wallet, Payee, Budget, FinancialGoal, Debt, Transfer
from django.contrib import messages
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
    fields = ['transaction_date', 'wallet', 'category', 'payee', 'amount', 'admin_fee', 'transaction_type', 'notes']
    template_name = 'transactions/transaction_form.html'

    def get_success_url(self):
        return reverse_lazy('transaction_list')

    def form_valid(self, form):
        old_transaction = self.get_object()

        self.object = form.save(commit=False)

        old_wallet = old_transaction.wallet
        if old_transaction.transaction_type == 'PENGELUARAN':
            old_wallet.balance += (old_transaction.amount + old_transaction.admin_fee)
        elif old_transaction.transaction_type == 'PEMASUKAN':
            old_wallet.balance -= old_transaction.amount

        if old_wallet.pk != self.object.wallet.pk:
            old_wallet.save()

        new_wallet = self.object.wallet
        if self.object.transaction_type == 'PENGELUARAN':
            new_wallet.balance -= (self.object.amount + self.object.admin_fee)
        elif self.object.transaction_type == 'PEMASUKAN':
            new_wallet.balance += self.object.amount
        new_wallet.save()

        self.object.save()

        return redirect(self.get_success_url())


class BudgetListView(ListView):
    model = Budget
    template_name = 'transactions/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        today = datetime.today()
        first_day_of_month = today.replace(day=1)
        return Budget.objects.filter(month__gte=first_day_of_month).order_by('month', 'category__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = context['budgets']

        for budget in budgets:
            spent = Transaction.objects.filter(
                category=budget.category,
                transaction_type='PENGELUARAN',
                transaction_date__year=budget.month.year,
                transaction_date__month=budget.month.month,
            ).aggregate(total_spent=Sum('amount'))['total_spent'] or Decimal(0)

            budget.spent = spent
            budget.remaining = budget.amount - spent
            budget.percentage = int((spent / budget.amount) * 100) if budget.amount > 0 else 0

        context['budgets'] = budgets
        return context


class BudgetCreateView(CreateView):
    model = Budget
    fields = ['category', 'amount', 'month']
    template_name = 'transactions/budget_form.html'
    success_url = reverse_lazy('budget_list')

class FinancialGoalListView(ListView):
    model = FinancialGoal
    template_name = 'transactions/goal_list.html'
    context_object_name = 'goals'
    ordering = ['target_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(wallet_type='ASET')
        return context

class FinancialGoalCreateView(CreateView):
    model = FinancialGoal
    fields = ['name', 'target_amount', 'target_date']
    template_name = 'transactions/goal_form.html'
    success_url = reverse_lazy('goal_list')

def add_saving_to_goal(request, pk):
    goal = FinancialGoal.objects.get(pk=pk)
    if request.method == 'POST':
        amount_to_add = Decimal(request.POST.get('amount'))
        souce_wallet_id = request.POST.get('source_wallet')
        source_wallet = Wallet.objects.get(pk=souce_wallet_id)

        if source_wallet.balance >= amount_to_add:
            saving_category, _ = Category.objects.get_or_create(name='Tabungan Tujuan')

            Transaction.objects.create(
                wallet=source_wallet,
                category=saving_category,
                amount=amount_to_add,
                transaction_type='PENGELUARAN',
                transaction_date=datetime.today(),
                notes=f"Menabung untuk {goal.name}"
            )

            source_wallet.balance -= amount_to_add
            source_wallet.save()

            goal.current_amount += amount_to_add
            goal.save()

    return redirect(reverse('goal_list'))

class DebtListView(ListView):
    model = Debt
    template_name = 'transactions/debt_list.html'
    context_object_name = 'debts'
    ordering = ['due_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(wallet_type='ASET')
        return context

class DebtCreateView(CreateView):
    model = Debt
    fields = ['lender_name', 'initial_amount', 'due_date', 'notes']
    template_name = 'transactions/debt_form.html'
    success_url = reverse_lazy('debt_list')

def pay_debt(request, pk):
    debt = Debt.objects.get(pk=pk)
    if request.method == 'POST':
        amount_to_pay = Decimal(request.POST.get('amount'))
        souce_wallet_id = request.POST.get('source_wallet')
        source_wallet = Wallet.objects.get(pk=souce_wallet_id)

        if source_wallet.balance >= amount_to_pay:
            debt_category, _ = Category.objects.get_or_create(name='Pembayaran Utang')
            payee, _ = Payee.objects.get_or_create(name=debt.lender_name)

            Transaction.objects.create(
                wallet=source_wallet,
                category=debt_category,
                payee=payee,
                amount=amount_to_pay,
                transaction_type='PENGELUARAN',
                transaction_date=datetime.today(),
                notes=f"Pembayaran utang kepada {debt.lender_name}"
            )

            source_wallet.balance -= amount_to_pay
            source_wallet.save()

            debt.current_balance -= amount_to_pay
            debt.save()

    return redirect(reverse('debt_list'))

class TransferListView(ListView):
    model = Transfer
    template_name = 'transactions/transfer_list.html'
    context_object_name = 'transfers'
    ordering = ['-transfer_date']

class TransferCreateView(CreateView):
    model = Transfer
    fields = ['from_wallet', 'to_wallet', 'amount', 'admin_fee', 'transfer_date', 'notes']
    template_name = 'transactions/transfer_form.html'
    success_url = reverse_lazy('transfer_list')

    def form_valid(self, form):
        transfer = form.save(commit=False)
        from_wallet = transfer.from_wallet
        to_wallet = transfer.to_wallet
        amount = transfer.amount
        admin_fee = transfer.admin_fee

        if from_wallet == to_wallet:
            messages.error(self.request, "Dompet asal dan tujuan tidak boleh sama.")
            return self.form_invalid(form)

        if from_wallet.balance < (amount + admin_fee):
            messages.error(self.request, f"Saldo di {from_wallet.name} tidak mencukupi.")
            return self.form_invalid(form)

        from_wallet.balance -= (amount + admin_fee)
        to_wallet.balance += amount

        from_wallet.save()
        to_wallet.save()

        transfer.save()
        return super().form_valid(form)