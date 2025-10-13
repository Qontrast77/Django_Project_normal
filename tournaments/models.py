from django.db import models

class Team(models.Model):
    name = models.TextField("Название команды")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"
    
    def __str__(self) -> str:
        return self.name

class Player(models.Model):
    name = models.TextField("Имя игрока")
    nickname = models.TextField("Никнейм")
    team = models.ForeignKey("Team", verbose_name="Команда", on_delete=models.CASCADE, null=True)
    
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