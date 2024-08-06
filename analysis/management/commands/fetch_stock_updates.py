
# your_app_name/management/commands/fetch_stock_updates.py
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ...views import fetch_stock_data

class Command(BaseCommand):
    help = 'Fetch stock updates'

    def handle(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        tickers = ["NBCC", "GOOGL"]  # replace with your tickers
        period = "1d"  # replace with your period
        stock_data, company_info = fetch_stock_data(tickers, period)

        async_to_sync(channel_layer.group_send)(
            'stock_data_group',
            {
                'type': 'stock_data_update',
                'data': {
                    'stock_data': stock_data,
                    'company_info': company_info
                }
            }
        )
