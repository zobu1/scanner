# stocks/forms.py
from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['ticker', 'price', 'volume']

class StockCreateForm(forms.ModelForm):
    # Extra field (not part of the model) for how many days of history to fetch.
    historical_days = forms.IntegerField(
        label="Number of historical days to retrieve", 
        min_value=1, 
        required=True
    )
    
    class Meta:
        model = Stock
        fields = ['ticker']  # Only the ticker is entered by the user.


FILTER_CHOICES = [
    ('rsi_lt_30', '10 day RSI < 30'),
    ('rsi_gt_80', '10 day RSI > 80'),
    ('cum_return_gt_0', '5 day cumulative return > 0'),
    ('cum_return_lt_0', '5 day cumulative return < 0'),
    ('avg_return_gt_0', '5 day average return > 0'),
    ('avg_return_lt_0', '5 day average return < 0'),
]

class FilterForm(forms.Form):
    filter_option = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        label="Select Filter"
    )