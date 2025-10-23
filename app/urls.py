from django.contrib import admin
from django.urls import path, include
from tournaments import views
from rest_framework.routers import DefaultRouter
from tournaments.api import TeamsViewSet, PlayersViewSet, TournamentsViewSet, MatchesViewSet, TournamentCategoriesViewSet
from django.conf.urls.static import static
from django.conf import settings

router = DefaultRouter()
router.register("teams", TeamsViewSet, basename="teams")
router.register("players", PlayersViewSet, basename="players")
router.register("tournament-categories", TournamentCategoriesViewSet, basename="tournament-categories")
router.register("tournaments", TournamentsViewSet, basename="tournaments")
router.register("matches", MatchesViewSet, basename="matches")

urlpatterns = [
    path('', views.ShowTournamentsView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
