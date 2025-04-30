from django.db import models

class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    
    class Meta:
        # The UNIQUE on ticker already creates an index under the hood.
        indexes = [
            # No extra indexes needed here beyond PK and unique
        ]

    def __str__(self):
        return self.ticker


class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history')
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            # Composite index on (stock_id, date DESC)
            models.Index(fields=['stock', '-date'], name='stock_id_date_idx'),
            # Single‐column index on date
            models.Index(fields=['date'], name='stockhistory_date_idx'),
        ]

    def __str__(self):
        return f"{self.stock.ticker} on {self.date}"