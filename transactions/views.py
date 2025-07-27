import json
import csv
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Transaction, Category, Wallet, Payee, Budget, FinancialGoal, Debt, Transfer


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/index.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-transaction_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['categories'] = Category.objects.filter(user=user)
        context['wallets'] = Wallet.objects.filter(user=user)
        context['payees'] = Payee.objects.filter(user=user)
        return context


@login_required
def transaction_add(request):
    if request.method == 'POST':
        user = request.user
        wallet_id = request.POST.get('wallet')
        payee_name = request.POST.get('payee')
        category_id = request.POST.get('category')
        amount = Decimal(request.POST.get('amount'))
        admin_fee = Decimal(request.POST.get('admin_fee') or 0)
        trans_type = request.POST.get('transaction_type')
        trans_date = request.POST.get('transaction_date')
        notes = request.POST.get('notes')

        wallet = Wallet.objects.get(pk=wallet_id, user=user)
        category = Category.objects.get(pk=category_id, user=user)
        payee, _ = Payee.objects.get_or_create(name=payee_name, defaults={'user': user})

        Transaction.objects.create(
            user=user,
            wallet=wallet,
            payee=payee,
            category=category,
            amount=amount,
            admin_fee=admin_fee,
            transaction_type=trans_type,
            transaction_date=trans_date,
            notes=notes
        )

        total_expense = amount + admin_fee
        if trans_type == 'PENGELUARAN':
            wallet.balance -= total_expense
        elif trans_type == 'PEMASUKAN':
            wallet.balance += amount
        wallet.save()

    return redirect(reverse('transaction_list'))


@login_required
def transaction_delete(request, pk):
    if request.method == 'POST':
        user = request.user
        transaction = Transaction.objects.get(pk=pk, user=user)
        wallet = transaction.wallet
        amount = transaction.amount

        if transaction.transaction_type == 'PENGELUARAN':
            wallet.balance += amount
        elif transaction.transaction_type == 'PEMASUKAN':
            wallet.balance -= amount
        wallet.save()

        transaction.delete()

    return redirect(reverse('transaction_list'))


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    fields = ['transaction_date', 'wallet', 'category', 'payee', 'amount', 'admin_fee', 'transaction_type', 'notes']
    template_name = 'transactions/transaction_form.html'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

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


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'transactions/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        today = date.today()
        first_day_of_month = today.replace(day=1)
        return Budget.objects.filter(user=self.request.user, month__gte=first_day_of_month).order_by('month',
                                                                                                     'category__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = context['budgets']

        for budget in budgets:
            spent = Transaction.objects.filter(user=self.request.user, category=budget.category,
                                               transaction_type='PENGELUARAN', transaction_date__year=budget.month.year,
                                               transaction_date__month=budget.month.month, ).aggregate(
                total_spent=Sum('amount'))['total_spent'] or Decimal(0)

            budget.spent = spent
            budget.remaining = budget.amount - spent
            budget.percentage = int((spent / budget.amount) * 100) if budget.amount > 0 else 0

        context['budgets'] = budgets
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    fields = ['category', 'amount', 'month']
    template_name = 'transactions/budget_form.html'
    success_url = reverse_lazy('budget_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form


class FinancialGoalListView(LoginRequiredMixin, ListView):
    model = FinancialGoal
    template_name = 'transactions/goal_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user).order_by('target_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(wallet_type='ASET', user=self.request.user)
        return context


class FinancialGoalCreateView(LoginRequiredMixin, CreateView):
    model = FinancialGoal
    fields = ['name', 'target_amount', 'target_date']
    template_name = 'transactions/goal_form.html'
    success_url = reverse_lazy('goal_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def add_saving_to_goal(request, pk):
    user = request.user
    goal = FinancialGoal.objects.get(pk=pk, user=user)
    if request.method == 'POST':
        amount_to_add = Decimal(request.POST.get('amount'))
        souce_wallet_id = request.POST.get('source_wallet')
        source_wallet = Wallet.objects.get(pk=souce_wallet_id, user=user)

        if source_wallet.balance >= amount_to_add:
            saving_category, _ = Category.objects.get_or_create(name='Tabungan Tujuan', user=user)

            Transaction.objects.create(user=user, wallet=source_wallet, category=saving_category, amount=amount_to_add,
                                       transaction_type='PENGELUARAN', transaction_date=datetime.today(),
                                       notes=f"Menabung untuk {goal.name}")

            source_wallet.balance -= amount_to_add
            source_wallet.save()

            goal.current_amount += amount_to_add
            goal.save()

    return redirect(reverse('goal_list'))


class DebtListView(LoginRequiredMixin, ListView):
    model = Debt
    template_name = 'transactions/debt_list.html'
    context_object_name = 'debts'

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user).order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(wallet_type='ASET', user=self.request.user)
        return context


class DebtCreateView(LoginRequiredMixin, CreateView):
    model = Debt
    fields = ['lender_name', 'initial_amount', 'due_date', 'notes']
    template_name = 'transactions/debt_form.html'
    success_url = reverse_lazy('debt_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def pay_debt(request, pk):
    user = request.user
    debt = Debt.objects.get(pk=pk, user=user)
    if request.method == 'POST':
        amount_to_pay = Decimal(request.POST.get('amount'))
        souce_wallet_id = request.POST.get('source_wallet')
        source_wallet = Wallet.objects.get(pk=souce_wallet_id, user=user)

        if source_wallet.balance >= amount_to_pay:
            debt_category, _ = Category.objects.get_or_create(name='Pembayaran Utang', user=user)
            payee, _ = Payee.objects.get_or_create(name=debt.lender_name, user=user)

            Transaction.objects.create(user=user, wallet=source_wallet, category=debt_category, payee=payee,
                                       amount=amount_to_pay, transaction_type='PENGELUARAN',
                                       transaction_date=datetime.today(),
                                       notes=f"Pembayaran utang kepada {debt.lender_name}")

            source_wallet.balance -= amount_to_pay
            source_wallet.save()

            debt.current_balance -= amount_to_pay
            debt.save()

    return redirect(reverse('debt_list'))


class TransferListView(LoginRequiredMixin, ListView):
    model = Transfer
    template_name = 'transactions/transfer_list.html'
    context_object_name = 'transfers'

    def get_queryset(self):
        return Transfer.objects.filter(user=self.request.user).order_by('-transfer_date')


class TransferCreateView(LoginRequiredMixin, CreateView):
    model = Transfer
    fields = ['from_wallet', 'to_wallet', 'amount', 'admin_fee', 'transfer_date', 'notes']
    template_name = 'transactions/transfer_form.html'
    success_url = reverse_lazy('transfer_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_wallets = Wallet.objects.filter(user=self.request.user)
        form.fields['from_wallet'].queryset = user_wallets
        form.fields['to_wallet'].queryset = user_wallets
        return form


@login_required
def dashboard_view(request):
    user = request.user
    latest_transaction = Transaction.objects.filter(user=user).order_by('-transaction_date').first()

    if latest_transaction:
        relevant_date = latest_transaction.transaction_date
    else:
        relevant_date = date.today()

    first_day_of_month = relevant_date.replace(day=1)

    total_assets = Wallet.objects.filter(user=user, wallet_type='ASET').aggregate(total=Sum('balance'))['total'] or 0
    total_liabilities = Debt.objects.filter(user=user).aggregate(total=Sum('current_balance'))['total'] or 0

    income_this_month = \
        Transaction.objects.filter(user=user, transaction_type='PEMASUKAN', transaction_date__gte=first_day_of_month,
                                   transaction_date__month=first_day_of_month.month).aggregate(total=Sum('amount'))[
            'total'] or 0

    expense_this_month = \
        Transaction.objects.filter(user=user, transaction_type='PENGELUARAN', transaction_date__gte=first_day_of_month,
                                   transaction_date__month=first_day_of_month.month).aggregate(total=Sum('amount'))[
            'total'] or 0

    expense_by_category = Transaction.objects.filter(user=user, transaction_type='PENGELUARAN',
                                                     transaction_date__gte=first_day_of_month).values(
        'category__name').annotate(total=Sum('amount')).order_by('-total')

    chart_labels = [item['category__name'] for item in expense_by_category]
    chart_data = [float(item['total']) for item in expense_by_category]

    context = {'total_assets': total_assets, 'total_liabilities': total_liabilities,
               'net_worth': total_assets - total_liabilities, 'income_this_month': income_this_month,
               'expense_this_month': expense_this_month, 'chart_labels': json.dumps(chart_labels),
               'chart_data': json.dumps(chart_data), }
    return render(request, 'transactions/dashboard.html', context)


@login_required
def export_transactions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaksi.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tanggal', 'Tipe', 'Penerima/Tujuan', 'Kategori', 'Jumlah', 'Biaya Admin', 'Dompet', 'Catatan'])

    transactions = Transaction.objects.filter(user=request.user).order_by('transaction_date')

    for tx in transactions:
        writer.writerow([
            tx.transaction_date,
            tx.get_transaction_type_display(),
            tx.payee.name if tx.payee else '',
            tx.category.name if tx.category else '',
            tx.amount,
            tx.admin_fee,
            tx.wallet.name,
            tx.notes
        ])

    return response

class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'transactions/wallet_list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    fields = ['name', 'wallet_type', 'balance']
    template_name = 'transactions/wallet_form.html'
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class WalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Wallet
    fields = ['name', 'wallet_type', 'balance']
    template_name = 'transactions/wallet_form.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

class WalletDeleteView(LoginRequiredMixin, DeleteView):
    model = Wallet
    template_name = 'transactions/wallet_confirm_delete.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)