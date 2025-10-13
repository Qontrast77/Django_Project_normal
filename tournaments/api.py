from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from .models import Team, Player, Tournament, Match, TournamentCategory
from .serializers import (
    TeamsCRSerializer, TeamsUDSerializer,
    PlayersCRSerializer, PlayersUDSerializer,
    TournamentsCRSerializer, TournamentsUDSerializer,
    MatchesCRSerializer, MatchesUDSerializer,
    TournamentCategoriesCRSerializer, TournamentCategoriesUDSerializer
)

class TeamsViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    queryset = Team.objects.all()
    serializer_class = TeamsCRSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TeamsUDSerializer
        return super().get_serializer_class()

class PlayersViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    queryset = Player.objects.all()
    serializer_class = PlayersCRSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return PlayersUDSerializer
        return super().get_serializer_class()

class TournamentCategoriesViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    queryset = TournamentCategory.objects.all()
    serializer_class = TournamentCategoriesCRSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TournamentCategoriesUDSerializer
        return super().get_serializer_class()

class TournamentsViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    queryset = Tournament.objects.all()
    serializer_class = TournamentsCRSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return TournamentsUDSerializer
        return super().get_serializer_class()

class MatchesViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    queryset = Match.objects.all()
    serializer_class = MatchesCRSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return MatchesUDSerializer
        return super().get_serializer_class()