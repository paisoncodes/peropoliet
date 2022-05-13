import secrets
from django.db import models

# Create your models here.
class PayWithCrypto(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField()
    amount = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=225)
    coin = models.CharField(max_length=225, default="USDC")
    reference = models.CharField(max_length=25)
    successful = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        while not self.reference:
            reference = secrets.token_urlsafe(16)
            if not PayWithCrypto.objects.filter(reference=reference).exists():
                self.reference = reference
        super().save(*args, **kwargs)
