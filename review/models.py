from django.db import models
from notification.models import Order
from accounts.models import CustomUser
from products.models import Product


class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)


class Rating(models.Model):
    rate = [(1, 'very bad'), (2, "bad"), (3, "normal"),(4, "good"),(5, "very good")]
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='Rating_user')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='Rating_product')
    score = models.CharField(max_length=1, choices=rate)
    

class CommentVote(models.Model):
    # user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    # comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    # vote = models.BooleanField()  # True: like, False: dislike

    pass

class Review(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


    pass # search for more info about confirmation of comment if user was bought product or not.

