from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Categories'


class Expense(models.Model):
    date = models.DateField(default=now)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.FloatField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.date} - {self.category} - {self.description} - {self.amount}'
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Expenses"
