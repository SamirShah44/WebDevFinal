from django.db import models
from django.contrib.auth.models import User
import uuid

class GameRoom(models.Model):
    room_code = models.CharField(max_length=8, unique=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    game_started = models.BooleanField(default=False)

    def __str__(self):
        return self.room_code

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    card = models.JSONField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    has_played = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

class GameHistory(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    played_at = models.DateTimeField(auto_now_add=True)
