from django.db import models
from django.contrib.auth.models import User 

# UserHistory model
class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    restaurant_name = models.CharField(max_length=150)
    restaurant_type = models.CharField(max_length=100)
    rate = models.FloatField()
    num_of_ratings = models.IntegerField()
    avg_cost = models.FloatField()
    online_order = models.CharField(max_length=10)
    table_booking = models.CharField(max_length=10)
    cuisines_type = models.CharField(max_length=200)
    area = models.CharField(max_length=100)
    local_address = models.CharField(max_length=200)
    interaction_time = models.DateTimeField(auto_now_add=True)
    interaction_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.restaurant_name} - {self.user.username}"


# UserTable model
class UserTable(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    admin = models.BooleanField(default=False)  # Admin field to denote extra privileges

    def __str__(self):
        return self.user.username
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
    
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_input = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"