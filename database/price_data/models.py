from django.db import models

class EquityBarData(models.Model):
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='equity_bardata')
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('asset', 'timestamp')

    def __str__(self):
        return f"EquityBarData(asset={self.asset}, timestamp={self.timestamp})"
    
class CommodityBarData(models.Model):
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='commodity_bardata')
    timestamp  = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('asset', 'timestamp')

    def __str__(self):
        return f"CommodityBarData(asset={self.asset}, timestamp={self.timestamp})"
    
class CryptocurrencyBarData(models.Model):
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='cryptocurrency_bardata')
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('asset', 'timestamp')

    def __str__(self):
        return f"CryptocurrencyBarData(asset={self.asset}, timestamp={self.timestamp})"


