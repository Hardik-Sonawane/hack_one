import os
import requests
from .models import Property
from django.db.models import Avg

# -----------------------------------------
# OPENROUTER CONFIG (Railway-safe)
# -----------------------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.5-pro"
URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_ai_agent(query):
    if not API_KEY:
        return "AI service is not configured. API key missing."

    query_lower = query.lower()
    context = ""

    # -----------------------------------------
    # DATABASE-AWARE CONTEXT
    # -----------------------------------------
    if "cheapest" in query_lower:
        prop = Property.objects.order_by("price").first()
        if prop:
            context = f"""
Cheapest property:
Title: {prop.title}
Price: {prop.price}
Locality: {prop.locality}
Area: {prop.area} sqft
Bedrooms: {prop.bedroom_num}
"""
        else:
            context = "No properties available in the database."

    elif "average price" in query_lower:
        avg_price = Property.objects.aggregate(avg=Avg("price"))["avg"]
        if avg_price:
            context = f"Average price of all properties is ₹{int(avg_price)}"
        else:
            context = "No price data available."

    else:
        total = Property.objects.count()
        context = f"There are {total} properties in the database."

    # -----------------------------------------
    # OPENROUTER PAYLOAD
    # -----------------------------------------
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI property assistant. Answer using the provided database information only."
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

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        return "AI could not generate a response."

    except requests.exceptions.RequestException as e:
        return f"AI request failed: {str(e)}"
