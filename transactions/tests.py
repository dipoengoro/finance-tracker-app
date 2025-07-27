from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Category, Wallet, Payee, Transaction, Budget, Transfer

class BaseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_category(self):
        category = Category.objects.create(name="Makanan", user=self.user)
        self.assertEqual(str(category), "Makanan")

    def test_create_wallet(self):
        wallet = Wallet.objects.create(name="BCA", user=self.user)
        self.assertEqual(str(wallet), "BCA")
        self.assertEqual(wallet.wallet_type, 'ASET')
        self.assertEqual(wallet.balance, Decimal('0.00'))

    def test_create_budget(self):
        category = Category.objects.create(name="Transportasi", user=self.user)
        budget = Budget.objects.create(
            category=category,
            amount=Decimal('500000.00'),
            month=date(2025, 7, 1),
            user=self.user
        )
        expected_str = "Budget for Transportasi in July 2025"
        self.assertEqual(str(budget), expected_str)

    def test_budget_unique_together_constraint(self):
        category = Category.objects.create(name="Hiburan", user=self.user)
        month = date(2025, 8, 1)
        Budget.objects.create(category=category, amount=Decimal('300000.00'), month=month, user=self.user)
        with self.assertRaises(IntegrityError):
            Budget.objects.create(category=category, amount=Decimal('250000.00'), month=month, user=self.user)

    def test_create_payee(self):
        payee = Payee.objects.create(name="Toko Kelontong", user=self.user)
        self.assertEqual(str(payee), "Toko Kelontong")

    def test_create_transaction(self):
        wallet = Wallet.objects.create(name="OVO", user=self.user)
        payee = Payee.objects.create(name="GoFood", user=self.user)
        transaction = Transaction.objects.create(
            wallet=wallet,
            payee=payee,
            amount=Decimal('35000'),
            transaction_type='PENGELUARAN',
            transaction_date=date.today(),
            user=self.user
        )
        expected_str = f"GoFood - 35000"
        self.assertEqual(str(transaction), expected_str)

    def test_create_transfer(self):
        wallet_from = Wallet.objects.create(name="Jenius", user=self.user)
        wallet_to = Wallet.objects.create(name="Dana", user=self.user)
        transfer = Transfer.objects.create(
            from_wallet=wallet_from,
            to_wallet=wallet_to,
            amount=Decimal('100000'),
            transfer_date=date.today(),
            user=self.user
        )
        expected_str = "Transfer from Jenius to Dana"
        self.assertEqual(str(transfer), expected_str)


class TransactionViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.wallet = Wallet.objects.create(user=self.user, name="BCA", balance=Decimal('1000000'))
        self.category = Category.objects.create(user=self.user, name="Makanan")
        self.payee = Payee.objects.create(user=self.user, name="Warung Padang")

    def test_transaction_list_view(self):
        Transaction.objects.create(user=self.user, wallet=self.wallet, category=self.category, payee=self.payee,
            amount=Decimal('25000'), transaction_type='PENGELUARAN', transaction_date=date.today())

        response = self.client.get(reverse('transaction_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions/index.html')
        self.assertContains(response, "Warung Padang")  # Cek apakah data payee muncul
        self.assertEqual(len(response.context['transactions']), 1)

    def test_add_transaction(self):
        initial_transaction_count = Transaction.objects.filter(user=self.user).count()

        form_data = {'wallet': self.wallet.pk, 'category': self.category.pk, 'payee': self.payee.name,
            # Ingat, kita mengirim nama untuk get_or_create
            'amount': '50000', 'transaction_type': 'PENGELUARAN',
            'transaction_date': date.today().strftime('%Y-%m-%d'), }

        response = self.client.post(reverse('transaction_add'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transaction_list'))

        self.assertEqual(Transaction.objects.count(), initial_transaction_count + 1)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('950000'))

        def test_delete_transaction(self):
            expense = Transaction.objects.create(user=self.user, wallet=self.wallet, category=self.category, payee=self.payee,
                amount=Decimal('50000'), transaction_type='PENGELUARAN', transaction_date=date.today())
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
            expense = Transaction.objects.create(user=self.user, wallet=self.wallet, category=self.category, payee=self.payee,
                amount=Decimal('100000'), transaction_type='PENGELUARAN', transaction_date=date.today())
            self.wallet.balance -= Decimal('100000')
            self.wallet.save()

            form_data = {'wallet': self.wallet.pk, 'category': self.category.pk, 'payee': self.payee.pk,
                'amount': '75000',  # Ubah jumlah pengeluaran
                'transaction_type': 'PENGELUARAN', 'transaction_date': date.today().strftime('%Y-%m-%d'), }

            response = self.client.post(reverse('transaction_update', kwargs={'pk': expense.pk}), data=form_data)

            self.assertEqual(response.status_code, 302)  # Cek redirect
            expense.refresh_from_db()
            self.wallet.refresh_from_db()

            self.assertEqual(expense.amount, Decimal('75000'))
            self.assertEqual(self.wallet.balance, Decimal('925000'))


class BudgetViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(user=self.user, name="Makanan")
        self.wallet = Wallet.objects.create(user=self.user, name="BCA", balance=Decimal('1000000'))
        self.payee = Payee.objects.create(user=self.user, name="Supermarket")
        self.budget_month = date(2025, 7, 1)

    def test_budget_list_view(self):
        budget = Budget.objects.create(user=self.user, category=self.category, amount=Decimal('500000'), month=self.budget_month)

        Transaction.objects.create(user=self.user, wallet=self.wallet, category=self.category, payee=self.payee,
            amount=Decimal('100000'), transaction_type='PENGELUARAN', transaction_date=date(2025, 7, 15))

        Transaction.objects.create(user=self.user, wallet=self.wallet, category=self.category, payee=self.payee,
            amount=Decimal('50000'), transaction_type='PENGELUARAN', transaction_date=date(2025, 8, 1))

        response = self.client.get(reverse('budget_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transactions/budget_list.html')

        budget_in_context = response.context['budgets'][0]
        self.assertEqual(budget_in_context.spent, Decimal('100000'))
        self.assertEqual(budget_in_context.remaining, Decimal('400000'))
        self.assertEqual(budget_in_context.percentage, 20)

    def test_budget_create_view(self):
        form_data = {'category': self.category.pk, 'amount': '750000', 'month': '2025-08-01', }

        response = self.client.post(reverse('budget_create'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('budget_list'))
        self.assertTrue(Budget.objects.filter(amount=750000).exists())


class TransferViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.wallet_from = Wallet.objects.create(user=self.user, name="Mandiri", balance=Decimal('2000000'))
        self.wallet_to = Wallet.objects.create(user=self.user, name="GoPay", balance=Decimal('500000'))

    def test_transfer_create_view_success(self):
        form_data = {'user': self.user, 'from_wallet': self.wallet_from.pk, 'to_wallet': self.wallet_to.pk, 'amount': '100000',
            'admin_fee': '2500', 'transfer_date': date.today().strftime('%Y-%m-%d'), }

        response = self.client.post(reverse('transfer_create'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('transfer_list'))

        self.assertTrue(Transfer.objects.filter(user=self.user, amount=100000).exists())

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()
        self.assertEqual(self.wallet_from.balance, Decimal('1897500'))  # 2.000.000 - 100.000 - 2.500
        self.assertEqual(self.wallet_to.balance, Decimal('600000'))  # 500.000 + 100.000

    def test_transfer_insufficient_funds(self):
        initial_transfer_count = Transfer.objects.filter(user=self.user).count()

        form_data = {'user': self.user, 'from_wallet': self.wallet_from.pk, 'to_wallet': self.wallet_to.pk, 'amount': '3000000',
            'transfer_date': date.today().strftime('%Y-%m-%d'), }

        self.client.post(reverse('transfer_create'), data=form_data)

        self.assertEqual(Transfer.objects.filter(user=self.user).count(), initial_transfer_count)

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()
        self.assertEqual(self.wallet_from.balance, Decimal('2000000'))
        self.assertEqual(self.wallet_to.balance, Decimal('500000'))


class WalletViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.wallet = Wallet.objects.create(name="Dompet Utama", user=self.user)

    def test_wallet_list_view(self):
        response = self.client.get(reverse('wallet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.wallet.name)

    def test_wallet_create_view(self):
        response = self.client.post(reverse('wallet_create'),
                                    {'name': 'Dompet Baru', 'wallet_type': 'ASET', 'balance': '500000'})
        self.assertRedirects(response, reverse('wallet_list'))
        self.assertTrue(Wallet.objects.filter(name='Dompet Baru').exists())

    def test_wallet_update_view(self):
        response = self.client.post(reverse('wallet_update', kwargs={'pk': self.wallet.pk}),
                                    {'name': 'Dompet Ganti Nama', 'wallet_type': 'ASET',
                                        'balance': self.wallet.balance})
        self.assertRedirects(response, reverse('wallet_list'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.name, 'Dompet Ganti Nama')

    def test_wallet_delete_view(self):
        response = self.client.post(reverse('wallet_delete', kwargs={'pk': self.wallet.pk}))
        self.assertRedirects(response, reverse('wallet_list'))
        self.assertFalse(Wallet.objects.filter(pk=self.wallet.pk).exists())
