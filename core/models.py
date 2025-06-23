from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'

AMOUNT_TYPE_CHOICES = [
    ('USD', 'Dollars'),
    ('INR', 'Rupees'),
    ('EUR', 'Euros'),
    ('GBP', 'Pounds'),
    ('JPY', 'Yen'),
    ('CNY', 'Yuan'),
    ('CAD', 'Canadian Dollars'),
    ('AUD', 'Australian Dollars'),
]

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_type = models.CharField(max_length=10, choices=AMOUNT_TYPE_CHOICES, default='USD')

    def __str__(self):
        return f"{self.account_name} ({self.user.username})"

    class Meta:
        db_table = 'accounts'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=8, choices=TRANSACTION_TYPES)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} ({self.account.account_name})"

    class Meta:
        db_table = 'transactions'
