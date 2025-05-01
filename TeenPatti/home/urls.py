from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lobby/', views.lobby, name='lobby'),
    path('start/<str:room_code>/', views.start_game, name='start_game'),
    path('room/<str:room_code>/', views.room, name='room'),
    path('play/<str:room_code>/', views.play_card, name='play_card'),
    path('reveal/<str:room_code>/', views.reveal_game, name='reveal_game'),
    path('reset/<str:room_code>/', views.reset_score, name='reset_score'),
    path('login/', views.auth_login, name='login'),
    path('callback/', views.auth_callback, name='callback'),
    path('logout/', views.auth_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-bot/<str:room_code>/', views.add_bot, name='add_bot'),
    path('bet/<str:room_code>/', views.bet_phase, name='bet_phase'),
    path('final_reveal/<str:room_code>/', views.final_reveal, name='final_reveal'),
    path('add-coins/', views.add_coins, name='add_coins'),

]
