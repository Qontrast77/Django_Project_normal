import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from tournaments.models import Team, Player, TournamentCategory, Tournament, Match

# Очищаем старые данные
Team.objects.all().delete()
TournamentCategory.objects.all().delete()
Tournament.objects.all().delete()
Match.objects.all().delete()

# Создаем команды
teams_data = [
    "Team Spirit", "Natus Vincere", "G2 Esports", "Team Liquid", "Fnatic"
]
teams = []
for team_name in teams_data:
    team = Team.objects.create(name=team_name)
    teams.append(team)
    print(f"Создана команда: {team_name}")

# Создаем игроков
players_data = [
    {"name": "Илья Мулярчук", "nickname": "Yatoro", "team": teams[0]},
    {"name": "Александр Костилев", "nickname": "s1mple", "team": teams[1]},
    {"name": "Риккардо Ромитти", "nickname": "Ricky", "team": teams[2]},
    {"name": "Михаил Агатов", "nickname": "Misha", "team": teams[3]},
    {"name": "Джаба Квицилашвили", "nickname": "Davai Lama", "team": teams[4]},
]

for player_data in players_data:
    Player.objects.create(**player_data)
    print(f"Создан игрок: {player_data['name']} ({player_data['nickname']})")

# Создаем категории турниров
categories_data = [
    "Major", "Premier", "Qualifier", "Regional", "Showmatch"
]
categories = []
for category_name in categories_data:
    category = TournamentCategory.objects.create(name=category_name)
    categories.append(category)
    print(f"Создана категория: {category_name}")

# Создаем турниры
tournaments_data = [
    {"name": "The International 2023", "category": categories[0], "start_date": "2023-10-15", "end_date": "2023-10-30"},
    {"name": "Riyadh Masters 2024", "category": categories[1], "start_date": "2024-07-01", "end_date": "2024-07-21"},
    {"name": "ESL One Birmingham 2024", "category": categories[1], "start_date": "2024-04-22", "end_date": "2024-04-28"},
    {"name": "DreamLeague Season 22", "category": categories[2], "start_date": "2024-02-10", "end_date": "2024-02-20"},
    {"name": "BetBoom Dacha 2024", "category": categories[3], "start_date": "2024-01-05", "end_date": "2024-01-15"},
]

tournaments = []
for tournament_data in tournaments_data:
    tournament = Tournament.objects.create(**tournament_data)
    tournaments.append(tournament)
    print(f"Создан турнир: {tournament_data['name']}")

# Создаем матчи
matches_data = [
    {"tournament": tournaments[0], "team1": teams[0], "team2": teams[1], "match_date": "2023-10-20 15:00:00", "team1_score": 2, "team2_score": 1},
    {"tournament": tournaments[1], "team1": teams[2], "team2": teams[3], "match_date": "2024-07-10 18:00:00", "team1_score": 2, "team2_score": 0},
    {"tournament": tournaments[2], "team1": teams[4], "team2": teams[0], "match_date": "2024-04-25 14:00:00", "team1_score": 1, "team2_score": 2},
    {"tournament": tournaments[3], "team1": teams[3], "team2": teams[1], "match_date": "2024-02-15 16:00:00", "team1_score": 2, "team2_score": 1},
    {"tournament": tournaments[4], "team1": teams[2], "team2": teams[4], "match_date": "2024-01-10 12:00:00", "team1_score": 2, "team2_score": 1},
]

for match_data in matches_data:
    Match.objects.create(**match_data)
    print(f"Создан матч: {match_data['team1'].name} vs {match_data['team2'].name}")

print("База данных успешно заполнена!")