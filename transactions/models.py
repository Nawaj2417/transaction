from django.db import models

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    transaction_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f'TXNID{str(Transaction.objects.count() + 1).zfill(4)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.transaction_id



from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('manager', 'Manager'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
