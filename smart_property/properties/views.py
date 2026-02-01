from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
import numpy as np

from .models import Property
from .recommender import recommend, cold_start
from .clustering import cluster_properties
from .ai_agent import ask_ai_agent


def index(request):
    return render(request, "index.html")


def get_recommendations(request):
    props = Property.objects.all()

    if not props.exists():
        return render(request, "recommend.html", {
            "error": "Database empty"
        })

    # Cold start
    if request.method != "POST" or not request.POST.get("price"):
        results = cold_start(props)
        return render(request, "recommend.html", {"results": results})

    # User input
    user_input = {
        "price": float(request.POST["price"]),
        "area": float(request.POST["area"]),
        "bedroom_num": int(request.POST["bedroom_num"]),
        "bathroom_num": int(request.POST["bathroom_num"]),
        "persona": request.POST.get("persona", "student")
    }

    ranked = recommend(user_input, list(props))

    # -------- FILTERS --------
    min_price = request.POST.get("min_price")
    max_price = request.POST.get("max_price")
    furnished = request.POST.get("furnished")
    property_type = request.POST.get("property_type")
    min_bedrooms = request.POST.get("min_bedrooms")

    filtered = []
    for p, score in ranked:
        if min_price and p.price < float(min_price):
            continue
        if max_price and p.price > float(max_price):
            continue
        if furnished and furnished != "any" and p.furnished != furnished:
            continue
        if property_type and property_type != "any" and p.property_type != property_type:
            continue
        if min_bedrooms and p.bedroom_num < int(min_bedrooms):
            continue
        filtered.append((p, score))

    if not filtered:
        return render(request, "recommend.html", {
            "error": "No properties matched your criteria."
        })

    # -------- SORTING --------
    sort_by = request.POST.get("sort_by")
    if sort_by == "price_low":
        filtered.sort(key=lambda x: x[0].price)
    elif sort_by == "area_high":
        filtered.sort(key=lambda x: x[0].area, reverse=True)
    elif sort_by == "bedrooms":
        filtered.sort(key=lambda x: x[0].bedroom_num, reverse=True)

    # -------- BEST CHOICE --------
    cheapest = min(filtered, key=lambda x: x[0].price)[0]
    largest = max(filtered, key=lambda x: x[0].area)[0]
    best_match = max(filtered, key=lambda x: x[1])[0]

    # -------- XAI EXPLANATION --------
    explanations = {}

    locality_prices = {}
    for p in props:
        locality_prices.setdefault(p.locality, []).append(p.price)

    locality_avg = {loc: np.mean(prices) for loc, prices in locality_prices.items()}

    for p, score in filtered:
        reasons = []

        if abs(p.price - user_input["price"]) < 0.2 * user_input["price"]:
            reasons.append("matches your budget")

        if p.bedroom_num == user_input["bedroom_num"]:
            reasons.append("has the same number of bedrooms")

        avg_price = locality_avg.get(p.locality, p.price)
        if p.price < avg_price:
            diff = int(((avg_price - p.price) / avg_price) * 100)
            reasons.append(f"is {diff}% cheaper than average in {p.locality}")

        if not reasons:
            reasons.append("is similar to your preferences")

        explanations[p.id] = "Recommended because it " + " and ".join(reasons) + "."

    # -------- CLUSTERING --------
    cluster_map = cluster_properties([p for p, _ in filtered])

    cluster_names = {
        0: "Budget Home",
        1: "Premium Home",
        2: "Luxury Home"
    }

    cluster_labels = {
        p.id: cluster_names.get(cluster_map.get(p.id, 0), "Property")
        for p, _ in filtered
    }

    return render(request, "recommend.html", {
        "ranked": filtered,
        "cheapest_id": cheapest.id,
        "largest_id": largest.id,
        "best_match_id": best_match.id,
        "explanations": explanations,
        "clusters": cluster_labels
    })


def compare_properties(request):
    ids = request.POST.getlist("compare_ids")

    if len(ids) < 2:
        return render(request, "compare.html", {
            "error": "Please select at least 2 properties."
        })

    props = Property.objects.filter(id__in=ids[:3])
    return render(request, "compare.html", {"properties": props})


def demand_heatmap(request):
    data = (
        Property.objects
        .values("locality")
        .annotate(count=Count("id"))
        .order_by("-count")[:20]
    )

    max_count = max([d["count"] for d in data]) if data else 1

    heatmap = [
        {
            "locality": d["locality"],
            "count": d["count"],
            "intensity": int((d["count"] / max_count) * 100),
        }
        for d in data
    ]

    return render(request, "heatmap.html", {"heatmap": heatmap})


def ai_agent_page(request):
    return render(request, "ai_agent.html")


def ai_chatbot(request):
    if request.method == "POST":
        msg = request.POST.get("message", "")
        reply = ask_ai_agent(msg)
        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"}, status=400)
