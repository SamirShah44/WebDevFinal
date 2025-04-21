from django.contrib import admin
from .models import GameRoom, Player, GameHistory

admin.site.register(GameRoom)
admin.site.register(Player)
admin.site.register(GameHistory)
