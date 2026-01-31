import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def recommend(user_input, properties):
    persona = user_input.get("persona", "student")

    X = []
    for p in properties:
        X.append([
            p.price,
            p.area,
            p.bedroom_num,
            p.bathroom_num
        ])
    X = np.array(X)

    user_vector = np.array([[
        user_input["price"],
        user_input["area"],
        user_input["bedroom_num"],
        user_input["bathroom_num"]
    ]])

    # -------- PERSONA WEIGHTS --------
    if persona == "student":
        weights = np.array([3, 1, 1, 1])      # price most important
    elif persona == "family":
        weights = np.array([1, 1, 3, 2])      # bedrooms important
    elif persona == "investor":
        weights = np.array([1, 3, 1, 1])      # area important
    else:  # professional
        weights = np.array([2, 2, 2, 1])      # balanced

    X_weighted = X * weights
    user_weighted = user_vector * weights

    similarities = cosine_similarity(user_weighted, X_weighted)[0]

    ranked = list(zip(properties, similarities))
    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked

def cold_start(properties):
    # fallback: show cheapest / most common
    return properties.order_by('price')[:10]