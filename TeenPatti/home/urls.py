from django.urls import path
from . import views

urlpatterns = [
    path('start/<str:room_code>/', views.start_game, name='start_game'),
    path('', views.home, name='home'),
    path("lobby/", views.lobby, name="lobby"),
    path("room/<str:room_code>/", views.room, name="room"),
    path("play/<str:room_code>/", views.play_card, name="play_card"),
    path("reveal/<str:room_code>/", views.reveal_game, name="reveal_game"),
    path("reset/<str:room_code>/", views.reset_score, name="reset_score"),
]
