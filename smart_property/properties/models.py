from django.db import models

class Property(models.Model):
    title = models.CharField(max_length=255)
    price = models.FloatField()
    area = models.FloatField()
    price_per_sqft = models.FloatField()

    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    property_type = models.CharField(max_length=50)
    bedroom_num = models.IntegerField()
    bathroom_num = models.IntegerField()
    balcony_num = models.IntegerField()

    furnished = models.CharField(max_length=50)
    age = models.IntegerField()
    total_floors = models.IntegerField()

    latitude = models.FloatField()
    longitude = models.FloatField()
