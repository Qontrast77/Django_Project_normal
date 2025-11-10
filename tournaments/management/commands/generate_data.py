import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db import transaction

from tournaments.models import Team, Player, Tournament, Match, TournamentCategory

class Command(BaseCommand):
    help = 'Generate test data: 300 teams, 1500 players, and matches'

    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        self.stdout.write('Генерация тестовых данных...')
        
        # Используем транзакцию для ускорения
        with transaction.atomic():
            # 1. Создаем категории
            self.stdout.write('Создаем категории...')
            categories_data = [
                {"name": "Counter-Strike 2", "description": "Турниры по Counter-Strike 2"},
                {"name": "Dota 2", "description": "Турниры по Dota 2"},
                {"name": "Valorant", "description": "Турниры по Valorant"},
                {"name": "League of Legends", "description": "Турниры по League of Legends"},
            ]
            
            categories = []
            for category_data in categories_data:
                category, _ = TournamentCategory.objects.get_or_create(
                    name=category_data["name"],
                    defaults={"description": category_data["description"]}
                )
                categories.append(category)
            
            # 2. Создаем команды
            self.stdout.write('Создаем команды...')
            
            team_names = [
                "Natus Vincere", "Virtus.pro", "Team Spirit", "Gambit", "Fnatic",
                "Team Liquid", "Evil Geniuses", "OG", "Team Secret", "Alliance",
                "Ninjas in Pyjamas", "G2 Esports", "FaZe Clan", "Astralis", "Cloud9",
                "100 Thieves", "T1", "DWG KIA", "Gen.G", "DRX", "NIP", "MOUZ",
                "ENCE", "BIG", "Heroic", "Complexity", "FURIA", "Imperial", "paiN",
                "LOUD", "FUT Esports", "Karmine Corp", "KOI", "GIANTX", "SK Gaming"
            ]
            
            teams = []
            for i in range(300):  # 300 команд
                if i < len(team_names):
                    team_name = team_names[i]
                else:
                    team_name = f"Team {i+1}"
                
                teams.append(Team(name=team_name))
            
            # Массовое создание команд
            Team.objects.bulk_create(teams)
            teams = list(Team.objects.all())
            self.stdout.write(f'Создано {len(teams)} команд')
            
            # 3. Создаем игроков
            self.stdout.write('Создаем игроков...')
            
            popular_nicknames = [
                "s1mple", "ZywOo", "device", "NiKo", "coldzera", "f0rest", "GeT_RiGhT",
                "olofmeister", "kennyS", "GuardiaN", "dupreeh", "Xyp9x", "magisk",
                "EliGE", "Twistzz", "NAF", "ropz", "buster", "electronic", "B1t"
            ]
            
            players = []
            used_nicknames = set()
            
            for team in teams:
                for j in range(5):  # 5 игроков в каждой команде
                    # Простые уникальные никнеймы
                    if popular_nicknames and random.random() < 0.3:
                        nickname = random.choice(popular_nicknames)
                        popular_nicknames.remove(nickname)
                    else:
                        nickname = f"player{len(used_nicknames) + 1}"
                        while nickname in used_nicknames:
                            nickname = f"player{len(used_nicknames) + 1}"
                    
                    used_nicknames.add(nickname)
                    
                    players.append(Player(
                        name=fake.first_name() + " " + fake.last_name(),
                        nickname=nickname,
                        team=team
                    ))
            
            # Массовое создание игроков
            Player.objects.bulk_create(players)
            players = list(Player.objects.all())
            self.stdout.write(f'Создано {len(players)} игроков')
            
            # 4. Создаем турниры
            self.stdout.write('Создаем турниры...')
            
            tournament_names = ["Major", "Championship", "Cup", "League", "Masters"]
            tournament_prefixes = ["PGL", "IEM", "ESL", "BLAST", "DreamHack"]
            
            tournaments = []
            for i in range(60):  # 60 турниров
                start_date = fake.date_between(start_date='-1y', end_date='+3m')
                end_date = start_date + timedelta(days=random.randint(3, 10))
                
                tournament_name = f"{random.choice(tournament_prefixes)} {random.choice(tournament_names)} {2024}"
                
                tournaments.append(Tournament(
                    name=tournament_name,
                    category=random.choice(categories),
                    start_date=start_date,
                    end_date=end_date
                ))
            
            Tournament.objects.bulk_create(tournaments)
            tournaments = list(Tournament.objects.all())
            self.stdout.write(f'Создано {len(tournaments)} турниров')
            
            # 5. Создаем матчи
            self.stdout.write('Создаем матчи...')
            matches = []
            
            # Для каждого турнира создаем матчи
            for tournament in tournaments:
                tournament_teams = random.sample(teams, min(12, len(teams)))
                
                # Создаем по 8-12 матчей на турнир
                num_matches = random.randint(8, 12)
                for _ in range(num_matches):
                    team1, team2 = random.sample(tournament_teams, 2)
                    
                    # Простой счет
                    team1_score = random.randint(0, 16)
                    team2_score = random.randint(0, 16)
                    if team1_score == team2_score:
                        team1_score = 16
                        team2_score = random.randint(0, 14)
                    
                    winner = team1 if team1_score > team2_score else team2
                    
                    matches.append(Match(
                        tournament=tournament,
                        team1=team1,
                        team2=team2,
                        match_date=fake.date_time_between(
                            start_date=tournament.start_date,
                            end_date=tournament.end_date
                        ),
                        team1_score=team1_score,
                        team2_score=team2_score,
                        winner=winner
                    ))
            
            # Также создаем внетурнирные матчи
            for _ in range(300):
                team1, team2 = random.sample(teams, 2)
                team1_score = random.randint(0, 16)
                team2_score = random.randint(0, 16)
                if team1_score == team2_score:
                    team1_score = 16
                    team2_score = random.randint(0, 14)
                
                winner = team1 if team1_score > team2_score else team2
                
                matches.append(Match(
                    team1=team1,
                    team2=team2,
                    match_date=fake.date_time_between(start_date='-1y', end_date='now'),
                    team1_score=team1_score,
                    team2_score=team2_score,
                    winner=winner
                ))
            
            # Массовое создание матчей
            Match.objects.bulk_create(matches)
            self.stdout.write(f'Создано {len(matches)} матчей')
            
            # 6. Создаем пользователей
            self.stdout.write('Создаем пользователей...')
            
            # Администратор
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
            
            # Создаем 10 игроков-пользователей
            user_players = random.sample(players, 10)
            for i, player in enumerate(user_players):
                username = f'user{i+1}'
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': f'{username}@example.com'}
                )
                if created:
                    user.set_password('password123')
                    user.save()
                    player.user = user
                    player.save()
        
        # Статистика
        total_teams = Team.objects.count()
        total_players = Player.objects.count()
        total_tournaments = Tournament.objects.count()
        total_matches = Match.objects.count()
        total_categories = TournamentCategory.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Генерация данных завершена!\n'
                f'📊 Статистика:\n'
                f'   • Команд: {total_teams}\n'
                f'   • Игроков: {total_players}\n'
                f'   • Турниров: {total_tournaments}\n'
                f'   • Матчей: {total_matches}\n'
                f'   • Категорий: {total_categories}\n'
                f'\n👤 Тестовые пользователи:\n'
                f'   Администратор: admin / admin123\n'
                f'   Игроки: user1-user10 / password123'
            )
        )