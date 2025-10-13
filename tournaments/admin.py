from django.contrib import admin
from .models import Team, Player, Tournament, Match, TournamentCategory

@admin.register(Team)
class TeamsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']

@admin.register(Player)
class PlayersAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'nickname', 'team']

@admin.register(TournamentCategory)
class TournamentCategoriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Tournament)
class TournamentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'start_date', 'end_date']

@admin.register(Match)
class MatchesAdmin(admin.ModelAdmin):
    list_display = ['id', 'tournament', 'team1', 'team2', 'match_date', 'team1_score', 'team2_score', 'winner']