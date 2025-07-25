from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Wallet(models.Model):
    class WalletType(models.TextChoices):
        ASSET = 'ASET', 'Aset'
        LIABILITY = 'LIABILITAS', 'Liabilitas'

    name = models.CharField(max_length=100, unique=True)
    wallet_type = models.CharField(max_length=10, choices=WalletType.choices, default=WalletType.ASSET)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Payee(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'PEMASUKAN', 'Pemasukan'
        EXPENSE = 'PENGELUARAN', 'Pengeluaran'

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    admin_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=12, choices=TransactionType.choices)
    transaction_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.payee} - {self.amount}"

class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.DateField()

    class Meta:
        unique_together = ('category', 'month')

    def __str__(self):
        return f"Budget for {self.category.name} in {self.month.strftime('%B %Y')}"

class FinancialGoal(models.Model):
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    target_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def percentage_complete(self):
        if self.target_amount > 0:
            return int((self.current_amount / self.target_amount) * 100)
        return 0

class Debt(models.Model):
    lender_name = models.CharField(max_length=100)
    initial_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Utang kepada {self.lender_name}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.current_balance = self.initial_amount
        super().save(*args, **kwargs)


