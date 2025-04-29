from django.shortcuts import render, get_object_or_404, redirect
from .models import GameRoom, Player, GameHistory
from .utils import deal_cards, evaluate_hand
import uuid

def home(request):
    return render(request, "home/index.html")

def lobby(request):
    if request.method == "POST":
        if "create" in request.POST:
            room = GameRoom.objects.create(room_code=str(uuid.uuid4())[:8])
            return redirect("room", room_code=room.room_code)
        elif "join" in request.POST:
            code = request.POST.get("room_code")
            return redirect("room", room_code=code)
    return render(request, "home/lobby.html")

def room(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = list(Player.objects.filter(room=room))

    # Ensure at least 3 players (fill with bots)
    if len(players) < 3:
        for _ in range(3 - len(players)):
            Player.objects.create(room=room, is_bot=True, card=[], has_played=False)
        players = list(Player.objects.filter(room=room))

    if request.method == "POST":
        if "join" in request.POST and not any(not p.is_bot for p in players):
            Player.objects.create(room=room, is_bot=False, card=[], has_played=False)
            players = list(Player.objects.filter(room=room))
        elif "play" in request.POST:
            hands = deal_cards(len(players))
            for p, hand in zip(players, hands):
                p.card = hand
                p.has_played = True
                p.save()
            return redirect("reveal_game", room_code=room_code)

    human_joined = any(not p.is_bot for p in players)
    return render(request, "home/room.html", {
        "room_code":    room.room_code,
        "players":      players,
        "human_joined": human_joined,
    })

def reveal_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = list(Player.objects.filter(room=room))
    evaluated = []

    for p in players:
        rank_info = evaluate_hand(p.card)
        p.score = sum(rank_info[1])
        p.total_score += p.score
        p.save()
        evaluated.append((p, rank_info))

    winner, _ = max(evaluated, key=lambda x: (-x[1][0], x[1][1]))
    GameHistory.objects.create(room=room, winner=winner)

    return render(request, "home/reveal.html", {
        "players": players,
        "winner": winner,
    })

def reset_score(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    for p in Player.objects.filter(room=room):
        p.total_score = 0
        p.score = 0
        p.card = []
        p.has_played = False
        p.save()
    return redirect("room", room_code=room_code)