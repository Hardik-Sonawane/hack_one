from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('recommend/', views.get_recommendations),
    path('compare/', views.compare_properties),
    path('heatmap/', views.demand_heatmap, name='heatmap'),

    path('ai-agent/', views.ai_agent_page),      
    path('ai-agent/api/', views.ai_chatbot), 

]
