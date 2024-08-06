# analysis/forms.py
from django import forms

PERIOD_CHOICES = [
    ('1d', '1 Day'),
    ('5d', '5 Days'),
    ('1mo', '1 Month'),
    ('3mo', '3 Months'),
    ('6mo', '6 Months'),
    ('1y', '1 Year'),
    ('2y', '2 Years'),
    ('5y', '5 Years'),
    ('ytd', 'Year to Date'),
    ('max', 'Max')
]

class TickerForm(forms.Form):
    tickers = forms.CharField(
        label='Enter Ticker Symbols (comma-separated)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TCS.NS, NBCC.NS'})
    )
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        label='Select Period',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
