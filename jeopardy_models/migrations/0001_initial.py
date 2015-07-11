# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('game_id', models.IntegerField()),
                ('title', models.CharField(max_length=500)),
                ('subtitle', models.CharField(max_length=500)),
                ('date_aired', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='GameRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('round_number', models.IntegerField()),
                ('round_type', models.CharField(max_length=500)),
                ('episode', models.ForeignKey(to='jeopardy_models.Episode')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('daily_double', models.BooleanField()),
                ('value', models.IntegerField()),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.CharField(max_length=1000)),
                ('catagory', models.ForeignKey(to='jeopardy_models.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='season',
            field=models.ForeignKey(to='jeopardy_models.Season'),
        ),
        migrations.AddField(
            model_name='category',
            name='game_round',
            field=models.ForeignKey(to='jeopardy_models.GameRound'),
        ),
    ]
