from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
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
    
class UserViewSet(viewsets.GenericViewSet):
    permission_classes = []

    @action(detail=False, url_path="info", methods=["GET"])
    def get_info(self, request, *args, **kwargs):
        user_info = {
            "username": request.user.username,
            "is_authenticated": request.user.is_authenticated,
            "is_staff": request.user.is_staff,
        }
        
        # Добавляем информацию о команде для игроков
        if request.user.is_authenticated and not request.user.is_staff:
            try:
                player = Player.objects.get(user=request.user)
                user_info["team_id"] = player.team.id if player.team else None
                user_info["team_name"] = player.team.name if player.team else None
                user_info["player_id"] = player.id
                user_info["player_nickname"] = player.nickname
            except Player.DoesNotExist:
                user_info["team_id"] = None
                user_info["team_name"] = None
                user_info["player_id"] = None
                user_info["player_nickname"] = None
        
        return Response(user_info)

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request, *args, **kwargs):
        username = self.request.data['username']
        password = self.request.data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return Response({
                'success': True,
            })

        return Response({
            'success': False,
        })
    
    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

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
    
    def get_queryset(self):
        """
        Переопределяем queryset для фильтрации матчей:
        - Администраторы видят все матчи
        - Игроки видят только матчи своей команды
        - Неавторизованные пользователи видят все матчи
        """
        queryset = super().get_queryset()
        
        # Если пользователь администратор или неавторизован - возвращаем все матчи
        if not self.request.user.is_authenticated or self.request.user.is_staff:
            return queryset
        
        # Для авторизованных игроков фильтруем матчи по их команде
        try:
            player = Player.objects.get(user=self.request.user)
            if player.team:
                # Фильтруем матчи, где команда игрока участвует как team1 или team2
                queryset = queryset.filter(
                    Q(team1=player.team) | Q(team2=player.team)
                )
            else:
                # Если у игрока нет команды, возвращаем пустой queryset
                queryset = queryset.none()
        except Player.DoesNotExist:
            # Если пользователь не является игроком, возвращаем пустой queryset
            queryset = queryset.none()
        
        return queryset