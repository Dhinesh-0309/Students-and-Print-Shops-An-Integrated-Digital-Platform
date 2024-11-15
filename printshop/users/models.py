from django.db import models
from django.contrib.auth.models import User
import datetime

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    opening_time = models.TimeField(default=datetime.time(9, 0))  # Set as a time object
    closing_time = models.TimeField(default=datetime.time(18, 0))  # Set as a time object
    landmark = models.CharField(max_length=255, default='Unknown Landmark')
    
    

    def __str__(self):
        return self.shop_name

class PrintRequest(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    pages = models.IntegerField()
    print_config = models.CharField(max_length=50)
    copies = models.IntegerField(default=1)
    start_page = models.IntegerField(null=True, blank=True)
    end_page = models.IntegerField(null=True, blank=True)
    unique_id = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Print Request by {self.student.username} for {self.shop.shop_name}"


class PrintCostConfig(models.Model):
    owner = models.OneToOneField(OwnerProfile, on_delete=models.CASCADE)
    color_print_cost = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)  # Default color cost
    black_white_print_cost = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)  # Default black & white cost

    def __str__(self):
        return f"Print Cost Config for {self.owner.shop_name}"    
    