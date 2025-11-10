from django.core.management.base import BaseCommand
from tournaments.models import Team, Player, Tournament, Match, TournamentCategory
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Clear all tournament data'

    def handle(self, *args, **options):
        self.stdout.write('Очищаем базу данных...')
        
        # Удаляем в правильном порядке (сначала зависимые объекты)
        Match.objects.all().delete()
        self.stdout.write('Удалены все матчи')
        
        Tournament.objects.all().delete()
        self.stdout.write('Удалены все турниры')
        
        Player.objects.all().delete()
        self.stdout.write('Удалены все игроки')
        
        Team.objects.all().delete()
        self.stdout.write('Удалены все команды')
        
        TournamentCategory.objects.all().delete()
        self.stdout.write('Удалены все категории')
        
        # Удаляем тестовых пользователей (кроме суперпользователей)
        test_users = User.objects.filter(
            username__in=['admin', 'player1', 'player2', 'player3', 'player4', 'player5', 
                         'player6', 'player7', 'player8', 'player9', 'player10']
        )
        test_users.delete()
        self.stdout.write('Удалены тестовые пользователи')
        
        self.stdout.write(
            self.style.SUCCESS('✅ База данных полностью очищена!')
        )