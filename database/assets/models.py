from django.db import models

class Asset(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('symbol', 'type')

    def __str__(self):
        return f"Asset(symbol={self.symbol}, type={self.type})"
    
class Equity(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='equity')
    company_name = models.CharField(max_length=150)
    exchange = models.CharField(max_length=25)
    currency = models.CharField(max_length=3, null=True, blank=True)
    industry = models.CharField(max_length=50, default='NULL')
    description = models.TextField(null=True, blank=True)
    market_cap = models.IntegerField(null=True, blank=True)
    shares_outstanding = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Equity(company_name={self.company_name}, exchange={self.exchange})"

class Commodity(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='commodity')
    commodity_name = models.CharField(max_length=25)
    base_future_code = models.CharField(max_length=10)
    expiration_date = models.DateTimeField()
    industry = models.CharField(max_length=50, default='NULL')
    exchange = models.CharField(max_length=25, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commodity(commodity_name={self.commodity_name}, base_future_code={self.base_future_code})"

class Cryptocurrency(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='cryptocurrency')
    cryptocurrency_name = models.CharField(max_length=50)
    circulating_supply = models.IntegerField(null=True, blank=True)
    market_cap = models.IntegerField(null=True, blank=True)
    total_supply = models.IntegerField(null=True, blank=True)
    max_supply = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cryptocurrency(name={self.cryptocurrency_name})"
