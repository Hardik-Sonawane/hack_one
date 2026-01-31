import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_property.settings")
django.setup()

from properties.models import Property

df = pd.read_csv("data/mumbai_houses.csv")

for _, row in df.iterrows():
    Property.objects.create(
        title=row['title'],
        price=row['price'],
        area=row['area'],
        price_per_sqft=row['price_per_sqft'],
        locality=row['locality'],
        city=row['city'],
        property_type=row['property_type'],
        bedroom_num=row['bedroom_num'],
        bathroom_num=row['bathroom_num'],
        balcony_num=row['balcony_num'],
        furnished=row['furnished'],
        age=row['age'],
        total_floors=row['total_floors'],
        latitude=row['latitude'],
        longitude=row['longitude'],
    )

print("✅ Data Loaded")
print("Total:", Property.objects.count())
