"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from stocks.views import stock_list , stock_history_view , StockListView, StockCreateView, StockUpdateView, StockDeleteView, StockReportView


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', views.index, name='index'),
    #path('', stock_list, name='stock_list'),
    path('history/<str:ticker>/', stock_history_view, name='stock_history'),
    path('', StockListView.as_view(), name='stock_list'),
    path('add/', StockCreateView.as_view(), name='stock_add'),
    path('edit/<int:pk>/', StockUpdateView.as_view(), name='stock_edit'),
    path('delete/<int:pk>/', StockDeleteView.as_view(), name='stock_delete'),
    path('report/', StockReportView.as_view(), name='stock_report'),
]
