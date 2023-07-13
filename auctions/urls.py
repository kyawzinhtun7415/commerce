from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing_detail/<int:listing_id>", views.listing_detail, name="listing_detail"),
    path("toggle_watchlist/<int:listing_id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("place_bid/<int:listing_id>", views.place_bid, name='place_bid'),
    path("close_auction/<int:listing_id>", views.close_auction, name='close_auction'),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name='watchlist'),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category")
]
