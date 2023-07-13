from decimal import Decimal


from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Auction, WatchlistItem, Bid, Comment, Category
from .forms import AuctionForm


def index(request):
    active_auctions = Auction.objects.filter(active=True)
    return render(request, "auctions/index.html", 
                  {'active_auctions': active_auctions})


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            new_auction = form.save(commit=False)
            new_auction.owner = request.user
            new_auction.save()
            return redirect("index")
    else:
        form = AuctionForm()
    return render(request, "auctions/create_listing.html", {"form": form})

# list the detail of the listing
def listing_detail(request, listing_id):
    listing = get_object_or_404(Auction, pk=listing_id)

    is_in_watchlist = False
    # Check user authentication before querying the watchlist
    if request.user.is_authenticated:
        is_in_watchlist = WatchlistItem.objects.filter(user=request.user, auction=listing, is_added=True).exists()

    # check the winner
    winning_bid = listing.bids.order_by('-bid_price').first()
    has_won = winning_bid is not None and winning_bid.user == request.user and not listing.active

    # List the comments
    comments = listing.comments.order_by('-created_at')

    return render(request, "auctions/listing_detail.html", {
        'listing': listing,
        'is_in_watchlist': is_in_watchlist,
        'has won': has_won,
        'comments': comments
    })


# add or remove item to watchlist
@login_required
@require_POST
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Auction, pk=listing_id)
    watchlist_item, created = WatchlistItem.objects.get_or_create(user=request.user, auction=listing) 

    # if the item is not in watchlist, it will be added to watchlist
    if created:
        watchlist_item.is_added = True
    # if not, it will be removed (is_added will become true to false)
    else:
        watchlist_item.is_added = not watchlist_item.is_added

    watchlist_item.save()
    return redirect('listing_detail', listing_id=listing.id)

# place bid 
@login_required
@require_POST
def place_bid(request, listing_id):
    listing = get_object_or_404(Auction, pk=listing_id)
    bid = Decimal(request.POST['bid'])

    # if bid is less than the current bid, reject with error
    if bid <= listing.current_price:
        messages.error(request, 'Your bid must be greater than the current price.')
        return redirect('listing_detail', listing_id=listing.id)
    
    Bid.objects.create(bid_price=bid, user=request.user, auction=listing)
    listing.current_price = bid
    listing.save()

    return redirect('listing_detail', listing_id=listing.id) 

@login_required
@require_POST
def close_auction(request, listing_id):
    listing = get_object_or_404(Auction, pk=listing_id)

    if request.user != listing.owner:
        return HttpResponseForbidden("You're not the owner of this listing")

    listing.active = False
    listing.save()

    return redirect('listing_detail', listing_id=listing.id)

@login_required
@require_POST
def add_comment(request, listing_id):
    listing = get_object_or_404(Auction, pk=listing_id)
    comment = request.POST['comment']

    Comment.objects.create(text=comment, user=request.user, auction=listing)

    return redirect('listing_detail', listing_id=listing.id)

@login_required
def watchlist(request):
    watchlist = WatchlistItem.objects.filter(user=request.user, is_added=True)
    print(watchlist)
    return render(request, 'auctions/watchlist.html',
                    {'watchlist': watchlist}
                  )


def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', { 'categories' : categories })

def category(request, category_name):
    category = Category.objects.get(name=category_name)
    auctions = Auction.objects.filter(category=category, active=True)
    return render(request, 'auctions/category.html', {
        'category_name': category_name,
        'auctions': auctions
    } )