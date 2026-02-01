from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("recommend/", views.get_recommendations, name="recommend"),
    path("compare/", views.compare_properties, name="compare"),
    path("heatmap/", views.demand_heatmap, name="heatmap"),

    path("ai-agent/", views.ai_agent_page, name="ai_agent"),
    path("ai-chatbot/", views.ai_chatbot, name="ai_chatbot"),
]
