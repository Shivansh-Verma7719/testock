from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import logout as logout_user
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime

from practice.models import Transactions, Users
from .forms import NewUserForm
from . import helpers
# Create your views here.


@login_required(login_url="login")
def index(request):
    """Show portfolio of stocks"""

    # Collecting the user id.
    user_id = request.session.get('user_id')
    if user_id is None:
        HttpResponseRedirect("login")

    # Gathering the portfolio of the user.
    stocks = Transactions.objects.values('symbol','name').filter(
        user_id=user_id).filter(type__contains="STOCKS").annotate(totalshares=Sum('shares')).order_by()

    coins = Transactions.objects.values('symbol','name').filter(
        user_id=user_id).filter(type__contains='CRYPTO').annotate(totalshares=Sum('shares')).order_by()

    # Gathering the cash of the user.
    cash = Users.objects.all().filter(id=user_id)[:1].get().cash

    # Finding the total amount of cash the user has(including the profits).
    nettotal = cash
    stocktotal = 0
    watchlist = []
    flag = False
    for stock in stocks:
        if stock["symbol"] != '':
            first = stock['symbol']
            flag =  True
            break
    if not flag:
        first = None
        
    for stock in stocks:
        if stock["symbol"] != '':
            stock['price'] = helpers.lookup(stock['symbol'])["price"]
            stocktotal += stock['price'] * stock['totalshares']
            watchlist.append(stock['symbol'])

    nettotal += stocktotal
    cryptototal = 0
    for coin in coins: 
        if coin['symbol'] != "":
            coin["price"] = helpers.lookupcryptobs(coin['symbol'])["price"]
            watchlist.append(coin['symbol']+'USD')
            cryptototal += coin['price'] * coin['totalshares']

    nettotal+=cryptototal
    stocktotal = round(stocktotal, 2)
    cryptototal = round(cryptototal, 2)

    # Displaying the portfolio of the user.
    return render(request, "practice/index.html", {
        'stocks': stocks,
        'first':first,
        'watchlist':watchlist,
        'nettotal': nettotal,
        'stocktotal': stocktotal,
        'cryptototal': cryptototal,
        'coins': coins,
        'cash': round(cash,3)
    })


@login_required
def buy(request):
    """Buy shares of stock"""

    if request.method == "POST":
        transact = request.POST["Type"]
        # Checking for stock transaction or crypto.
        if transact == "stock":
            sym = str(request.POST["symbol"])
            sym = sym.upper()

            # Ensuring that the shares are an integer.
            try:
                shares = int(request.POST["shares"])
            except:
                messages.error(request, "Shares must be an integer")
                return HttpResponseRedirect("buy")

            # Looking up the information about the stock.
            stock = helpers.lookup(sym)
 
            # Ensuring that the shares are a positive integer.
            if shares <= 0:
                messages.error(request, "Shares must be positive")
                return HttpResponseRedirect("buy")
            # Checking for valid stock symbol.
            if not stock:
                messages.error(request, "Enter valid stock symbol")
                return HttpResponseRedirect("buy")

            # Collecting the user id.
            userid = request.session.get("user_id")
            cash = Users.objects.all().filter(id=userid)[:1].get().cash

            # Extracting the information of the stock.
            stock_name = stock["name"]
            stock_price = stock["price"]
            # Calculating the total price of that stock.
            cost = stock_price * shares

            # Ensuring the user has that much cash available.
            if cash < cost:
                messages.error(
                    request, "You don't have enough money!")
                return HttpResponseRedirect("buy")

            # Calculating how much money will be left after the transaction.
            new_cash = cash - cost

            # Updating the cash avaliable to that user.
            Users.objects.filter(id=userid).update(cash=new_cash)

            user = Users.objects.get(id=userid)
            # Recording the transaction.
            f = Transactions(user_id=user, name=stock_name, shares=shares,
                             price=stock_price, type='BUY:STOCKS', symbol=sym, time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            f.save()

            return HttpResponseRedirect("/")
        else:
            coin_sym = str(request.POST["symbol"])
            coin_sym = coin_sym.upper()

            # Ensuring that the shares are an integer.
            try:
                shares = int(request.POST["shares"])
            except:
                messages.error(request, "Shares must be an integer")
                return HttpResponseRedirect("buy")

            # Looking up the information about the coin.
            coin = helpers.lookupcryptobs(coin_sym)

            # Ensuring that the shares are a positive integer.
            if shares <= 0:
                messages.error(request, "Shares must be positive")
                return HttpResponseRedirect("buy")

            # Checking for valid stock symbol.
            if not coin:
                messages.error(request, "Enter valid coin")
                return HttpResponseRedirect("buy")

            # Collecting the user id.
            userid = request.session.get("user_id")
            cash = Users.objects.all().filter(id=userid)[:1].get().cash

            # Extracting the information of the stock.
            coin_name = coin["name"]
            coin_price = coin["price"]

            # Calculating the total price of that stock.
            cost = coin_price * shares

            # Ensuring the user has that much cash available.
            if cash < cost:
                messages.error(
                    request, "You don't have enough money!")
                return HttpResponseRedirect("buy")

            # Calculating how much money will be left after the transaction.
            new_cash = cash - cost

            # Updating the cash avaliable to that user.
            Users.objects.filter(id=userid).update(cash=new_cash)

            user = Users.objects.get(id=userid)

            # Recording the transaction.
            f = Transactions(user_id=user, name=coin_name, shares=shares,
                             price=coin_price, type='BUY:CRYPTO', symbol=coin_sym, time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            f.save()

            return HttpResponseRedirect("/")
    else:
        # Displaying the form into which to enter the demand.
        return render(request, "practice/buy.html")


@login_required
def history(request):
    """Show history of transactions"""
    # Collecting the user id.
    user_id = request.session.get("user_id")
    # Extracting the transaction history of the user.
    transactions = Transactions.objects.filter(user_id=user_id)

    # Displaying the transaction history of the user.
    return render(request, "practice/history.html", {
        'transactions': transactions
    })


def login(request):
    """Log user in"""

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            rows = Users.objects.get(username=username)
            request.session["user_id"] = rows.id
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect("/")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "practice/login.html", context={"form": form})


def logout(request):
    """Log user out"""

    logout_user(request)
    return HttpResponseRedirect("login")


@login_required
def currency(request):
    """Get currency quote."""
    if request.method == "POST":
        currency = str(request.POST["currency"]).upper()
        currency_to = str(request.POST["currency_to"]).upper()

        # Looking up the information about the stock.
        rate = helpers.lookupcurrency(currency, currency_to)

        # Checking for invalid stock.
        if not rate:
            messages.error(request, "Enter valid currency")
            return HttpResponseRedirect("currency") 

        data = helpers.news(currency)
        art1 = data[2]
        art1.pop("source")
        art2 = data[0]
        art2.pop("source")
        art3 = data[4]
        art3.pop("source")

        # Displaying the quoted stock.
        return render(request, "practice/currency_past.html", {
            'currency': rate,
            'sym': currency,
            'sym_to': currency_to,
            'art1': art1,
            'art2': art2,
            'art3': art3
        })
    else:
        # Displaying the quote form.
        return render(request, "practice/currency.html")


@login_required
def crypto(request):
    """Get crypto quote."""
    if request.method == "POST":
        coin = str(request.POST["coin"]).upper()
        coin_to = str(request.POST["coin_to"]).upper()

        coin_lookup = helpers.lookupcrypto(coin, coin_to)

        # Checking for invalid stock.
        if not coin_lookup:
            messages.error(request, "Invalid coin or currency")
            return HttpResponseRedirect("crypto")

        data = helpers.news(coin)
        art1 = data[2]
        art1.pop("source")
        art2 = data[0]
        art2.pop("source")
        art3 = data[4]
        art3.pop("source")

        # Displaying the quoted stock.
        return render(request, "practice/crypted.html", {
            'coin': coin_lookup,
            "sym": coin,
            "sym_to": coin_to,
            'art1': art1,
            'art2': art2,
            'art3': art3
        })
    else:
        # Displaying the quote form.
        return render(request, "practice/crypto.html")


@login_required
def quote(request):
    """Get stock quote."""
    if request.method == "POST":
        sym = str(request.POST["symbol"]).upper()

        # Looking up the information about the stock.
        stock = helpers.lookup(sym)
        # Checking for invalid stock.
        if not stock:
            messages.error(request, "Invalid stock")
            return HttpResponseRedirect("quote")


        data = helpers.news(stock["name"])
        art1 = data[2]
        art1.pop("source")
        art2 = data[0]
        art2.pop("source")
        art3 = data[4]
        art3.pop("source")
    
        # Displaying the quoted stock.
        return render(request, "practice/quoted.html", {
            'stock': stock,
            'sym' :sym,
            'art1': art1,
            'art2': art2,
            'art3': art3})
    else:
        # Displaying the quote form.
        return render(request, "practice/quote.html")


def register(request):
    """Register user"""
    if request.method == "POST":
        form = NewUserForm(request.POST)
        print(form)
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        username = request.POST['username']
        users = Users.objects.values('username')
        for user in users:
            if user['username'] == username:
                messages.error(
                    request, "Username taken")
                return HttpResponseRedirect("register")
        if pass1 != pass2:
            messages.error(
                request, "Passwords do not match")
            return HttpResponseRedirect("register")
        if len(pass1) < 8:
            messages.error(
                request, "Passwords should have at least 8 charecters")
            return HttpResponseRedirect("register")
        if form.is_valid():
            user = form.save()
            f = Users(username=user.username, cash=10000)
            f.save()
            rows = Users.objects.get(username=user.username)
            request.session["user_id"] = rows.id
            auth_login(request, user)
            return HttpResponseRedirect("/")
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request, "practice/register.html", context={"register_form": form})


@login_required
def sell(request):
    """Sell shares of stock"""
    # Collecting the user id.
    
    if request.method == "POST":
        # Checking for stock transaction or crypto.
        if request.POST["Type"] == "stock":
            sym = request.POST["symbol"]

            shares = int(request.POST["shares"])
            if shares <= 0:
                messages.error(request, "Shares must be positive")
                return HttpResponseRedirect("sell")

            # Looking up the information about the stock.
            stock = helpers.lookup(sym)

            if not stock:
                messages.error(request, "Enter valid stock")
                return HttpResponseRedirect("sell")
            stock_price = stock["price"]
            stock_name = stock["name"]
            user_id = request.session.get("user_id")

            # Finding out the shares owned by the user
            shares_owned = Transactions.objects.filter(user_id=user_id).filter(
                symbol=sym).aggregate(Sum("shares"))["shares__sum"]

            # Checking if the user has the requested amount of shares.
            if shares_owned < shares:
                messages.error(
                    request, "You don't have enough shares of the company!")
                return HttpResponseRedirect("sell")

            # Calculating the price of the stock being sold.
            price = shares * stock_price

            user_id = request.session.get("user_id")
            # Finding the cash the user has.
            cur_cash = Users.objects.all().filter(id=user_id)[:1].get().cash

            # Updating the cash avaliable to that user.
            Users.objects.filter(id=user_id).update(cash=cur_cash+price)

            # Recording the transaction.
            user = Users.objects.get(id=user_id)
            f = Transactions(user_id=user, name=stock_name, shares=-shares,
                             price=stock_price, type='SELL, STOCKS', symbol=sym, time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            f.save()

            newshares = Transactions.objects.filter(user_id=user_id).filter(
                symbol=sym).aggregate(Sum("shares"))["shares__sum"]

            if newshares == 0:
                Transactions.objects.filter(
                    user_id=user_id).filter(symbol=sym).delete()
            return HttpResponseRedirect("/")
        else:
            coin_sym = request.POST["symbol"]

            shares = int(request.POST["shares"])
            if shares <= 0:
                messages.error(request, "Shares must be positive")
                return HttpResponseRedirect("sell")

            # Looking up the information about the stock.
            coin = helpers.lookupcryptobs(coin_sym)
            if not coin:
                messages.error(request, "Enter valid symbol")
                return HttpResponseRedirect("sell")
            coin_price = coin["price"]
            coin_name = coin["name"]

            user_id = request.session.get("user_id")
            # Finding out the shares owned by the user
            shares_owned = Transactions.objects.filter(user_id=user_id).filter(
                symbol=coin_sym).aggregate(Sum("shares"))["shares__sum"]
            # Checking if the user has the requested amount of shares.
            if shares_owned < shares:
                messages.error(
                    request, "You don't have enough coins!")
                return HttpResponseRedirect("sell")

            # Calculating the price of the stock being sold.
            price = shares * coin_price

            # Finding the cash the user has.
            cur_cash = Users.objects.all().filter(id=user_id)[:1].get().cash

            # Updating the cash avaliable to that user.
            Users.objects.filter(id=user_id).update(cash=cur_cash+price)

            # Recording the transaction.
            f = Transactions(user_id=Users.objects.get(id=user_id), name=coin_name, shares=-shares,
                             price=coin_price, type='SELL, CRYPTO', symbol=coin_sym , time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            f.save()

            newshares = Transactions.objects.filter(user_id=user_id).filter(
                symbol=coin_sym).aggregate(Sum("shares"))["shares__sum"]

            if newshares == 0:
                Transactions.objects.filter(
                    user_id=user_id).filter(symbol=coin_sym).delete()

            return HttpResponseRedirect("/")
    else:
        user_id = request.session.get("user_id")
        # Displaying the form into which to enter the demand.
        sym = Transactions.objects.values(
            'symbol').filter(user_id=user_id).annotate(totalshares = Sum('shares')).order_by('symbol')
            
        return render(request, "practice/sell.html", {'symbols': sym})


@login_required
def add(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        amount = request.POST["amount"]

        amount = float(amount)

        cur_cash = Users.objects.all().filter(id=user_id)[:1].get().cash

        Users.objects.filter(id=user_id).update(cash=cur_cash+amount)

        user = Users.objects.get(id=user_id)
        f = Transactions(user_id=user, name='N.A', shares=0,
                         price=0, type='MONEY ADDED', symbol='N.A', time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        f.save()

        return HttpResponseRedirect("/")
    else:
        return render(request, "practice/add.html")


def handler404(request, exception):
    return HttpResponseNotFound(request, '404.html')


def handler500(request):
    return HttpResponseServerError(request, '500.html')


def handler403(request, exception):
    return HttpResponseForbidden(request, '403.html')


def handler400(request, exception):
    return HttpResponseBadRequest(request, '400.html')


def csrf_failure(request, reason=""):
    
    return render(request,'403_csrf.html')
