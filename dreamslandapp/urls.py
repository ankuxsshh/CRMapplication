from django.urls import path
from . import views  

urlpatterns = [
    path('', views.loginpage, name='loginpage'),
    path('login', views.login, name='login'),
    path('admindashboard', views.admindashboard, name='admindashboard'),
    path('analytics', views.analytics, name='analytics'),
]
