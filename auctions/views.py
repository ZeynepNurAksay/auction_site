from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.db.models import Max

from .models import Bid, Item, User, Watchlist, Comment

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'starting_bid', 'image', 'category', 'auction_end_date']
        exclude = ['user']
        widgets = {
            'auction_end_date': DateTimeInput()
        }
        

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = "Image Link:"
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

def index(request):
    for i in Item.objects.all():
        item = Item.objects.get(pk = i.id)
        bids = Bid.objects.filter(item = item).count()
        if bids != 0:
            max_bid = Bid.objects.filter(item = item).aggregate(mb = Max('bid'))
            item.starting_bid = max_bid['mb']
            item.save()

        end_date = getattr(item, 'auction_end_date')
        today = timezone.now()
        if end_date <= today:
            setattr(item, 'is_active', False)
            item.save()
    items = Item.objects.filter(
        is_active = True
    )
    return render(request, "auctions/index.html", {
        "items": items,
        "now":timezone.now()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            watchlist = Watchlist(user=user)
            watchlist.save()
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def createListing(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            end_date = form.cleaned_data.get("auction_end_date")
            today = timezone.now()
            if end_date < today:
                return render(request, "auctions/createListing.html", {
                    "message": "The end date should be later than today!",
                    "form": ItemForm()
                })
            starting_bid = form.cleaned_data.get("starting_bid")
            if starting_bid == 0 or starting_bid < 0:
                return render(request, "auctions/createListing.html", {
                    "message": "The minimum starting bid can be £0.01!",
                    "form": ItemForm()
                })
            item = form.save(commit=False)
            item.user = request.user
            item.save()

            bid = Bid(user=request.user, item=item, bid= item.starting_bid)
            bid.save()
            return HttpResponseRedirect(reverse('index'))
    return render(request, "auctions/createListing.html", {
        "form": ItemForm()
    })

@login_required(login_url='login')
def listingPage(request, listing_id):
    item = Item.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.get(user = request.user)
    in_watchlist = False
    comments = Comment.objects.filter(item = item)
    if item in watchlist.items.all():
        in_watchlist = True

    bids = Bid.objects.filter(item = item).count()
    if bids != 0:
        max_bid = Bid.objects.filter(item = item).aggregate(mb = Max('bid'))
        item.starting_bid = max_bid['mb']
        item.save()

    recently_created = False
    if bids == 1:
        recently_created = True

    user_wins = False
    try:
        bid = Bid.objects.get(user = request.user, item = item, bid = item.starting_bid)
        if bid != None:
            user_wins = True
    except Bid.DoesNotExist:
        user_wins = False
    
    return render(request, "auctions/listingPage.html", {
        "item":item,
        "now":timezone.now(),
        "in_watchlist":in_watchlist,
        "expired": item.is_active,
        "user_wins": user_wins,
        "bids":bids,
        "recently_created": recently_created,
        "comments": comments
    })

@login_required(login_url='login')
def active_watchlist(request):
    watchlist = Watchlist.objects.get(user = request.user)
    return render(request, "auctions/watchlist.html", {
        "items": watchlist.items.filter(is_active = True),
        "now":timezone.now()
    })

@login_required(login_url='login')
def ended_watchlist(request):
    watchlist = Watchlist.objects.get(user = request.user)
    return render(request, "auctions/watchlist.html", {
        "items": watchlist.items.filter(is_active = False),
        "now":timezone.now()
    })

@login_required(login_url='login')
def addItem(request, item_id):
    watchlist = Watchlist.objects.get(user = request.user)
    item = Item.objects.get(pk = item_id)
    watchlist.items.add(item)
    return HttpResponseRedirect(reverse("active_watchlist"))

@login_required(login_url='login')
def removeItem(request, item_id):
    watchlist = Watchlist.objects.get(user = request.user)
    item = Item.objects.get(pk = item_id)
    watchlist.items.remove(item)
    return HttpResponseRedirect(reverse("active_watchlist"))

@login_required(login_url='login')
def bid_on(request, item_id):
    item = Item.objects.get(pk = item_id)
    bids = Bid.objects.filter(item = item).count()
    if request.method == "POST":
        try:
            bid = Decimal(request.POST["bid"])
        except InvalidOperation:
            return render(request, "auctions/listingPage.html", {
                "item":item,
                "now":timezone.now(),
                "expired": item.is_active,
                "message": "Please enter a valid bid!",
                "bids":bids
            })
        
        if bid <= item.starting_bid:
            return render(request, "auctions/listingPage.html", {
                "item":item,
                "now":timezone.now(),
                "expired": item.is_active,
                "message": "Your bid must be greater than the current price!",
                "bids":bids
            })
            

        bid2 = Bid(user = request.user, item = item, bid = bid)
        bid2.save()

        max_bid = Bid.objects.filter(user = request.user).filter(item = item).aggregate(mb = Max('bid'))
        item.starting_bid = max_bid['mb']
        item.save()

        
        return HttpResponseRedirect(reverse("listingPage", kwargs={'listing_id': item_id}))
    else:
        return render(request, "auctions/listingPage.html", {
            "item":item,
            "now":timezone.now(),
            "expired": item.is_active,
            "bids":bids
        })

@login_required(login_url='login')
def end_auction(request, item_id):
    item = Item.objects.get(pk = item_id)
    item.is_active = False
    item.save()
    return HttpResponseRedirect(reverse("listingPage", kwargs={'listing_id': item_id}))

@login_required(login_url='login')
def comment(request, item_id):
    item = Item.objects.get(pk = item_id)
    bids = Bid.objects.filter(item = item).count()
    comment = request.POST["comment"]
    if  len(comment) <= 0:
            return render(request, "auctions/listingPage.html", {
                "item":item,
                "now":timezone.now(),
                "expired": item.is_active,
                "message": "Comment cannot be blank!",
                "bids":bids
            })
    comment = Comment(user = request.user, item = item, comment = comment)
    comment.save()
    return HttpResponseRedirect(reverse("listingPage", kwargs={'listing_id': item_id}))

def category(request, category):
    items = Item.objects.filter(
        category = category
    )
    return render(request, "auctions/category.html", {
        "items": items,
        "now":timezone.now()
    })