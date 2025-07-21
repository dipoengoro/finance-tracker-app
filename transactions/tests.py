# file: transactions/tests.py
from django.test import TestCase
from django.db.utils import IntegrityError
from decimal import Decimal
from datetime import date
from .models import Category, Wallet, Budget


class ModelTests(TestCase):

    def test_create_category(self):
        """Tes pembuatan objek Category dan method __str__."""
        category = Category.objects.create(name="Makanan")
        self.assertEqual(str(category), "Makanan")

    def test_create_wallet(self):
        """Tes pembuatan objek Wallet dengan nilai default."""
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