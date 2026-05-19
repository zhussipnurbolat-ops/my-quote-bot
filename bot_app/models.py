from django.db import models

class FavoriteQuote(models.Model):
    user_id = models.BigIntegerField()          
    text = models.TextField()                  
    author = models.CharField(max_length=255)   

    def __str__(self):
        return f"{self.author}: {self.text[:20]}..."