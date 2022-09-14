from django.contrib import admin

from .models import *

class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starting_bid")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bid")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user")

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")
    
admin.site.register(Item, ItemAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)