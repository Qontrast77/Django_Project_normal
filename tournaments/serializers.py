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
        fields = ['id', 'name', 'nickname', 'team']

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
        fields = ['id', 'name', 'nickname', 'team']

class TournamentCategoriesUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentCategory
        fields = "__all__"

class TournamentsUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'category', 'start_date', 'end_date']
        extra_kwargs = {
            'name': {'required': False},
            'category': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
        }

class MatchesUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'tournament', 'team1', 'team2', 'match_date', 'team1_score', 'team2_score', 'winner']
        extra_kwargs = {
            'tournament': {'required': False},
            'team1': {'required': False},
            'team2': {'required': False},
            'match_date': {'required': False},
            'team1_score': {'required': False},
            'team2_score': {'required': False},
            'winner': {'required': False},
        }