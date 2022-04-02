from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buy", views.buy, name='buy'),
    path("history", views.history, name='history'),
    path("login", views.login, name='login'),
    path("logout", views.logout, name='logout'),
    path("currency", views.currency, name='currency'),
    path("crypto", views.crypto, name='crypto'),
    path("quote", views.quote, name='quote'),
    path("register", views.register, name='register'),
    path("sell", views.sell, name='sell'),
    path("add", views.add, name='add'),
]

handler404 = "practice.views.handler404"
handler400 = "practice.views.handler400"
handler500 = "practice.views.handler500"
handler403 = "practice.views.handler403"
