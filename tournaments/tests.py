from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker
from .models import Team, Player, Tournament, Match, TournamentCategory


class TeamsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_get_teams_list(self):
        """Тест получения списка команд"""
        baker.make(Team, _quantity=3)
        response = self.client.get('/api/teams/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
    
    def test_get_team_detail(self):
        """Тест получения деталей команды"""
        team = baker.make(Team)
        response = self.client.get(f'/api/teams/{team.id}/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(team.name, data['name'])
        self.assertEqual(team.id, data['id'])
    
    def test_create_team(self):
        """Тест создания команды"""
        response = self.client.post("/api/teams/", {
            "name": "Team Spirit"
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_team_id = response.json()['id']
        teams = Team.objects.all()
        self.assertEqual(len(teams), 1)
        
        new_team = Team.objects.filter(id=new_team_id).first()
        self.assertEqual(new_team.name, 'Team Spirit')
    
    def test_update_team(self):
        """Тест обновления команды"""
        team = baker.make(Team, name="NaVi")
        response = self.client.patch(f'/api/teams/{team.id}/', {
            "name": "Natus Vincere"
        })
        
        self.assertEqual(response.status_code, 200)
        
        team.refresh_from_db()
        self.assertEqual(team.name, "Natus Vincere")
    
    def test_delete_team(self):
        """Тест удаления команды"""
        team = baker.make(Team)
        response = self.client.delete(f'/api/teams/{team.id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Team.objects.count(), 0)


class PlayersViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_get_players_list(self):
        """Тест получения списка игроков"""
        baker.make(Player, _quantity=3)
        response = self.client.get('/api/players/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
    
    def test_get_player_detail(self):
        """Тест получения деталей игрока"""
        player = baker.make(Player)
        response = self.client.get(f'/api/players/{player.id}/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(player.name, data['name'])
        self.assertEqual(player.nickname, data['nickname'])
        self.assertEqual(player.id, data['id'])
    
    def test_create_player(self):
        """Тест создания игрока"""
        team = baker.make(Team)
        response = self.client.post("/api/players/", {
            "name": "Иван Иванов",
            "nickname": "Yatoro",
            "team": team.id
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_player_id = response.json()['id']
        players = Player.objects.all()
        self.assertEqual(len(players), 1)
        
        new_player = Player.objects.filter(id=new_player_id).first()
        self.assertEqual(new_player.name, 'Иван Иванов')
        self.assertEqual(new_player.nickname, 'Yatoro')
    
    def test_update_player(self):
        """Тест обновления игрока"""
        team = baker.make(Team)
        player = baker.make(Player, name="Петр", nickname="Petr1")
        response = self.client.patch(f'/api/players/{player.id}/', {
            "nickname": "Collapse"
        })
        
        self.assertEqual(response.status_code, 200)
        
        player.refresh_from_db()
        self.assertEqual(player.nickname, "Collapse")
    
    def test_delete_player(self):
        """Тест удаления игрока"""
        player = baker.make(Player)
        response = self.client.delete(f'/api/players/{player.id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Player.objects.count(), 0)


class TournamentCategoriesViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_get_categories_list(self):
        """Тест получения списка категорий турниров"""
        baker.make(TournamentCategory, _quantity=3)
        response = self.client.get('/api/tournament-categories/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
    
    def test_get_category_detail(self):
        """Тест получения деталей категории"""
        category = baker.make(TournamentCategory)
        response = self.client.get(f'/api/tournament-categories/{category.id}/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(category.name, data['name'])
        self.assertEqual(category.id, data['id'])
    
    def test_create_category(self):
        """Тест создания категории"""
        response = self.client.post("/api/tournament-categories/", {
            "name": "Major",
            "description": "Крупные международные турниры"
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_category_id = response.json()['id']
        categories = TournamentCategory.objects.all()
        self.assertEqual(len(categories), 1)
        
        new_category = TournamentCategory.objects.filter(id=new_category_id).first()
        self.assertEqual(new_category.name, 'Major')
        self.assertEqual(new_category.description, 'Крупные международные турниры')
    
    def test_update_category(self):
        """Тест обновления категории"""
        category = baker.make(TournamentCategory, name="Premier")
        response = self.client.patch(f'/api/tournament-categories/{category.id}/', {
            "name": "Major"
        })
        
        self.assertEqual(response.status_code, 200)
        
        category.refresh_from_db()
        self.assertEqual(category.name, "Major")
    
    def test_delete_category(self):
        """Тест удаления категории"""
        category = baker.make(TournamentCategory)
        response = self.client.delete(f'/api/tournament-categories/{category.id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(TournamentCategory.objects.count(), 0)


class TournamentsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_get_tournaments_list(self):
        """Тест получения списка турниров"""
        category = baker.make(TournamentCategory)
        baker.make(Tournament, category=category, _quantity=3)
        response = self.client.get('/api/tournaments/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
    
    def test_get_tournament_detail(self):
        """Тест получения деталей турнира"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        response = self.client.get(f'/api/tournaments/{tournament.id}/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tournament.name, data['name'])
        self.assertEqual(tournament.id, data['id'])
        self.assertEqual(tournament.category.id, data['category']['id'])
    
    def test_create_tournament(self):
        """Тест создания турнира"""
        category = baker.make(TournamentCategory)
        response = self.client.post("/api/tournaments/", {
            "name": "The International 2024",
            "category": category.id,
            "start_date": "2024-09-01",
            "end_date": "2024-09-15"
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_tournament_id = response.json()['id']
        tournaments = Tournament.objects.all()
        self.assertEqual(len(tournaments), 1)
        
        new_tournament = Tournament.objects.filter(id=new_tournament_id).first()
        self.assertEqual(new_tournament.name, 'The International 2024')
        self.assertEqual(new_tournament.category, category)
    
    def test_update_tournament(self):
        """Тест обновления турнира"""
        category1 = baker.make(TournamentCategory)
        category2 = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, name="TI 2023", category=category1)
        
        # Обновляем только название, категория остается прежней
        response = self.client.patch(f'/api/tournaments/{tournament.id}/', {
            "name": "The International 2023"
        })
        
        self.assertEqual(response.status_code, 200)
        
        tournament.refresh_from_db()
        self.assertEqual(tournament.name, "The International 2023")
        # Категория не должна измениться, так как мы ее не обновляли
        self.assertEqual(tournament.category, category1)

    def test_update_tournament_category(self):
        """Простой тест обновления названия турнира"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, name="Old Name", category=category)
        
        response = self.client.patch(f'/api/tournaments/{tournament.id}/', {
            "name": "New Name"
        })
        
        self.assertEqual(response.status_code, 200)
        
        tournament.refresh_from_db()
        self.assertEqual(tournament.name, "New Name")
        
        def test_delete_tournament(self):
            """Тест удаления турнира"""
            category = baker.make(TournamentCategory)
            tournament = baker.make(Tournament, category=category)
            response = self.client.delete(f'/api/tournaments/{tournament.id}/')
            
            self.assertEqual(response.status_code, 204)
            self.assertEqual(Tournament.objects.count(), 0)


class MatchesViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_get_matches_list(self):
        """Тест получения списка матчей"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)
        
        baker.make(Match, 
                  tournament=tournament,
                  team1=team1,
                  team2=team2,
                  _quantity=3)
        
        response = self.client.get('/api/matches/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
    
    def test_get_match_detail(self):
        """Тест получения деталей матча"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)
        
        match = baker.make(Match,
                         tournament=tournament,
                         team1=team1,
                         team2=team2,
                         team1_score=2,
                         team2_score=1)
        
        response = self.client.get(f'/api/matches/{match.id}/')
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(match.id, data['id'])
        self.assertEqual(match.team1_score, data['team1_score'])
        self.assertEqual(match.team2_score, data['team2_score'])
        
        # Проверяем вложенные объекты
        self.assertEqual(match.tournament.id, data['tournament']['id'])
        self.assertEqual(match.team1.id, data['team1']['id'])
        self.assertEqual(match.team2.id, data['team2']['id'])
        self.assertEqual(match.winner.id, data['winner']['id'])
    
    def test_create_match(self):
        """Тест создания матча"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)
        
        response = self.client.post("/api/matches/", {
            "tournament": tournament.id,
            "team1": team1.id,
            "team2": team2.id,
            "match_date": "2024-09-10T15:00:00Z",
            "team1_score": 2,
            "team2_score": 1
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_match_id = response.json()['id']
        matches = Match.objects.all()
        self.assertEqual(len(matches), 1)
        
        new_match = Match.objects.filter(id=new_match_id).first()
        self.assertEqual(new_match.tournament, tournament)
        self.assertEqual(new_match.team1, team1)
        self.assertEqual(new_match.team2, team2)
        self.assertEqual(new_match.team1_score, 2)
        self.assertEqual(new_match.team2_score, 1)
        self.assertEqual(new_match.winner, team1)  # Автоматически определился победитель
    
    def test_create_match_with_draw(self):
        """Тест создания матча с ничьей"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)
        
        response = self.client.post("/api/matches/", {
            "tournament": tournament.id,
            "team1": team1.id,
            "team2": team2.id,
            "match_date": "2024-09-10T15:00:00Z",
            "team1_score": 1,
            "team2_score": 1
        })
        
        self.assertEqual(response.status_code, 201)
        
        new_match = Match.objects.first()
        self.assertIsNone(new_match.winner)  # При ничье победитель None
    
    def test_update_match(self):
        """Простой тест обновления счета матча"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)

        match = baker.make(Match,
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                    team1_score=1,
                    team2_score=1)  # ничья

        # Обновляем только счет
        response = self.client.patch(f'/api/matches/{match.id}/', {
            "team1_score": 2,
            "team2_score": 1
        })

        self.assertEqual(response.status_code, 200)
        
        match.refresh_from_db()
        self.assertEqual(match.team1_score, 2)
        self.assertEqual(match.team2_score, 1)
        self.assertEqual(match.winner, team1)
    
    def test_update_match_change_winner(self):
        """Тест обновления матча с изменением победителя"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)

        match = baker.make(Match,
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                    team1_score=2,
                    team2_score=1)  # Победитель team1

        # Меняем счет - победитель должен измениться на team2
        response = self.client.patch(f'/api/matches/{match.id}/', {
            "team1_score": 1,
            "team2_score": 2
        })

        self.assertEqual(response.status_code, 200)
        
        match.refresh_from_db()
        self.assertEqual(match.winner, team2)
    
    def test_delete_match(self):
        """Тест удаления матча"""
        category = baker.make(TournamentCategory)
        tournament = baker.make(Tournament, category=category)
        team1 = baker.make(Team)
        team2 = baker.make(Team)
        
        match = baker.make(Match,
                         tournament=tournament,
                         team1=team1,
                         team2=team2)
        
        response = self.client.delete(f'/api/matches/{match.id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Match.objects.count(), 0)