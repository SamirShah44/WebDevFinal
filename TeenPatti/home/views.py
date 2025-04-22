from django.shortcuts import render, get_object_or_404 , redirect
from .models import GameRoom, Player, GameHistory
from .utils import deal_cards, evaluate_hand
import uuid
from django.http import HttpResponseRedirect
from django.urls import reverse

# def start_game(request, room_code):
#     room = get_object_or_404(GameRoom, room_code=room_code)
#     players = Player.objects.filter(room=room)

#     if not players.filter(user=request.user).exists():
#         Player.objects.create(user=request.user, room=room, is_bot=False)

#     players = Player.objects.filter(room=room)  # Refresh
#     while players.count() < 3:
#         Player.objects.create(room=room, is_bot=True)
#         players = Player.objects.filter(room=room)

#     hands = deal_cards(len(players))
#     for i, player in enumerate(players):
#         player.card = hands[i]
#         player.has_played = False
#         player.save()

#     return redirect(f"/room/{room.room_code}/")

def start_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)

    players = Player.objects.filter(room=room)

    if not players.filter(is_bot=False).exists():
        Player.objects.create(room=room, is_bot=False, card=[], has_played=False)

    players = Player.objects.filter(room=room) 

    while players.count() < 3:
        Player.objects.create(room=room, is_bot=True, card=[], has_played=False)
        players = Player.objects.filter(room=room)  # refresh count

    hands = deal_cards(len(players))
    for i, player in enumerate(players):
        player.card = hands[i]
        player.has_played = False
        player.save()

    return redirect(f"/room/{room.room_code}/")


def room(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    current_player = players.filter(is_bot=False).first()

    # If no human yet, make one
    if not current_player:
        current_player = Player.objects.create(
            room=room,
            is_bot=False,
            card=[],
            has_played=False
        )
        players = Player.objects.filter(room=room) 

    if all(p.has_played for p in players):
        return redirect(f"/reveal/{room.room_code}/")

    return render(request, "home/room.html", {
        "room_code": room.room_code,
        "players": players,
        "current_player": current_player,
    })



def home(request):
    #add here 
    return render(request, "home/index.html")

def lobby(request):
    if request.method == "POST":
        # If creating a room
        if 'create' in request.POST:
            room = GameRoom.objects.create(room_code=str(uuid.uuid4())[:8])
            return redirect(f"/start/{room.room_code}/")

        # If joining an existing room
        elif 'join' in request.POST:
            code = request.POST.get("room_code")
            return redirect(f"/start/{code}/")

    return render(request, "home/lobby.html")

    

def play_card(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    
    players = Player.objects.filter(room=room)

    # TODO:Uncomment this after creating oauth and login page
    # player = Player.objects.filter(room=room, user=request.user).first()
    player = players.filter(is_bot=False).first()

    if player and not player.has_played:
        player.has_played = True
        player.save()

    # Make all bots auto-play immediately
    for bot in players.filter(is_bot=True):
        bot.has_played = True
        bot.save()

    # If all have played → reveal results
    if all(p.has_played for p in players):
        return redirect(f"/reveal/{room_code}/")

    return redirect(f"/room/{room_code}/")


def reveal_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    evaluated = []
    for p in players:
        hand_rank = evaluate_hand(p.card)        
        score = sum(hand_rank[1])
        p.score = score
        p.total_score += score
        p.save()
        evaluated.append((p, hand_rank))

    # Pick the best hand:
    #  -x[1][0] makes Trail(1) -> -1 highest, HighCard(6)->-6 lowest
    #  x[1][1] is the list of card values, so higher ranks win ties
    winner_player, _ = max(
        evaluated,
        key=lambda x: (-x[1][0], x[1][1])
    )

    GameHistory.objects.create(room=room, winner=winner_player)

    return render(request, "home/reveal.html", {
        "players": players,
        "winner": winner_player,
    })



def reset_score(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    for p in players:
        p.total_score = 0          # 🔁 Reset cumulative score
        p.score = 0                # 🧼 Reset last round score
        p.card = []                # 🃏 Clear old hand
        p.has_played = False       # 🕹️ Ready for new round
        p.save()

    return redirect(f"/start/{room_code}/")  # 🔥 Automatically deal new cards


