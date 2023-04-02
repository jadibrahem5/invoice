from django.db import models
import datetime
from django.contrib.auth.models import User



class Company(models.Model):
    # Basic Fields.
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    companyName = models.CharField(null=True, blank=True, max_length=200)
    address = models.CharField(null=True, blank=True, max_length=200)
    companyLogo  = models.ImageField(default='default_logo.jpg', upload_to='company_logos')
    postalCode = models.CharField(null=True, blank=True, max_length=10)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    email = models.EmailField(null=True, blank=True, max_length=100)
    taxID = models.CharField(null=True, blank=True, max_length=100)
    website = models.CharField(null=True, blank=True, max_length=100)

    class Meta:
        unique_together = ('user',)
    def __str__(self):
        return '{}'.format(self.companyName)


class Client(models.Model):
    name=models.CharField(null=True, blank=True, max_length=200)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    address = models.CharField(null=True, blank=True, max_length=200)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return '{}'.format(self.name)
class Product(models.Model):
    CURRENCY = [
    ('I', 'IQD'),
    ('$', 'USD'),
    ]

    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(choices=CURRENCY, default='I', max_length=100)

    #Related Fields
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)

class Invoice(models.Model):
    STATUS = [
    ('UNPAID', 'UNPAID'),
    ('PAID',  'PAID'),
    ]
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(choices=STATUS, default='UNPAID', max_length=100)
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    Client= models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField(Product, blank=True)


