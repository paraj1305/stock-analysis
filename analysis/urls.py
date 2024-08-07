from django.urls import path
from . import views

urlpatterns = [
    path('stock-price/', views.stock_price_view, name='stock_price'),
]
