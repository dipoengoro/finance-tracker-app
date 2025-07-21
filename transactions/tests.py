from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import date
from .models import Category, Wallet, Payee, Transaction, Budget


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