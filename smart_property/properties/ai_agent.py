import requests
import json
from .models import Property
from django.db.models import Avg

API_KEY = "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"
MODEL = "google/gemini-2.5-pro"
URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_ai_agent(query):
    query_lower = query.lower()

    context = ""

    # REAL DATABASE LOGIC
    if "cheapest" in query_lower:
        prop = Property.objects.order_by("price").first()
        context = f"""
Cheapest property:
Title: {prop.title}
Price: {prop.price}
Locality: {prop.locality}
Area: {prop.area} sqft
Bedrooms: {prop.bedroom_num}
"""

    elif "average price" in query_lower:
        avg_price = Property.objects.aggregate(avg=Avg("price"))["avg"]
        context = f"Average price of all properties is ₹{int(avg_price)}"

    else:
        total = Property.objects.count()
        context = f"There are {total} properties in the database."

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI property assistant. Use the given database info to answer."
            },
            {
                "role": "user",
                "content": f"User question: {query}\n\nDatabase info:\n{context}"
            }
        ],
        "temperature": 0.2,
        "max_tokens": 400
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return str(data)
