# stocks/urls.py
from django.urls import path
from .views import StockListView, StockCreateView, StockUpdateView, StockDeleteView, StockReportView

urlpatterns = [
    path('', StockListView.as_view(), name='stock_list'),
    path('add/', StockCreateView.as_view(), name='stock_add'),
    path('edit/<int:pk>/', StockUpdateView.as_view(), name='stock_edit'),
    path('delete/<int:pk>/', StockDeleteView.as_view(), name='stock_delete'),
    path('report/', StockReportView.as_view(), name='stock_report'),
]
