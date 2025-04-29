# home/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("lobby/", views.lobby, name="lobby"),
    path("room/<str:room_code>/", views.room, name="room"),
    path("reveal/<str:room_code>/", views.reveal_game, name="reveal_game"),
    path("reset/<str:room_code>/", views.reset_score, name="reset_score"),
]
