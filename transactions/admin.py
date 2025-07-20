from django.contrib import admin
from .models import Category, Wallet, Payee, Transaction

admin.site.register(Category)
admin.site.register(Wallet)
admin.site.register(Payee)
admin.site.register(Transaction)