from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Team(models.Model):
    name = models.TextField("Название команды")
    logo = models.ImageField("Логотип команды", null=True, blank=True, upload_to="tournaments_img")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"
    
    def __str__(self) -> str:
        return self.name

class Player(models.Model):
    name = models.TextField("Имя игрока")
    nickname = models.TextField("Никнейм")
    photo = models.ImageField("Фото игрока", null=True, blank=True, upload_to="tournaments_img")
    team = models.ForeignKey("Team", verbose_name="Команда", on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.nickname})"

class TournamentCategory(models.Model):
    name = models.TextField("Категория турнира")
    description = models.TextField("Описание категории", blank=True)
    
    class Meta:
        verbose_name = "Категория турнира"
        verbose_name_plural = "Категории турниров"
    
    def __str__(self) -> str:
        return self.name

class Tournament(models.Model):
    name = models.TextField("Название турнира")
    category = models.ForeignKey("TournamentCategory", verbose_name="Категория", on_delete=models.CASCADE, null=True)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    
    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"
    
    def __str__(self) -> str:
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey("Tournament", verbose_name="Турнир", on_delete=models.CASCADE, null=True)
    team1 = models.ForeignKey("Team", verbose_name="Команда 1", on_delete=models.CASCADE, related_name="team1_matches", null=True)
    team2 = models.ForeignKey("Team", verbose_name="Команда 2", on_delete=models.CASCADE, related_name="team2_matches", null=True)
    match_date = models.DateTimeField("Дата матча")
    team1_score = models.IntegerField("Счёт команды 1", default=0)
    team2_score = models.IntegerField("Счёт команды 2", default=0)
    winner = models.ForeignKey("Team", verbose_name="Победитель", on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"
    
    def __str__(self) -> str:
        return f"{self.team1} vs {self.team2}"
    
    def save(self, *args, **kwargs):
        # Автоматически определяем победителя на основе счета
        if self.team1_score > self.team2_score:
            self.winner = self.team1
        elif self.team2_score > self.team1_score:
            self.winner = self.team2
        else:
            self.winner = None  # ничья
        super().save(*args, **kwargs)


# Сигнал для автоматического создания пользователя при создании игрока
@receiver(post_save, sender=Player)
def create_user_for_player(sender, instance, created, **kwargs):
    if created and not instance.user:
        # Формируем username из имени и никнейма
        username = f"{instance.name}_{instance.nickname}".replace(' ', '_')
        
        # Пароль = имя игрока
        password = instance.name
        
        try:
            # Создаем пользователя с паролем = имя игрока
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=password,  # Пароль = имя игрока
                first_name=instance.name
            )
            
            # Сохраняем связь
            instance.user = user
            instance.save()
            
            print(f"Создан пользователь для игрока {instance.name}:")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Email: {username}@example.com")
            
        except Exception as e:
            print(f"Ошибка при создании пользователя для игрока: {e}")

# Сигнал для обновления пользователя при изменении игрока
@receiver(post_save, sender=Player)
def update_user_for_player(sender, instance, created, **kwargs):
    if not created and instance.user:
        try:
            # Обновляем данные пользователя
            instance.user.first_name = instance.name
            
            # Обновляем username
            new_username = f"{instance.name}_{instance.nickname}".replace(' ', '_')
            
            if instance.user.username != new_username:
                instance.user.username = new_username
            
            # Обновляем пароль на имя игрока
            instance.user.set_password(instance.name)
            
            instance.user.email = f"{new_username}@example.com"
            instance.user.save()
            
            print(f"Обновлен пользователь для игрока {instance.name}:")
            print(f"New password: {instance.name}")
            
        except Exception as e:
            print(f"Ошибка при обновлении пользователя для игрока: {e}")

# Сигнал для удаления пользователя при удалении игрока
@receiver(post_delete, sender=Player)
def delete_user_for_player(sender, instance, **kwargs):
    try:
        if instance.user:
            instance.user.delete()
            print(f"Пользователь {instance.user.username} удален")
    except Exception as e:
        print(f"Ошибка при удалении пользователя для игрока: {e}")