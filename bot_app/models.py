from django.db import models

# 1
class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100, default="Unknown")
    category = models.CharField(max_length=50, default="Motivation") 

    def __str__(self):
        return f"[{self.category}] {self.text[:30]}..."
# 2
class FavoriteQuote(models.Model):
    user_id = models.BigIntegerField()
    text = models.TextField()
    author = models.CharField(max_length=100, default="Unknown")
    category = models.CharField(max_length=50, default="Motivation") # Здесь тоже можно оставить

    def __str__(self):
        return f"User {self.user_id} favorite"