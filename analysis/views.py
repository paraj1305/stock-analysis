import yfinance as yf
from django.shortcuts import render
from .forms import TickerForm
import plotly.graph_objs as go
from babel.numbers import format_number

def fetch_stock_data(tickers, period):
    stock_data = {}
    company_info = {}
    rolling_window_size = get_rolling_window_size(period)
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
      
         
        # Fetch dividends
        dividends = stock.dividends
        dividend_data = dividends.to_dict()
        company_info[ticker] = {**info, 'dividends': dividend_data}
        
        if not hist.empty:
            try:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                percentage_change = ((current_price - previous_price) / previous_price) * 100
                moving_average = hist['Close'].rolling(window=rolling_window_size).mean().iloc[-1]
                
                recent_high = hist['High'].rolling(window=rolling_window_size).max().iloc[-1]
                recent_low = hist['Low'].rolling(window=rolling_window_size).min().iloc[-1]
                stop_loss = recent_low
                resistance = recent_high
                
                # Create Plotly plot with candlestick chart
                fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                                     open=hist['Open'],
                                                     high=hist['High'],
                                                     low=hist['Low'],
                                                     close=hist['Close'],
                                                     name='Candlestick')])
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=rolling_window_size).mean(), mode='lines', name='Moving Average'))
                
                # Add horizontal lines for stop loss and resistance
                fig.add_hline(y=stop_loss, line=dict(color='red', dash='dash'), name='Stop Loss')
                fig.add_hline(y=resistance, line=dict(color='green', dash='dash'), name='Resistance')
                
                # Add volume bar chart
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2', opacity=0.3))
                fig.update_layout(yaxis2=dict(overlaying='y', side='right', showgrid=False, title='Volume'))

                plot_html = fig.to_html(full_html=False)
                
                stock_data[ticker] = {
                    'info': info,
                    'current_price': current_price,
                    'percentage_change': percentage_change,
                    'moving_average': moving_average,
                    'stop_loss': stop_loss,
                    'resistance': resistance,
                    'plot_html': plot_html,
                  
                }
            except Exception as e:
                stock_data[ticker] = {
                    'info': info,
                    'current_price': None,
                    'percentage_change': None,
                    'moving_average': None,
                    'stop_loss': None,
                    'resistance': None,
                    'error': str(e),
                    'plot_html': None
                }
        else:
            stock_data[ticker] = {
                'info': info,
                'current_price': None,
                'percentage_change': None,
                'moving_average': None,
                'stop_loss': None,
                'resistance': None,
                'error': 'No historical data available',
                'plot_html': None,
                
            }
    return stock_data, company_info

def stock_price_view(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            tickers = form.cleaned_data['tickers'].split(',')
            tickers = [ticker.strip() for ticker in tickers]
            period = form.cleaned_data['period']
            stock_data, company_info = fetch_stock_data(tickers, period)
            return render(request, 'analysis/analyze_stock.html', {'form': form, 'stock_data': stock_data, 'company_info': company_info})
    else:
        form = TickerForm()
   
    stock_data = None
    company_info = None
    
    tickers = {
        'NIFTY': '^NSEI',
        'Bank_NIFTY': '^NSEBANK',
        'SENSEX': '^BSESN'
    }
    
    data = {}
    for name, ticker in tickers.items():
        ticker_data = yf.Ticker(ticker).history(period="1d")
        if not ticker_data.empty:
            latest_data = ticker_data.iloc[-1]
            data[name] = {
                'current_value': latest_data['Close'],
                'change': latest_data['Close'] - latest_data['Open'],
                'open': latest_data['Open'],
                'high': latest_data['High'],
                'low': latest_data['Low']
            }
    context = {
        'form': form,
        'stock_data': stock_data,
        'company_info': company_info,
        'index_data': data
    }
    
    return render(request, 'analysis/analyze_stock.html', context)

def get_rolling_window_size(period):
    if period == '1d':
        return 1
    elif period == '5d':
        return 5
    elif period == '1mo':
        return 20  # Roughly 20 trading days in a month
    elif period == '3mo':
        return 60  # 3 months
    elif period == '6mo':
        return 120  # 6 months
    elif period == '1y':
        return 250  # Roughly 250 trading days in a year
    elif period == '2y':
        return 500  # 2 years
    elif period == '5y':
        return 1250  # 5 years
    elif period == 'ytd':
        return 180  # Year to date (approximation)
    elif period == 'max':
        return 2500  # Max period, can be adjusted based on max available data
    else:
        return 7  # default window size for unspecified periods
