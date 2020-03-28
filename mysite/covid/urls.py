from django.urls import path
from . import views

app_name = 'covid'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
