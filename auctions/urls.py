from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("listingPage/<int:listing_id>", views.listingPage, name="listingPage"),
    path("active_watchlist", views.active_watchlist, name="active_watchlist"),
    path("ended_watchlist", views.ended_watchlist, name="ended_watchlist"),
    path("addItem/<int:item_id>", views.addItem, name="addItem"),
    path("removeItem/<int:item_id>", views.removeItem, name="removeItem"),
    path("bid_on/<int:item_id>", views.bid_on, name="bid_on"),
    path("end_auction/<int:item_id>", views.end_auction, name="end_auction"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("category/<str:category>", views.category, name="category")
]