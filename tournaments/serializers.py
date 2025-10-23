# serializers.py
from rest_framework import serializers
from .models import Team, Player, Tournament, Match, TournamentCategory

# Для чтения
class TeamsCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"

class PlayersCRSerializer(serializers.ModelSerializer):
    team = TeamsCRSerializer(read_only=True)
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'nickname', 'team', 'photo']

class TournamentCategoriesCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentCategory
        fields = "__all__"

class TournamentsCRSerializer(serializers.ModelSerializer):
    category = TournamentCategoriesCRSerializer(read_only=True)
    
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'category', 'start_date', 'end_date']

class MatchesCRSerializer(serializers.ModelSerializer):
    tournament = TournamentsCRSerializer(read_only=True)
    team1 = TeamsCRSerializer(read_only=True)
    team2 = TeamsCRSerializer(read_only=True)
    winner = TeamsCRSerializer(read_only=True)
    
    class Meta:
        model = Match
        fields = ['id', 'tournament', 'team1', 'team2', 'match_date', 'team1_score', 'team2_score', 'winner']

# Для создания/обновления
class TeamsUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"

class PlayersUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'nickname', 'team', 'photo']

class TournamentCategoriesUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentCategory
        fields = "__all__"

class TournamentsUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'category', 'start_date', 'end_date']

class MatchesUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'tournament', 'team1', 'team2', 'match_date', 'team1_score', 'team2_score', 'winner']