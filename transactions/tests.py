from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import date
from .models import Category, Wallet, Payee, Transaction, Budget, Transfer


class ModelTests(TestCase):

    def test_create_category(self):
        category = Category.objects.create(name="Makanan")
        self.assertEqual(str(category), "Makanan")

    def test_create_wallet(self):
        wallet = Wallet.objects.create(name="BCA")
        self.assertEqual(str(wallet), "BCA")
        self.assertEqual(wallet.wallet_type, 'ASET')
        self.assertEqual(wallet.balance, Decimal('0.00'))

    def test_create_budget(self):
        category = Category.objects.create(name="Transportasi")
        budget = Budget.objects.create(
            category=category,
            amount=Decimal('500000.00'),
            month=date(2025, 7, 1)
        )
        expected_str = "Budget for Transportasi in July 2025"
        self.assertEqual(str(budget), expected_str)
        self.assertEqual(budget.amount, Decimal('500000.00'))

    def test_budget_unique_together_constraint(self):
        category = Category.objects.create(name="Hiburan")
        month = date(2025, 8, 1)

        Budget.objects.create(category=category, amount=Decimal('300000.00'), month=month)

        with self.assertRaises(IntegrityError):
            Budget.objects.create(category=category, amount=Decimal('250000.00'), month=month)

    def test_create_payee(self):
        payee = Payee.objects.create(name="Toko Kelontong")
        self.assertEqual(str(payee), "Toko Kelontong")

    def test_create_transaction(self):
        wallet = Wallet.objects.create(name="OVO")
        payee = Payee.objects.create(name="GoFood")
        transaction = Transaction.objects.create(
            wallet=wallet,
            payee=payee,
            amount=Decimal('35000'),
            transaction_type='PENGELUARAN',
            transaction_date=date.today()
        )
        expected_str = f"GoFood - 35000"
        self.assertEqual(str(transaction), expected_str)

    def test_create_transfer(self):
        wallet_from = Wallet.objects.create(name="Jenius")
        wallet_to = Wallet.objects.create(name="Dana")
        transfer = Transfer.objects.create(
            from_wallet=wallet_from,
            to_wallet=wallet_to,
            amount=Decimal('100000'),
            transfer_date=date.today()
        )
        expected_str = "Transfer from Jenius to Dana"
        self.assertEqual(str(transfer), expected_str)


class TransactionViewTests(TestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(name="BCA", balance=Decimal('1000000'))
        self.category = Category.objects.create(name="Makanan")
        self.payee = Payee.objects.create(name="Warung Padang")

    def test_transaction_list_view(self):
        Transaction.objects.create(
            wallet=self.wallet,
            category=self.category,
            payee=self.payee,
            amount=Decimal('25000'),
            transaction_type='PENGELUARAN',
            transaction_date=date.today()
        )

        response = self.client.get(reverse('transaction_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions/index.html')
        self.assertContains(response, "Warung Padang")  # Cek apakah data payee muncul
        self.assertEqual(len(response.context['transactions']), 1)

    def test_add_transaction(self):
        initial_transaction_count = Transaction.objects.count()

        form_data = {
            'wallet': self.wallet.pk,
            'category': self.category.pk,
            'payee': self.payee.name,  # Ingat, kita mengirim nama untuk get_or_create
            'amount': '50000',
            'transaction_type': 'PENGELUARAN',
            'transaction_date': date.today().strftime('%Y-%m-%d'),
        }

        response = self.client.post(reverse('transaction_add'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transaction_list'))

        self.assertEqual(Transaction.objects.count(), initial_transaction_count + 1)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('950000'))

        def test_delete_transaction(self):
            expense = Transaction.objects.create(
                wallet=self.wallet, category=self.category, payee=self.payee,
                amount=Decimal('50000'), transaction_type='PENGELUARAN',
                transaction_date=date.today()
            )
            self.wallet.balance -= Decimal('50000')
            self.wallet.save()

            initial_balance = self.wallet.balance
            self.assertEqual(Transaction.objects.count(), 1)

            response = self.client.post(reverse('transaction_delete', kwargs={'pk': expense.pk}))

            self.assertEqual(response.status_code, 302)  # Cek redirect
            self.assertEqual(Transaction.objects.count(), 0)  # Cek data terhapus
            self.wallet.refresh_from_db()
            self.assertEqual(self.wallet.balance, initial_balance + expense.amount)

        def test_update_transaction(self):
            expense = Transaction.objects.create(
                wallet=self.wallet, category=self.category, payee=self.payee,
                amount=Decimal('100000'), transaction_type='PENGELUARAN',
                transaction_date=date.today()
            )
            self.wallet.balance -= Decimal('100000')
            self.wallet.save()

            form_data = {
                'wallet': self.wallet.pk,
                'category': self.category.pk,
                'payee': self.payee.pk,
                'amount': '75000',  # Ubah jumlah pengeluaran
                'transaction_type': 'PENGELUARAN',
                'transaction_date': date.today().strftime('%Y-%m-%d'),
            }

            response = self.client.post(reverse('transaction_update', kwargs={'pk': expense.pk}), data=form_data)

            self.assertEqual(response.status_code, 302)  # Cek redirect
            expense.refresh_from_db()
            self.wallet.refresh_from_db()

            self.assertEqual(expense.amount, Decimal('75000'))
            self.assertEqual(self.wallet.balance, Decimal('925000'))


class BudgetViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Makanan")
        self.wallet = Wallet.objects.create(name="BCA", balance=Decimal('1000000'))
        self.payee = Payee.objects.create(name="Supermarket")
        self.budget_month = date(2025, 7, 1)

    def test_budget_list_view(self):
        budget = Budget.objects.create(
            category=self.category,
            amount=Decimal('500000'),
            month=self.budget_month
        )

        Transaction.objects.create(
            wallet=self.wallet, category=self.category, payee=self.payee,
            amount=Decimal('100000'), transaction_type='PENGELUARAN',
            transaction_date=date(2025, 7, 15)
        )

        Transaction.objects.create(
            wallet=self.wallet, category=self.category, payee=self.payee,
            amount=Decimal('50000'), transaction_type='PENGELUARAN',
            transaction_date=date(2025, 8, 1)
        )

        response = self.client.get(reverse('budget_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions/budget_list.html')

        budget_in_context = response.context['budgets'][0]
        self.assertEqual(budget_in_context.spent, Decimal('100000'))
        self.assertEqual(budget_in_context.remaining, Decimal('400000'))
        self.assertEqual(budget_in_context.percentage, 20)

    def test_budget_create_view(self):
        form_data = {
            'category': self.category.pk,
            'amount': '750000',
            'month': '2025-08-01',
        }

        response = self.client.post(reverse('budget_create'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('budget_list'))
        self.assertTrue(Budget.objects.filter(amount=750000).exists())


class TransferViewTests(TestCase):
    def setUp(self):
        self.wallet_from = Wallet.objects.create(name="Mandiri", balance=Decimal('2000000'))
        self.wallet_to = Wallet.objects.create(name="GoPay", balance=Decimal('500000'))

    def test_transfer_create_view_success(self):
        form_data = {
            'from_wallet': self.wallet_from.pk,
            'to_wallet': self.wallet_to.pk,
            'amount': '100000',
            'admin_fee': '2500',
            'transfer_date': date.today().strftime('%Y-%m-%d'),
        }

        response = self.client.post(reverse('transfer_create'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfer_list'))

        self.assertTrue(Transfer.objects.filter(amount=100000).exists())

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()
        self.assertEqual(self.wallet_from.balance, Decimal('1897500'))  # 2.000.000 - 100.000 - 2.500
        self.assertEqual(self.wallet_to.balance, Decimal('600000'))  # 500.000 + 100.000

    def test_transfer_insufficient_funds(self):
        initial_transfer_count = Transfer.objects.count()

        form_data = {
            'from_wallet': self.wallet_from.pk,
            'to_wallet': self.wallet_to.pk,
            'amount': '3000000',  # Melebihi saldo
            'transfer_date': date.today().strftime('%Y-%m-%d'),
        }

        self.client.post(reverse('transfer_create'), data=form_data)

        self.assertEqual(Transfer.objects.count(), initial_transfer_count)

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()
        self.assertEqual(self.wallet_from.balance, Decimal('2000000'))
        self.assertEqual(self.wallet_to.balance, Decimal('500000'))