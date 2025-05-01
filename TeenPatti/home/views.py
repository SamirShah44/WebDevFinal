from django.shortcuts import render, get_object_or_404, redirect
from .models import GameRoom, Player, GameHistory
from .utils import deal_cards, evaluate_hand
import uuid
from django.contrib.auth import logout as django_logout
import urllib.parse
from django.conf import settings
from social_django.utils import psa
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponse

import random
from .utils import evaluate_hand
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "home/index.html")

def dashboard(request):
    return render(request, "home/dashboard.html")

@login_required
def add_coins(request):
    player = Player.objects.filter(user=request.user).order_by('-id').first()
    if player:
        player.balance += 100  # 💰 Add 100 coins (or whatever you want)
        player.save()
    return redirect('lobby')

def lobby(request):
    if request.method == "POST":
        if 'create' in request.POST:
            room = GameRoom.objects.create(room_code=str(uuid.uuid4())[:8], game_started=False)
            return redirect(f"/start/{room.room_code}/")
        elif 'join' in request.POST:
            code = request.POST.get("room_code")
            return redirect(f"/start/{code}/")
    return render(request, "home/lobby.html")

def start_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)

    # ❌ Don't delete everyone
    # Only remove anonymous/unwanted players
    Player.objects.filter(room=room, is_bot=True).delete()
    Player.objects.filter(room=room, user=None).delete()

    room.game_started = False
    room.save()

    if request.user.is_authenticated:
        # Only add player if not already in room
        if not Player.objects.filter(room=room, user=request.user).exists():
            # ✅ Try to reuse old balance
            old_player = Player.objects.filter(user=request.user).exclude(room=room).order_by('-id').first()
            balance = old_player.balance if old_player else 200

            Player.objects.create(
                room=room,
                user=request.user,
                is_bot=False,
                card=[],
                has_played=False,
                balance=balance
            )

    return redirect(f"/room/{room.room_code}/")



def room(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    current_player = None
    if request.user.is_authenticated:
        current_player = players.filter(user=request.user).first()

    if not current_player:
        # 🔍 Check if this user has played before
        existing_player = Player.objects.filter(user=request.user).exclude(room=room).order_by('-id').first()
        balance = existing_player.balance if existing_player else 200

        if players.count() < 3:
            current_player = Player.objects.create(
                room=room,
                user=request.user,
                is_bot=False,
                card=[],
                has_played=False,
                balance=balance
            )
        # Remove bot if exists
        bot = players.filter(is_bot=True).first()
        if bot:
            bot.delete()

    players = Player.objects.filter(room=room)

    waiting_for_more_players = players.count() < 3

    if not room.game_started and not waiting_for_more_players:
        hands = deal_cards(len(players))
        for i, player in enumerate(players):
            player.card = hands[i]
            player.has_played = False
            player.save()
        room.game_started = True
        room.save()

    if all(p.has_played for p in players) and room.game_started:
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
        "waiting_for_more_players": waiting_for_more_players,
        "player_count": players.count(),
    })



def play_card(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    player = players.filter(user=request.user).first()
    if player and not player.has_played:
        player.has_played = True
        player.save()

    # Make bots ready (just mark them as played)
    for bot in players.filter(is_bot=True):
        if not bot.has_played:
            bot.has_played = True
            bot.save()

    if all(p.has_played for p in players) and room.game_started:
        return redirect(f"/reveal/{room_code}/")

    return redirect(f"/room/{room_code}/")


def reveal_game(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)
    current_player = players.filter(user=request.user).first()

    if not current_player:
        return redirect("/lobby/")

    return render(request, "home/reveal.html", {
        "room_code": room.room_code,
        "players": players,
        "current_player": current_player
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

    room.game_started = False
    room.save()

    return redirect(f"/start/{room_code}/")

def add_bot(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)

    if players.count() < 3:
        Player.objects.create(room=room, is_bot=True, card=[], has_played=False)

    return redirect(f"/room/{room_code}/")

def submit_bet(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    player = Player.objects.filter(room=room, user=request.user).first()

    if player and not player.has_bet:
        bet = int(request.POST.get("bet", 20))
        bet = max(1, min(bet, player.balance))  # Clamp within range
        player.balance -= bet
        player.bet_amount = bet
        player.has_bet = True
        player.save()

    return redirect(f"/reveal/{room_code}/")

@csrf_exempt
def bet_phase(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)
    player = players.filter(user=request.user).first()

    MIN_BET = 20

    if request.method == "POST" and player and not player.has_bet:
        try:
            bet = int(request.POST.get("bet", MIN_BET))
            # 🔒 Enforce minimum or all-in
            if player.balance < MIN_BET:
                bet = player.balance  # Go all-in
            else:
                bet = max(MIN_BET, min(bet, player.balance))
            player.balance -= bet
            player.bet_amount = bet
            player.has_bet = True
            player.save()
        except ValueError:
            return HttpResponse("Invalid bet", status=400)

    for bot in players.filter(is_bot=True, has_bet=False):
        rank_num, _ = evaluate_hand(bot.card)

        # Map rank to betting logic
        if rank_num == 1:  # Trio
            bot_bet = min(bot.balance, 100)
        elif rank_num == 2:  # Pure Sequence
            bot_bet = min(bot.balance, 90)
        elif rank_num == 3:  # Sequence
            bot_bet = min(bot.balance, 70)
        elif rank_num == 4:  # Flush
            bot_bet = min(bot.balance, 50)
        elif rank_num == 5:  # Pair
            bot_bet = min(bot.balance, 30)
        else:  # High Card
            bot_bet = 20 if bot.balance >= 20 else bot.balance  # always bet something

        bot.balance -= bot_bet
        bot.bet_amount = bot_bet
        bot.has_bet = True
        bot.save()

    if all(p.has_bet for p in players):
        return redirect("final_reveal", room_code=room_code)

    return render(request, "home/reveal.html", {
        "players": players,
        "room_code": room_code,
        "current_player": player,
    })



def final_reveal(request, room_code):
    room = get_object_or_404(GameRoom, room_code=room_code)
    players = Player.objects.filter(room=room)
    evaluated = []

    for p in players:
        if len(p.card) == 3:
            hand_rank = evaluate_hand(p.card)
            rank_num, card_vals = hand_rank
            score = sum(card_vals)
            p.score = score
            p.total_score += score
            evaluated.append((p, rank_num, card_vals))

    if not evaluated:
        return redirect("/lobby/")

    winner_player, *_ = max(evaluated, key=lambda x: (-x[1], x[2]))
    pot = sum(p.bet_amount for p in players)
    winner_player.balance += pot
    winner_player.save()

    response = render(request, "home/final_reveal.html", {
        "players": players,
        "winner": winner_player,
        "room_code": room.room_code,
        "evaluated": evaluated,
        "current_player": players.filter(user=request.user).first(),
    })

    # ❌ Don't reset bet before rendering
    for p in players:
        p.bet_amount = 0
        p.has_played = False
        p.has_bet = False
        p.save()

    return response


# Auth
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
