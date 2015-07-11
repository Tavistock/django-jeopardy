# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jeopardy_models.models import Season, Episode, GameRound, Category, Question
from datetime import datetime
from django.utils.timezone import make_aware
from django.db import transaction

class ScrapyJeopardyPipeline(object):
    def process_item(self, item, spider):
        if item['type'] == 'season':
            process_season(item)
        #elif item['type'] == 'episode':
        #    process_episode(item)
        #elif item['type'] == 'rounds':
        #    process_rounds(item)
        return item

def process_season(item):
    start = get_date(item['start'])
    end = get_date(item['end'])
    title = item['title']
    with transaction.atomic():
        season = Season(start=start, end=end, title=title)
        season.save()

def get_date(stamp):
    stamp_time = None
    try:
         stamp_time = datetime.strptime(stamp, '%Y-%m-%d')
    except Exception as e:
         stamp_time = datetime.strptime(stamp, '%Y')
    return make_aware(stamp_time)
