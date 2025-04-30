import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

from django.shortcuts import render
from .models import Stock, StockHistory
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import StockForm, StockCreateForm , FilterForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .utils import (
    get_last_n_days_history,
    compute_rsi,
    compute_cumulative_return,
    compute_average_return
)


def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stocks/stock_list.html', {'stocks': stocks})

def update_stock_data(ticker):
    data = yf.Ticker(ticker).info
    price = data.get('regularMarketPrice')
    volume = data.get('volume')

    Stock.objects.update_or_create(
        ticker=ticker,
        defaults={'price': price, 'volume': volume}
    )

def update_historical_data(symbol, period=30):
    # Remove trailing 'd' if present and convert to int
    if isinstance(period, str):
        period = int(period.rstrip('d'))
    else:
        period = int(period)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period * 5)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    data = yf.download(symbol, start=start_date_str, end=end_date_str)
    
    # Get or create the Stock object
    stock_obj, created = Stock.objects.get_or_create(ticker=symbol)
    
    for date, row in data.iterrows():
        # Extract the 'Close' price
        price = row['Close']
        # If price is a Series (e.g., from a MultiIndex), take the first element
        if isinstance(price, pd.Series):
            price = price.iloc[0]
        
        # Extract volume and convert to int. Use iloc[0] if it's a Series.
        vol = row['Volume']
        if isinstance(vol, pd.Series):
            vol = int(vol.iloc[0])
        else:
            vol = int(vol)
        
        # Now update or create the historical record
        StockHistory.objects.update_or_create(
            stock=stock_obj,
            date=date.date(),  # Convert Timestamp to date
            defaults={'price': price, 'volume': vol}
        )
        
def stock_history_view(request, ticker):
    stock_obj = Stock.objects.get(ticker=ticker)
    history = stock_obj.history.all().order_by('date')
    return render(request, 'stocks/history.html', {'stock': stock_obj, 'history': history})

class StockListView(ListView):
    model = Stock
    template_name = 'stocks/stock_list.html'

class StockCreateView(CreateView):
    model = Stock
    form_class = StockCreateForm
    template_name = 'stocks/stock_form.html'
    success_url = reverse_lazy('stock_list')

    def form_valid(self, form):
        # Get the unsaved stock instance
        self.object = form.save(commit=False)
        ticker = self.object.ticker
        
        # Fetch current data from Yahoo Finance using yfinance
        data = yf.Ticker(ticker).info
        # Set price and volume; you might want to handle cases where these are not available
        self.object.price = data.get('regularMarketPrice') or 0
        self.object.volume = data.get('volume') or 0
        self.object.save()
        
        # Retrieve the number of historical days from the extra form field
        historical_days = form.cleaned_data.get('historical_days')
        period = f"{historical_days}d"
        # Update historical data for the stock
        update_historical_data(ticker, period)
        
        return HttpResponseRedirect(self.get_success_url())

class StockUpdateView(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'stocks/stock_form.html'
    success_url = reverse_lazy('stock_list')

class StockDeleteView(DeleteView):
    model = Stock
    template_name = 'stocks/stock_confirm_delete.html'
    success_url = reverse_lazy('stock_list')
    
    

def calculate_5day_cumulative_return(stock):
    history_qs = stock.history.order_by('-date')[:5]
    if len(history_qs) < 5:
        return None
    prices = [record.price for record in history_qs]
    cum_return = (prices[0] - prices[-1]) / prices[-1]
    return cum_return

def calculate_rsi(stock, period=14):
    history_qs = stock.history.order_by('date')[:(period+1)]
    if len(history_qs) < period+1:
        return None
    prices = pd.Series([record.price for record in history_qs])
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain[1:].mean()
    avg_loss = loss[1:].mean()
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

class StockReportView(TemplateView):
    template_name = 'stocks/stock_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_return_min = self.request.GET.get('min_return')
        filter_return_max = self.request.GET.get('max_return')

        filter_rsi_max = self.request.GET.get('max_rsi')
        filter_rsi_min = self.request.GET.get('min_rsi')

        
        stocks = Stock.objects.all()
        stock_data = []
        for stock in stocks:
            cum_return = calculate_5day_cumulative_return(stock)
            rsi = calculate_rsi(stock)
            stock_data.append({
                'ticker': stock.ticker,
                'price': stock.price,
                'volume': stock.volume,
                'five_day_return': cum_return,
                'rsi': rsi,
            })
        
        # Apply filters if provided
        if filter_return_min:
            try:
                filter_return = float(filter_return_min)
                stock_data = [s for s in stock_data if s['five_day_return'] is not None and s['five_day_return'] >= filter_return]
            except ValueError:
                pass
        if filter_return_max:
            try:
                filter_return = float(filter_return_max)
                stock_data = [s for s in stock_data if s['five_day_return'] is not None and s['five_day_return'] <= filter_return]
            except ValueError:
                pass
        if filter_rsi_max:
            try:
                filter_rsi_max = float(filter_rsi_max)
                stock_data = [s for s in stock_data if s['rsi'] is not None and s['rsi'] <= filter_rsi_max]
            except ValueError:
                pass
        if filter_rsi_min:
            try:
                filter_rsi_min = float(filter_rsi_min)
                stock_data = [s for s in stock_data if s['rsi'] is not None and s['rsi'] >= filter_rsi_min]
            except ValueError:
                pass

        context['stock_data'] = stock_data
        return context
    
class StockListView(ListView):
    model = Stock
    template_name = 'stocks/stock_list.html'
    context_object_name = 'stocks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = FilterForm(self.request.GET or None)
        context['form'] = form
        
        stocks = Stock.objects.all()
        if form.is_valid():
            filter_option = form.cleaned_data.get('filter_option')
            if filter_option:
                filtered_stocks = []
                for stock in stocks:
                    df_10 = get_last_n_days_history(stock.id, 10)
                    df_5 = df_10.tail(5)
                    prices_10 = df_10['price'].tolist()
                    prices_5 = df_5['price'].tolist()
    
                    rsi_10 = compute_rsi(prices_10, period=10)
                    cum_ret_5 = compute_cumulative_return(prices_5)
                    avg_ret_5 = compute_average_return(prices_5)
    
                    if filter_option == 'rsi_lt_30' and rsi_10 is not None and rsi_10 < 30:
                        filtered_stocks.append(stock)
                    elif filter_option == 'rsi_gt_80' and rsi_10 is not None and rsi_10 > 80:
                        filtered_stocks.append(stock)
                    elif filter_option == 'cum_return_gt_0' and cum_ret_5 is not None and cum_ret_5 > 0:
                        filtered_stocks.append(stock)
                    elif filter_option == 'cum_return_lt_0' and cum_ret_5 is not None and cum_ret_5 < 0:
                        filtered_stocks.append(stock)
                    elif filter_option == 'avg_return_gt_0' and avg_ret_5 is not None and avg_ret_5 > 0:
                        filtered_stocks.append(stock)
                    elif filter_option == 'avg_return_lt_0' and avg_ret_5 is not None and avg_ret_5 < 0:
                        filtered_stocks.append(stock)
                stocks = filtered_stocks
        context['stocks'] = stocks
        return context

