from django.db import models

class Season(models.Model):
    title = models.CharField(max_lenth=500)
    start = models.DateField()
    end = models.DateField()

class Episode(models.Model):
    name = models.CharField(max_length=500)
    game_id = models.IntegerField()
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500)
    date_aired = models.DateField()
    season = models.ForeignKey(Season)

class GameRound(models.Model):
    round_number = models.IntegerField()
    round_type = models.CharField(max_length=500)
    episode = models.ForeignKey(Episode)

class Category(models.Model):
    name = models.CharField(max_length=500)
    game_round = models.ForeignKey(GameRound)

class Question(models.Model):
    daily_double = models.BooleanField()
    value = models.IntegerField()
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    catagory = models.ForeignKey(Category)
