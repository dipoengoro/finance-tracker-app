from django.views.generic import ListView
from .models import Transaction

class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/index.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date']