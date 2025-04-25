from django.shortcuts import render, get_object_or_404, redirect
from .models import GameRoom, Player, GameHistory
from .utils import deal_cards, evaluate_hand
import uuid
from django.contrib.auth import logout as django_logout
import urllib.parse
from django.conf import settings
from social_django.utils import psa


def start_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)

    if not Player.objects.filter(room=room, is_bot=False).exists():
        Player.objects.create(room=room, user=request.user, is_bot=False, card=[], has_played=False)

    players = Player.objects.filter(room=room)

    while players.count() < 3:
        Player.objects.create(room=room, is_bot=True, card=[], has_played=False)
        players = Player.objects.filter(room=room)

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

    evaluated = []
    for p in players:
        if len(p.card) == 3:
            hand_rank = evaluate_hand(p.card)
            evaluated.append((p, hand_rank))

    winner_player = None
    if evaluated:
        winner_player, _ = max(
            evaluated,
            key=lambda x: (-x[1][0], x[1][1])
        )

    return render(request, "home/room.html", {
        "room_code": room.room_code,
        "players": players,
        "current_player": current_player,
        "evaluated": evaluated,
        "winner": winner_player,
    })


def home(request):
    return render(request, "home/index.html")


def lobby(request):
    if request.method == "POST":
        if 'create' in request.POST:
            room = GameRoom.objects.create(room_code=str(uuid.uuid4())[:8])
            return redirect(f"/start/{room.room_code}/")

        elif 'join' in request.POST:
            code = request.POST.get("room_code")
            return redirect(f"/start/{code}/")

    return render(request, "home/lobby.html")


def play_card(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)
    player = players.filter(is_bot=False).first()

    if player and not player.has_played:
        player.has_played = True
        player.save()

    for bot in players.filter(is_bot=True):
        bot.has_played = True
        bot.save()

    if all(p.has_played for p in players):
        return redirect(f"/reveal/{room_code}/")

    return redirect(f"/room/{room_code}/")


def reveal_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    evaluated = []
    for p in players:
        if len(p.card) == 3: 
            hand_rank = evaluate_hand(p.card)  # (rank_num, card_vals)
            rank_num, card_vals = hand_rank
            rank_name = [
                "Trail", "Pure Sequence", "Sequence", "Flush", "Pair", "High Card"
            ][rank_num - 1]
            score = sum(card_vals)
            p.score = score
            p.total_score += score
            p.save()
            evaluated.append((p, rank_num, card_vals, rank_name))  # 4 values

    winner_player, *_ = max(
        evaluated,
        key=lambda x: (-x[1], x[2])  # rank_num and card_vals
    )

    GameHistory.objects.create(room=room, winner=winner_player)

    return render(request, "home/reveal.html", {
        "players": players,
        "winner": winner_player,
        "room_code": room.room_code,
        "current_player": players.filter(is_bot=False).first(),
        "evaluated": evaluated,
    })



def reset_score(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    for p in players:
        p.total_score = 0
        p.score = 0
        p.card = []
        p.has_played = False
        p.save()

    return redirect(f"/start/{room_code}/")


def dashboard(request):
    return render(request, "home/dashboard.html")


def auth_login(request):
    return redirect('social:begin', backend='auth0')


@psa('social:complete')
def auth_callback(request, backend):
    return redirect('lobby')


def auth_logout(request):
    django_logout(request)
    return_to = request.build_absolute_uri('/')
    logout_url = f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/v2/logout?" + urllib.parse.urlencode({
        'returnTo': return_to,
        'client_id': settings.SOCIAL_AUTH_AUTH0_KEY,
    })
    return redirect(logout_url)
