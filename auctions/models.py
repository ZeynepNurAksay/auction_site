from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY_CHOICES = (
    ('Toys and Games','Toys and Games'),
    ('Electronics', 'Electronics'),
    ('Fashion','Fashion'),
    ('Beauty and Personal Care','Beauty and Personal Care'),
    ('Furniture','Furniture'),
    ('Automobiles','Automobiles'),
    ('Household Products','Household Products')
)

class User(AbstractUser):
    pass

class Item(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(blank=True)
    category = models.CharField(max_length = 50, blank=True, choices=CATEGORY_CHOICES)
    auction_end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    

    def __str__(self):
        return f"{self.title}"
        
class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    items = models.ManyToManyField(Item, blank=True, related_name="items")
    def __str__(self):
        return f"{self.user.username}'s whatchlist"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids_item")
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.user.username}'s bid"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_user")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comments_item")
    comment = models.TextField()
    def __str__(self):
        return f"{self.user.username}'s comment"