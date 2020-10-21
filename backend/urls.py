from rest_framework import routers
from django.urls import path, include
from backend import views

router = routers.DefaultRouter()


urlpatterns = [
    path("query_data/", views.QueryView.as_view()),
    path("most_outdated_page/", views.MostOutdatedPage.as_view()),
]
