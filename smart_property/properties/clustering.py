# properties/clustering.py

import numpy as np
from sklearn.cluster import KMeans

def cluster_properties(properties):
    n = len(properties)

    # Edge case: 0 or 1 property
    if n <= 1:
        return {p.id: 0 for p in properties}

    # Adaptive cluster count
    k = min(3, n)

    X = np.array([
        [p.price, p.area, p.bedroom_num]
        for p in properties
    ])

    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(X)

    return {
        properties[i].id: int(labels[i])
        for i in range(n)
    }
